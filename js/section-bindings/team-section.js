(function ($) {
    function safeImgSrc(s) {
        if (typeof s !== 'string') return '';
        var t = s.trim();
        return /^img\/team\/[a-zA-Z0-9_.-]+$/.test(t) ? t : '';
    }

    function safeHref(h) {
        if (typeof h !== 'string' || !h.trim()) return '#';
        var t = h.trim();
        if (/^javascript:/i.test(t)) return '#';
        return t;
    }

    function applySetBg($root) {
        $root.find('.set-bg').each(function () {
            var bg = $(this).data('setbg');
            if (bg) $(this).css('background-image', 'url(' + bg + ')');
        });
    }

    function initTeamOwl($slider) {
        $slider.owlCarousel({
            loop: true,
            margin: 0,
            items: 3,
            dots: true,
            dotsEach: 2,
            smartSpeed: 1200,
            autoHeight: false,
            autoplay: true,
            responsive: {
                320: { items: 1 },
                768: { items: 2 },
                992: { items: 3 }
            }
        });
    }

    function renderTeam(data) {
        var subtitleEl = document.getElementById('team-subtitle');
        var titleEl = document.getElementById('team-title');
        var appointmentEl = document.getElementById('team-appointment-btn');
        var $slider = $('.ts-slider');
        if (!subtitleEl || !titleEl || !appointmentEl || !$slider.length || !data) return;

        subtitleEl.textContent = data.subtitle || '';
        titleEl.textContent = data.title || '';
        appointmentEl.href = safeHref(data.appointmentLink);
        appointmentEl.textContent = data.appointmentLabel || 'appointment';

        if ($slider.data('owl.carousel')) {
            $slider.owlCarousel('destroy');
        }
        $slider.empty();

        var members = data.members || [];
        members.forEach(function (m) {
            var src = safeImgSrc(m.image);
            var col = $('<div class="col-lg-4"></div>');
            var item = $('<div class="ts-item set-bg"></div>');
            item.attr('data-setbg', src);
            var tsText = $('<div class="ts_text"></div>');
            tsText.append($('<h4></h4>').text(typeof m.name === 'string' ? m.name : ''));
            tsText.append($('<span></span>').text(typeof m.role === 'string' ? m.role : ''));
            item.append(tsText);
            col.append(item);
            $slider.append(col);
        });

        applySetBg($slider);
        if (members.length) {
            initTeamOwl($slider);
        }
    }

    fetch('database/team-section.json')
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(renderTeam)
        .catch(function (err) {
            console.error('team-section:', err);
        });
})(jQuery);
