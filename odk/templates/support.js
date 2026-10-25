/**
 * OpenDesignKit — minimal preview runtime for .dc.html boards
 * ---------------------------------------------------------------
 * Independent, dependency-free implementation of the public .dc.html
 * file-format subset, so boards can be previewed (and their declared
 * interactions exercised) directly in any modern browser without a
 * proprietary editor.
 *
 * Supported: {{ hole }} interpolation (dot paths + true/false/null and
 * numeric literals), sc-for / sc-if, onClick/onInput/onChange="{{ fn }}"
 * bindings, DCLogic base class (props / state / setState / forceUpdate /
 * renderVals), <helmet> hoisting, $preview metadata, dc-import child
 * boards (requires http:// serving; degrades to a hint on file://).
 * Board-to-board <a href="X.dc.html"> links use native navigation and
 * work as-is.
 * Not supported: editor WYSIWYG tooling.
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
      var p = path.trim();
      if (p === 'true') return true;
      if (p === 'false') return false;
      if (p === 'null') return null;
      if (/^-?\d+(\.\d+)?$/.test(p)) return parseFloat(p);
      var segs = p.split('.'), cur = scope, i;
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

    function unwrapChildren(el, scope, depth) {
      var holder = document.createElement('div');
      holder.innerHTML = el.innerHTML;
      processContainer(holder, scope, depth);
      var frag = document.createDocumentFragment();
      while (holder.firstChild) frag.appendChild(holder.firstChild);
      el.parentNode.replaceChild(frag, el);
    }

    // ---- dc-import: mount sibling <Name>.dc.html as child component ----
    function kebabToCamel(s) {
      return s.replace(/-([a-z])/g, function (_, c) { return c.toUpperCase(); });
    }

    function mountChild(slot, srcEl, cname, scope, depth) {
      var props = {};
      Array.prototype.slice.call(srcEl.attributes).forEach(function (a) {
        if (a.name === 'name' || a.name === 'hint-size' || a.name === 'class' || a.name === 'style') return;
        var key = kebabToCamel(a.name);
        var whole = a.value.match(/^\{\{\s*([^}]+?)\s*\}\}$/);
        props[key] = whole ? lookup(whole[1], scope) : interp(a.value, scope);
      });
      fetch(cname + '.dc.html').then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      }).then(function (text) {
        var doc = new DOMParser().parseFromString(text, 'text/html');
        var croot = doc.querySelector('x-dc');
        var cscript = doc.querySelector('script[type="text/x-dc"][data-dc-script]');
        if (!croot || !cscript) throw new Error('bad child board');
        var ch = croot.querySelector('helmet');
        if (ch) {
          Array.prototype.slice.call(ch.childNodes).forEach(function (nn) { document.head.appendChild(nn); });
          ch.parentNode.removeChild(ch);
        }
        var declared = {};
        try { declared = JSON.parse(cscript.getAttribute('data-props') || '{}'); } catch (e) {}
        var merged = {};
        Object.keys(declared).forEach(function (k) {
          var d = declared[k];
          if (d && Object.prototype.hasOwnProperty.call(d, 'default')) merged[k] = d.default;
        });
        Object.keys(props).forEach(function (k) { merged[k] = props[k]; });
        var C = new Function('DCLogic', cscript.textContent + '\n;return typeof Component === "function" ? Component : null;')(window.DCLogic);
        if (!C) throw new Error('no Component class');
        var inst = new C(merged);
        var vals = inst.renderVals ? (inst.renderVals() || {}) : {};
        var childScope = Object.assign({}, merged, inst.state, vals);
        slot.innerHTML = croot.innerHTML;
        processContainer(slot, childScope, depth + 1);
      }).catch(function () {
        slot.style.cssText += ';border:1px dashed #98a2b3;display:flex;align-items:center;justify-content:center;color:#98a2b3;font:13px system-ui,sans-serif;padding:12px;min-height:60px;';
        slot.setAttribute('title', 'dc-import 需通过 http:// 服务预览（如 python3 -m http.server）');
        slot.textContent = '[dc-import "' + cname + '" 未加载]';
      });
    }

    // ---- recursive renderer ----
    function processContainer(container, scope, depth) {
      depth = depth || 0;
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
            processContainer(holder, childScope, depth);
            while (holder.firstChild) frag.appendChild(holder.firstChild);
          });
          n.parentNode.replaceChild(frag, n);
          return;
        }

        if (tag === 'SC-IF') {
          var condPath = (n.getAttribute('value') || '').replace(/^\{\{/, '').replace(/\}\}$/, '').trim();
          var truthy = lookup(condPath, scope);
          if (truthy) unwrapChildren(n, scope, depth); else n.parentNode.removeChild(n);
          return;
        }

        if (tag === 'DC-IMPORT') {
          var cname = n.getAttribute('name');
          if (!cname || depth > 8) { n.parentNode.removeChild(n); return; }
          var slot = document.createElement('div');
          var hint = n.getAttribute('hint-size');
          if (hint) {
            var parts = hint.split(',');
            if (parts[0]) slot.style.width = parts[0].trim();
            if (parts[1]) slot.style.height = parts[1].trim();
          }
          slot.style.boxSizing = 'border-box';
          n.parentNode.replaceChild(slot, n);
          mountChild(slot, n, cname, scope, depth);
          return;
        }

        applyAttrs(n, scope);
        processContainer(n, scope, depth);
      });
    }

    // ---- render cycle ----
    function render() {
      var vals = instance.renderVals ? (instance.renderVals() || {}) : {};
      var scope = Object.assign({}, instance.props, instance.state, vals);
      root.innerHTML = templateHTML;
      processContainer(root, scope, 0);
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
