(function () {
    'use strict';
    if (window.__AXIS_WHATSAPP_CONTACT__) return;
    window.__AXIS_WHATSAPP_CONTACT__ = true;

    var WA_URL =
        'https://wa.me/971547007900?text=' +
        encodeURIComponent('Hi AXIS! I would like to get in touch.');

    function iconUrl() {
        var script = document.currentScript;
        if (script && script.src) {
            return script.src.replace(
                /components\/axis-whatsapp-contact\.js(\?.*)?$/i,
                'public/svgs/whatsapp-icons.svg'
            );
        }
        var branding = document.getElementById('axis-branding-css');
        if (branding && branding.href) {
            return branding.href.replace(
                /components\/axis-branding\.css(\?.*)?$/i,
                'public/svgs/whatsapp-icons.svg'
            );
        }
        return 'public/svgs/whatsapp-icons.svg';
    }

    function init() {
        var root =
            document.getElementById('chatbot-setup') ||
            document.querySelector('.chat-bot-main');
        if (!root || root.getAttribute('data-axis-whatsapp') === '1') return;
        root.setAttribute('data-axis-whatsapp', '1');

        var link = document.createElement('a');
        link.className = 'axis-whatsapp-float gnwhatsapp-btn';
        link.href = WA_URL;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.title = 'WhatsApp +971 54 700 7900';
        link.setAttribute('aria-label', 'Contact AXIS on WhatsApp +971 54 700 7900');

        var img = document.createElement('img');
        img.src = iconUrl();
        img.alt = '';
        img.width = 72;
        img.height = 72;
        img.loading = 'lazy';
        img.decoding = 'async';

        link.appendChild(img);

        root.parentNode.replaceChild(link, root);
    }

    function loadMobileMenuFix() {
        if (window.__AXIS_MOBILE_MENU__ || window.__AXIS_MOBILE_MENU_LOADING__) return;
        window.__AXIS_MOBILE_MENU_LOADING__ = true;
        var script = document.currentScript || document.getElementById('axis-whatsapp-contact-js');
        var base = 'components/';
        if (script && script.src) {
            base = script.src.replace(/axis-whatsapp-contact\.js(\?.*)?$/i, '');
        } else {
            var branding = document.getElementById('axis-branding-css');
            if (branding && branding.href) {
                base = branding.href.replace(/axis-branding\.css(\?.*)?$/i, '');
            }
        }
        var tag = document.createElement('script');
        tag.src = base + 'axis-mobile-menu.js';
        tag.defer = true;
        document.head.appendChild(tag);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    loadMobileMenuFix();
})();
