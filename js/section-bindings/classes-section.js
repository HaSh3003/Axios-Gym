(function () {
    var colClassPattern = /^[\w\s-]+$/;

    function safeColClass(c) {
        if (typeof c !== 'string') return 'col-lg-4 col-md-6';
        var t = c.trim();
        return colClassPattern.test(t) ? t : 'col-lg-4 col-md-6';
    }

    function safeImgSrc(s) {
        if (typeof s !== 'string') return '';
        var t = s.trim();
        return /^img\/[a-zA-Z0-9_./-]+$/.test(t) ? t : '';
    }

    function safeTitleTag(t) {
        return t === 'h4' ? 'h4' : 'h5';
    }

    function safeHref(h) {
        if (typeof h !== 'string' || !h.trim()) return '#';
        var t = h.trim();
        if (/^javascript:/i.test(t)) return '#';
        return t;
    }

    function renderClasses(data) {
        var subtitleEl = document.getElementById('classes-subtitle');
        var titleEl = document.getElementById('classes-title');
        var row = document.getElementById('classes-items-row');
        if (!subtitleEl || !titleEl || !row || !data) return;

        subtitleEl.textContent = data.subtitle || '';
        titleEl.textContent = data.title || '';
        row.replaceChildren();

        (data.items || []).forEach(function (item) {
            var col = document.createElement('div');
            col.className = safeColClass(item.colClass);

            var classItem = document.createElement('div');
            classItem.className = 'class-item';

            var pic = document.createElement('div');
            pic.className = 'ci-pic';
            var img = document.createElement('img');
            img.src = safeImgSrc(item.image);
            img.alt = typeof item.imageAlt === 'string' ? item.imageAlt : '';
            pic.appendChild(img);

            var ciText = document.createElement('div');
            ciText.className = 'ci-text';
            var span = document.createElement('span');
            span.textContent = item.category || '';
            var nameEl = document.createElement(safeTitleTag(item.titleTag));
            nameEl.textContent = item.name || '';
            var a = document.createElement('a');
            a.href = safeHref(item.link);
            var icon = document.createElement('i');
            icon.className = 'fa fa-angle-right';
            a.appendChild(icon);

            ciText.appendChild(span);
            ciText.appendChild(nameEl);
            ciText.appendChild(a);
            classItem.appendChild(pic);
            classItem.appendChild(ciText);
            col.appendChild(classItem);
            row.appendChild(col);
        });
    }

    fetch('database/classes-section.json')
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(renderClasses)
        .catch(function (err) {
            console.error('classes-section:', err);
        });
})();
