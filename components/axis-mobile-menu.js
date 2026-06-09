/**
 * Mobile header menu — works without the Vite client bundle (missing jquery chunk).
 */
(function () {
    'use strict';
    if (window.__AXIS_MOBILE_MENU__) return;
    window.__AXIS_MOBILE_MENU__ = true;

    function qs(sel, root) {
        return (root || document).querySelector(sel);
    }

    function qsa(sel, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    }

    function closeSubmenus(menu) {
        qsa('.menu-item.active', menu).forEach(function (el) {
            el.classList.remove('active');
        });
        qsa('.submenu-wrapper', menu).forEach(function (el) {
            el.style.display = 'none';
        });
        var err = document.getElementById('emptysearchvalmsgm');
        if (err) err.style.display = 'none';
    }

    function setMenuOpen(open) {
        var trigger = qs('header .menu-trigger');
        var menu = qs('header .menu.mobile-view');
        if (!trigger || !menu) return;

        document.body.classList.toggle('mobile-menu-open', open);
        trigger.classList.toggle('active', open);
        menu.style.display = open ? 'block' : 'none';
        if (!open) closeSubmenus(menu);
    }

    function toggleMenu() {
        setMenuOpen(!document.body.classList.contains('mobile-menu-open'));
    }

    function flattenMobileLocationsLink(menu) {
        qsa('.hs-menu-wrapper > ul > .menu-item.has-submenu', menu).forEach(function (item) {
            var link = item.querySelector(':scope > a.menu-item--link[title="Locations"]');
            if (!link) return;

            item.classList.remove('has-submenu', 'active');

            var trigger = item.querySelector(':scope > .child-trigger');
            var submenu = item.querySelector(':scope > .submenu-wrapper');
            if (trigger) trigger.remove();
            if (submenu) submenu.remove();
        });
    }

    function onChildTriggerClick(e) {
        e.preventDefault();
        e.stopPropagation();
        var trigger = e.currentTarget;
        var item = trigger.parentElement;
        var submenu = trigger.nextElementSibling;
        if (!item || !submenu || !submenu.classList.contains('submenu-wrapper')) return;

        var menu = qs('header .menu.mobile-view');
        qsa('.menu-item', menu).forEach(function (sibling) {
            if (sibling !== item) {
                sibling.classList.remove('active');
                var sub = sibling.querySelector(':scope > .submenu-wrapper');
                if (sub) sub.style.display = 'none';
            }
        });

        var willOpen = submenu.style.display !== 'block';
        item.classList.toggle('active', willOpen);
        submenu.style.display = willOpen ? 'block' : 'none';
    }

    function init() {
        var bound = false;

        function bindOnce() {
            if (bound) return true;

            var trigger = qs('header .menu-trigger');
            var menu = qs('header .menu.mobile-view');
            if (!trigger || !menu) return false;

            bound = true;

            if (menu.style.display !== 'block') menu.style.display = 'none';

            flattenMobileLocationsLink(menu);

            trigger.addEventListener('click', function (e) {
                e.preventDefault();
                toggleMenu();
            });

            // Bind submenu toggles inside the mobile menu only.
            qsa('.child-trigger', menu).forEach(function (el) {
                el.addEventListener('click', onChildTriggerClick);
            });

            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && document.body.classList.contains('mobile-menu-open')) {
                    setMenuOpen(false);
                }
            });

            return true;
        }

        // Some pages inject the header asynchronously after DOMContentLoaded.
        // Retry binding for a short window so the hamburger works on all pages.
        if (bindOnce()) return;

        var attempts = 0;
        var maxAttempts = 30; // ~4.5s at 150ms intervals
        var interval = setInterval(function () {
            attempts += 1;
            if (bindOnce() || attempts >= maxAttempts) {
                clearInterval(interval);
            }
        }, 150);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
