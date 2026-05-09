(function () {
    'use strict';
    if (window.__AXIS_SITE_LAYOUT_LOADED__) return;
    window.__AXIS_SITE_LAYOUT_LOADED__ = true;

    var script = document.currentScript;
    if (!script || !script.src) {
        console.error('[axis-layout] Load site-layout.js with a script src');
        return;
    }

    var componentsBase = script.src.replace(/\/site-layout\.js(\?.*)?$/i, '/');
    var siteRootUrl = new URL('..', componentsBase).href;

    if (!document.getElementById('axis-branding-css')) {
        var branding = document.createElement('link');
        branding.id = 'axis-branding-css';
        branding.rel = 'stylesheet';
        branding.href = componentsBase + 'axis-branding.css';
        document.head.appendChild(branding);
    }

    function resolveUrl(raw) {
        if (raw == null || raw === '') return raw;
        var s = String(raw).trim();
        if (/^(https?:|mailto:|tel:|javascript:|\/\/)/i.test(s)) return s;
        if (s.startsWith('data:') || s.startsWith('blob:')) return s;
        if (s.startsWith('#') && s.indexOf('/') === -1) return s;
        if (s.charAt(0) === '/' && s.charAt(1) !== '/') return s;
        try {
            return new URL(s, siteRootUrl).href;
        } catch (e) {
            return raw;
        }
    }

    function resolveSrcset(val) {
        if (!val) return val;
        return val.split(',').map(function (part) {
            var p = part.trim();
            if (!p) return p;
            var sp = p.indexOf(' ');
            var urlPart = sp === -1 ? p : p.slice(0, sp);
            var rest = sp === -1 ? '' : p.slice(sp);
            var u = urlPart.trim();
            if (!u || /^https?:/i.test(u) || (u.charAt(0) === '/' && u.charAt(1) !== '/')) {
                return part;
            }
            return resolveUrl(u) + rest;
        }).join(', ');
    }

    function rewriteHandlerAttrs(html) {
        return html
            .replace(/desktopsearch\(\s*['"]([^'"]+)['"]\s*\)/g, function (_, p) {
                return "desktopsearch('" + resolveUrl(p).replace(/'/g, "\\'") + "')";
            })
            .replace(/mobilesearch\(\s*['"]([^'"]+)['"]\s*\)/g, function (_, p) {
                return "mobilesearch('" + resolveUrl(p).replace(/'/g, "\\'") + "')";
            });
    }

    function resolveElement(el) {
        if (!el || el.nodeType !== 1) return;
        ['href', 'src', 'poster'].forEach(function (a) {
            if (el.hasAttribute(a)) el.setAttribute(a, resolveUrl(el.getAttribute(a)));
        });
        if (el.hasAttribute('srcset')) {
            el.setAttribute('srcset', resolveSrcset(el.getAttribute('srcset')));
        }
        for (var c = el.firstElementChild; c; c = c.nextElementSibling) {
            resolveElement(c);
        }
    }

    function injectMount(mountId, htmlString) {
        var mount = document.getElementById(mountId);
        if (!mount) return;
        htmlString = rewriteHandlerAttrs(htmlString);
        var wrap = document.createElement('div');
        wrap.innerHTML = htmlString.trim();
        var newEl = wrap.firstElementChild;
        if (!newEl) return;
        resolveElement(newEl);
        mount.parentNode.replaceChild(newEl, mount);
    }

    function loadTextSync(url) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', url, false);
            xhr.send(null);
            if ((xhr.status >= 200 && xhr.status < 300) || xhr.status === 0) {
                return xhr.responseText;
            }
        } catch (e) {}
        return null;
    }

    function fetchText(url) {
        return fetch(url, { credentials: 'same-origin' }).then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status + ' ' + url);
            return r.text();
        });
    }

    var needHeader = !!document.getElementById('axis-site-header');
    var needFooter = !!document.getElementById('axis-site-footer');
    if (!needHeader && !needFooter) return;

    function trySyncInject() {
        var allOk = true;
        if (needHeader) {
            var ht = loadTextSync(componentsBase + 'site-header.html');
            if (ht) injectMount('axis-site-header', ht);
            else allOk = false;
        }
        if (needFooter) {
            var ft = loadTextSync(componentsBase + 'site-footer.html');
            if (ft) injectMount('axis-site-footer', ft);
            else allOk = false;
        }
        return allOk;
    }

    if (!trySyncInject()) {
        Promise.all([
            needHeader ? fetchText(componentsBase + 'site-header.html') : Promise.resolve(null),
            needFooter ? fetchText(componentsBase + 'site-footer.html') : Promise.resolve(null)
        ])
            .then(function (parts) {
                if (parts[0]) injectMount('axis-site-header', parts[0]);
                if (parts[1]) injectMount('axis-site-footer', parts[1]);
            })
            .catch(function (err) {
                console.error('[axis-layout] Failed to load layout fragments', err);
            });
    }
})();
