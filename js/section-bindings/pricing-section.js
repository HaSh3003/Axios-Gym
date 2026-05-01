(function () {
    var colClassPattern = /^[\w\s-]+$/;

    function safeColClass(c) {
        if (typeof c !== 'string') return 'col-lg-4 col-md-8';
        var t = c.trim();
        return colClassPattern.test(t) ? t : 'col-lg-4 col-md-8';
    }

    function safeHref(h) {
        if (typeof h !== 'string' || !h.trim()) return '#';
        var t = h.trim();
        if (/^javascript:/i.test(t)) return '#';
        return t;
    }

    function renderPricing(data) {
        var subtitleEl = document.getElementById('pricing-subtitle');
        var titleEl = document.getElementById('pricing-title');
        var row = document.getElementById('pricing-plans-row');
        if (!subtitleEl || !titleEl || !row || !data) return;

        subtitleEl.textContent = data.subtitle || '';
        titleEl.textContent = data.title || '';
        row.replaceChildren();

        (data.plans || []).forEach(function (plan) {
            var col = document.createElement('div');
            col.className = safeColClass(plan.colClass);

            var psItem = document.createElement('div');
            psItem.className = 'ps-item';

            var h3 = document.createElement('h3');
            h3.textContent = plan.name || '';

            var piPrice = document.createElement('div');
            piPrice.className = 'pi-price';
            var priceH2 = document.createElement('h2');
            priceH2.textContent = plan.price || '';
            var captionSpan = document.createElement('span');
            captionSpan.textContent = plan.priceCaption || '';
            piPrice.appendChild(priceH2);
            piPrice.appendChild(captionSpan);

            var ul = document.createElement('ul');
            (plan.features || []).forEach(function (line) {
                var li = document.createElement('li');
                li.textContent = typeof line === 'string' ? line : '';
                ul.appendChild(li);
            });

            var enroll = document.createElement('a');
            enroll.href = safeHref(plan.enrollLink);
            enroll.className = 'primary-btn pricing-btn';
            enroll.textContent = plan.enrollLabel || 'Enroll now';

            psItem.appendChild(h3);
            psItem.appendChild(piPrice);
            psItem.appendChild(ul);
            psItem.appendChild(enroll);

            if (plan.thumbIcon !== false) {
                var thumb = document.createElement('a');
                thumb.href = safeHref(plan.thumbLink);
                thumb.className = 'thumb-icon';
                var icon = document.createElement('i');
                icon.className = 'fa fa-picture-o';
                thumb.appendChild(icon);
                psItem.appendChild(thumb);
            }

            col.appendChild(psItem);
            row.appendChild(col);
        });
    }

    fetch('database/pricing-section.json')
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(renderPricing)
        .catch(function (err) {
            console.error('pricing-section:', err);
        });
})();
