(function () {
    var TRAINEE_API = 'https://axissportclub.com/wp-json/axis/v1/trainee';
    var MEMBERSHIP_API = 'https://axissportclub.com/wp-json/wp/v2/membership?per_page=100';
    var MEMBERSHIP_API_FALLBACK = 'https://axissportclub.com/wp-json/axis/v1/memberships';
    var toastTimer = null;
    var toastEl = null;
    var toastTextEl = null;

    function sanitizePhone(value) {
        return String(value || '').replace(/\D/g, '');
    }

    function pickField(item, field) {
        if (!item) return '';
        if (item[field] != null && item[field] !== '') return item[field];
        if (item.acf && item.acf[field] != null && item.acf[field] !== '') return item.acf[field];
        if (item.meta && item.meta[field] != null && item.meta[field] !== '') return item.meta[field];
        return '';
    }

    function inferCategory(item) {
        var duration = String(pickField(item, 'duration') || '').toLowerCase();
        var time = String(pickField(item, 'time') || '').toLowerCase();
        if (duration.indexOf('month') !== -1 || time.indexOf('program') !== -1) {
            return 'Program + Following Up';
        }
        if (duration.indexOf('session') !== -1 || time.indexOf('session') !== -1) {
            return 'Session Packages';
        }
        return 'Other Packages';
    }

    function normalizePlan(item) {
        var title = '';
        if (item.title && item.title.rendered) {
            title = String(item.title.rendered).replace(/<[^>]*>/g, '').trim();
        }
        return {
            id: item.id,
            category: inferCategory(item),
            time: String(pickField(item, 'time') || title).trim(),
            price: String(pickField(item, 'price') || '').trim(),
            duration: String(pickField(item, 'duration') || '').trim()
        };
    }

    function getPlanLabel(plan) {
        var duration = plan.duration ? ' /' + plan.duration : '';
        if (plan.time && plan.price) {
            return plan.time + ' — AED ' + plan.price + duration;
        }
        return plan.time || ('Package #' + plan.id);
    }

    function ensureToast() {
        if (toastEl) return;
        toastEl = document.createElement('div');
        toastEl.id = 'axis-lead-toast';
        toastEl.className = 'axis-lead-toast';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'polite');
        toastEl.hidden = true;
        toastEl.innerHTML = '<p class="axis-lead-toast-text"></p><button type="button" class="axis-lead-toast-close" aria-label="Close">&times;</button>';
        document.body.appendChild(toastEl);
        toastTextEl = toastEl.querySelector('.axis-lead-toast-text');
        toastEl.querySelector('.axis-lead-toast-close').addEventListener('click', hideToast);
    }

    function showToast(message, type) {
        ensureToast();
        clearTimeout(toastTimer);
        toastEl.hidden = false;
        toastEl.className = 'axis-lead-toast axis-lead-toast--' + (type || 'info') + ' is-visible';
        toastTextEl.textContent = message;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (type === 'success') {
            toastTimer = setTimeout(hideToast, 8000);
        } else if (type === 'error') {
            toastTimer = setTimeout(hideToast, 10000);
        }
    }

    function hideToast() {
        if (!toastEl) return;
        clearTimeout(toastTimer);
        toastEl.classList.remove('is-visible');
        setTimeout(function () {
            toastEl.hidden = true;
        }, 350);
    }

    function fetchPlans() {
        return fetch(MEMBERSHIP_API)
            .then(function (res) {
                if (!res.ok) throw new Error('fetch failed');
                return res.json();
            })
            .catch(function () {
                return fetch(MEMBERSHIP_API_FALLBACK).then(function (res) {
                    if (!res.ok) throw new Error('fetch failed');
                    return res.json();
                });
            });
    }

    function populatePackageSelect(select) {
        if (!select) return;
        select.innerHTML = '<option value="">SELECT PACKAGE</option>';
        select.disabled = true;

        fetchPlans()
            .then(function (items) {
                if (!Array.isArray(items) || !items.length) throw new Error('empty');
                var plans = items
                    .filter(function (item) { return item && item.id; })
                    .map(normalizePlan)
                    .filter(function (plan) { return plan.time || plan.price; });

                var groups = {};
                plans.forEach(function (plan) {
                    if (!groups[plan.category]) groups[plan.category] = [];
                    groups[plan.category].push(plan);
                });

                ['Session Packages', 'Program + Following Up', 'Other Packages'].forEach(function (category) {
                    var list = groups[category];
                    if (!list || !list.length) return;
                    list.sort(function (a, b) {
                        return (parseFloat(a.price) || 0) - (parseFloat(b.price) || 0);
                    });
                    var optgroup = document.createElement('optgroup');
                    optgroup.label = category;
                    list.forEach(function (plan) {
                        var opt = document.createElement('option');
                        opt.value = String(plan.id);
                        opt.textContent = getPlanLabel(plan);
                        optgroup.appendChild(opt);
                    });
                    select.appendChild(optgroup);
                });
                select.disabled = false;
            })
            .catch(function () {
                select.innerHTML = '<option value="">Unable to load packages</option>';
                select.disabled = true;
            });
    }

    function stripReferralContent(container) {
        if (!container) return;
        container.querySelectorAll('.thnk-social-share-main, .thnk-msg-social-share, .link-share-box').forEach(function (el) {
            el.remove();
        });
        container.querySelectorAll('p').forEach(function (p) {
            var text = (p.textContent || '').trim();
            if (/GIVE YOUR FRIENDS|COPY AND SEND|Share a FREE DAY PASS/i.test(text)) {
                p.remove();
            }
        });
    }

    function showThankYou(form, name) {
        var thankYou = document.getElementById('submitmsg');
        var nameEl = document.getElementById('submittedUserName');
        var fieldsWrap = form.querySelector('.form-fields-wrap');
        var submitWrap = form.querySelector('.hs-submit');
        var title = form.querySelector('.form-title');

        stripReferralContent(thankYou);
        if (nameEl) nameEl.textContent = name;
        if (fieldsWrap) fieldsWrap.style.display = 'none';
        if (submitWrap) submitWrap.style.display = 'none';
        if (title) title.style.display = 'none';
        if (thankYou) {
            thankYou.style.display = 'block';
            thankYou.classList.add('active');
        }
        form.reset();
    }

    function handleSubmit(e) {
        var form = e.target;
        if (!form || form.id !== 'workoutlead') return;

        e.preventDefault();
        e.stopPropagation();
        if (typeof e.stopImmediatePropagation === 'function') {
            e.stopImmediatePropagation();
        }

        var packageSelect = form.querySelector('#axis-lead-package');
        var nameInput = form.querySelector('#name');
        var emailInput = form.querySelector('#email');
        var phoneInput = form.querySelector('#phone1') || form.querySelector('#phone');
        var submitBtn = form.querySelector('#btnlead');

        var packageId = packageSelect ? parseInt(packageSelect.value, 10) : 0;
        var username = nameInput ? String(nameInput.value || '').trim() : '';
        var email = emailInput ? String(emailInput.value || '').trim() : '';
        var phone = sanitizePhone(phoneInput && phoneInput.value);

        if (!packageId) {
            showToast('Please select a package.', 'error');
            if (packageSelect) packageSelect.focus();
            return;
        }
        if (!username) {
            showToast('Please enter your first name.', 'error');
            if (nameInput) nameInput.focus();
            return;
        }
        if (!email) {
            showToast('Please enter your email address.', 'error');
            if (emailInput) emailInput.focus();
            return;
        }
        if (!phone) {
            showToast('Please enter a valid phone number.', 'error');
            if (phoneInput) phoneInput.focus();
            return;
        }

        if (phoneInput) phoneInput.value = phone;

        var payload = {
            username: username,
            email: email,
            phone: phone,
            gender: 'Not specified',
            date_of_birth: '1990-01-01',
            package: packageId
        };

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting…';
        }
        showToast('Sending your registration…', 'info');

        fetch(TRAINEE_API, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(function (res) {
                return res.json().then(function (data) {
                    return { ok: res.ok, data: data };
                });
            })
            .then(function (result) {
                if (!result.ok) {
                    var msg = (result.data && result.data.message) || 'Could not submit. Please try again.';
                    throw new Error(msg);
                }
                showToast('Thank you! We will contact you shortly.', 'success');
                showThankYou(form, username);
            })
            .catch(function (err) {
                var errMsg = err.message || 'Something went wrong. Please try again.';
                if (errMsg === 'Failed to fetch') {
                    errMsg = 'Could not reach the server. Check your connection and try again.';
                }
                showToast(errMsg, 'error');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit';
                }
            });
    }

    function init() {
        var form = document.getElementById('workoutlead');
        if (!form) return;

        var packageSelect = form.querySelector('#axis-lead-package');
        populatePackageSelect(packageSelect);
        form.addEventListener('submit', handleSubmit, true);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
