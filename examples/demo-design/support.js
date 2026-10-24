/**
 * OpenClaudeDesign — minimal preview runtime for .dc.html boards
 * ---------------------------------------------------------------
 * Independent, dependency-free implementation of the public .dc.html
 * file-format subset, so boards can be previewed (and their declared
 * interactions exercised) directly in any modern browser without a
 * proprietary editor.
 *
 * Supported: {{ hole }} interpolation (dot paths), sc-for / sc-if,
 * onClick/onInput/onChange="{{ fn }}" bindings, DCLogic base class
 * (props / state / setState / forceUpdate / renderVals), <helmet>
 * hoisting, $preview metadata.
 * Not supported: dc-import (child DC), editor WYSIWYG tooling.
 */
(function () {
  'use strict';

  function boot() {
    var scriptTag = document.querySelector('script[type="text/x-dc"][data-dc-script]');
    var root = document.querySelector('x-dc');
    if (!scriptTag || !root) { console.warn('[dc-preview] missing x-dc or dc-script'); return; }

    // ---- DCLogic base class ----
    function DCLogic(props) { this.props = props || {}; this.state = {}; }
    DCLogic.prototype.setState = function (patch) {
      for (var k in patch) this.state[k] = patch[k];
      scheduleRender();
    };
    DCLogic.prototype.forceUpdate = function () { scheduleRender(); };
    window.DCLogic = DCLogic;

    // ---- declared props / $preview ----
    var declaredProps = {};
    try { declaredProps = JSON.parse(scriptTag.getAttribute('data-props') || '{}'); }
    catch (e) { console.warn('[dc-preview] bad data-props JSON', e); }
    var previewMeta = declaredProps.$preview || {};
    if (previewMeta.width) {
      document.documentElement.setAttribute('data-dc-preview-size', previewMeta.width + 'x' + (previewMeta.height || ''));
    }

    // ---- component factory ----
    var ComponentClass = null;
    try {
      var factory = new Function(
        'DCLogic',
        scriptTag.textContent + '\n;return typeof Component === "function" ? Component : null;'
      );
      ComponentClass = factory(window.DCLogic);
    } catch (e) { console.error('[dc-preview] script eval failed', e); }
    if (!ComponentClass) { console.warn('[dc-preview] no `class Component extends DCLogic` found'); return; }

    function defaults() {
      var p = {};
      Object.keys(declaredProps).forEach(function (k) {
        var d = declaredProps[k];
        if (d && Object.prototype.hasOwnProperty.call(d, 'default')) p[k] = d.default;
      });
      return p;
    }
    var instance = new ComponentClass(defaults());

    // ---- hoist <helmet> once, capture template ----
    var helmet = root.querySelector('helmet');
    if (helmet) {
      Array.prototype.slice.call(helmet.childNodes).forEach(function (n) { document.head.appendChild(n); });
      helmet.parentNode.removeChild(helmet);
    }
    var templateHTML = root.innerHTML;

    // ---- hole helpers ----
    var HOLE = /\{\{\s*([^}]+?)\s*\}\}/g;
    function lookup(path, scope) {
      var segs = path.trim().split('.'), cur = scope, i;
      for (i = 0; i < segs.length; i++) {
        if (cur === null || cur === undefined) return null;
        if (!Object.prototype.hasOwnProperty.call(cur, segs[i])) return null;
        cur = cur[segs[i]];
      }
      return cur === undefined ? null : cur;
    }
    function interp(text, scope) {
      return text.replace(HOLE, function (_, path) {
        var v = lookup(path, scope);
        return (v === null || v === undefined) ? '' : String(v);
      });
    }

    var EVENTS = { onclick: 'click', oninput: 'input', onchange: 'change' };

    function applyAttrs(el, scope) {
      Array.prototype.slice.call(el.attributes).forEach(function (a) {
        if (HOLE.test(a.value)) {
          HOLE.lastIndex = 0;
          var whole = a.value.match(/^\{\{\s*([^}]+?)\s*\}\}$/);
          var val;
          if (whole) {
            var name = a.name.toLowerCase();
            val = lookup(whole[1], scope);
            if (EVENTS[name]) {
              el.removeAttribute(a.name);
              if (typeof val === 'function') {
                el.addEventListener(EVENTS[name], function (ev) { ev.preventDefault(); val(ev); });
              }
            } else if (val !== null && val !== undefined && typeof val !== 'object' && typeof val !== 'function') {
              el.setAttribute(a.name, String(val));
            } else {
              el.removeAttribute(a.name);
            }
          } else {
            el.setAttribute(a.name, interp(a.value, scope));
          }
        }
        HOLE.lastIndex = 0;
      });
    }

    function unwrapChildren(el, scope) {
      var holder = document.createElement('div');
      holder.innerHTML = el.innerHTML;
      processContainer(holder, scope);
      var frag = document.createDocumentFragment();
      while (holder.firstChild) frag.appendChild(holder.firstChild);
      el.parentNode.replaceChild(frag, el);
    }

    // ---- recursive renderer ----
    function processContainer(container, scope) {
      Array.prototype.slice.call(container.childNodes).forEach(function (n) {
        if (n.nodeType === 3) { // text
          if (HOLE.test(n.textContent)) { HOLE.lastIndex = 0; n.textContent = interp(n.textContent, scope); }
          HOLE.lastIndex = 0;
          return;
        }
        if (n.nodeType !== 1) return;

        var tag = n.tagName;

        // control-flow elements FIRST: their list/value attributes are
        // expressions to evaluate, not render attrs (applyAttrs would strip them)
        if (tag === 'SC-FOR') {
          var listPath = (n.getAttribute('list') || '').replace(/^\{\{/, '').replace(/\}\}$/, '').trim();
          var asName = n.getAttribute('as') || 'item';
          var list = lookup(listPath, scope) || [];
          var tpl = n.innerHTML;
          var frag = document.createDocumentFragment();
          Array.prototype.forEach.call(list, function (item, idx) {
            var holder = document.createElement('div');
            holder.innerHTML = tpl;
            var childScope = Object.assign({}, scope, { $index: idx });
            childScope[asName] = item;
            processContainer(holder, childScope);
            while (holder.firstChild) frag.appendChild(holder.firstChild);
          });
          n.parentNode.replaceChild(frag, n);
          return;
        }

        if (tag === 'SC-IF') {
          var condPath = (n.getAttribute('value') || '').replace(/^\{\{/, '').replace(/\}\}$/, '').trim();
          var truthy = lookup(condPath, scope);
          if (truthy) unwrapChildren(n, scope); else n.parentNode.removeChild(n);
          return;
        }

        applyAttrs(n, scope);
        processContainer(n, scope);
      });
    }

    // ---- render cycle ----
    function render() {
      var vals = instance.renderVals ? (instance.renderVals() || {}) : {};
      var scope = Object.assign({}, instance.props, instance.state, vals);
      root.innerHTML = templateHTML;
      processContainer(root, scope);
    }

    var scheduled = false;
    function scheduleRender() {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(function () { scheduled = false; render(); });
    }

    try { render(); } catch (e) { console.error('[dc-preview] render failed', e); }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
