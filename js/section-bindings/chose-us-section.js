(function () {
    var iconClassPattern = /^flaticon-[\w-]+$/;

    function safeIconClass(c) {
        return typeof c === 'string' && iconClassPattern.test(c) ? c : '';
    }

    function renderChoseus(data) {
        var subtitleEl = document.getElementById('choseus-subtitle');
        var titleEl = document.getElementById('choseus-title');
        var row = document.getElementById('choseus-items-row');
        if (!subtitleEl || !titleEl || !row || !data) return;

        subtitleEl.textContent = data.subtitle || '';
        titleEl.textContent = data.title || '';
        row.replaceChildren();

        (data.items || []).forEach(function (item) {
            var col = document.createElement('div');
            col.className = 'col-lg-3 col-sm-6';
            var csItem = document.createElement('div');
            csItem.className = 'cs-item';
            var span = document.createElement('span');
            span.className = safeIconClass(item.iconClass);
            var h4 = document.createElement('h4');
            h4.textContent = item.title || '';
            var p = document.createElement('p');
            p.textContent = item.description || '';
            csItem.appendChild(span);
            csItem.appendChild(h4);
            csItem.appendChild(p);
            col.appendChild(csItem);
            row.appendChild(col);
        });
    }

    fetch('database/chose-us-section.json')
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(renderChoseus)
        .catch(function (err) {
            console.error('chose-us-section:', err);
        });
})();
