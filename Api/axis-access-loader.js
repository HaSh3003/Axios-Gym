/**
 * WHY AXIS? — stats from WordPress we__access API.
 * Updates [data-axis-why] featured cards via [data-axis-access-key].
 */
(function () {
    var API_URL = "https://axissportclub.com/wp-json/wp/v2/we__access?per_page=100&status=publish";

    var LABELS = {
        locations: function (v) {
            var n = parseInt(v, 10) || 0;
            return n + " LOCATION" + (n === 1 ? "" : "S");
        },
        members: function (v) {
            var n = parseInt(String(v).replace(/\D/g, ""), 10) || 0;
            return n.toLocaleString("en-US") + "+ MEMBERS";
        },
        paymentType: function (v) {
            var s = String(v || "").trim().toLowerCase();
            if (s === "monthly") return "PAY MONTHLY";
            if (s === "yearly" || s === "annual") return "PAY YEARLY";
            return String(v || "PAY MONTHLY").toUpperCase();
        },
        open24_7: function (v) {
            var s = String(v || "").trim().toLowerCase();
            if (s === "true" || s === "1" || s === "yes") return "OPEN 24/7";
            var hours = parseInt(s, 10);
            if (!isNaN(hours) && hours > 0) return "OPEN " + hours + " HOURS";
            return "OPEN DAILY";
        },
        freeClasses: function (v) {
            var n = parseInt(v, 10) || 0;
            return n + "+ FREE FITNESS CLASSES";
        },
        machines: function (v) {
            var n = parseInt(v, 10) || 0;
            return n + "+ FREE WEIGHTS & MACHINES";
        },
    };

    function buildMap(items) {
        var map = {};
        if (!Array.isArray(items)) return map;
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            if (item && item.key) map[item.key] = item.value_;
        }
        return map;
    }

    function applyLabels(section, map) {
        var nodes = section.querySelectorAll("[data-axis-access-key]");
        for (var i = 0; i < nodes.length; i++) {
            var el = nodes[i];
            var key = el.getAttribute("data-axis-access-key");
            var fn = LABELS[key];
            if (!fn || map[key] == null || map[key] === "") continue;
            var label = fn(map[key]);
            el.textContent = label;
            var card = el.closest(".featured-item");
            if (card) card.setAttribute("title", label);
        }
    }

    function loadSection(section) {
        fetch(API_URL, { credentials: "omit", mode: "cors" })
            .then(function (res) {
                if (!res.ok) throw new Error("HTTP " + res.status);
                return res.json();
            })
            .then(function (data) {
                applyLabels(section, buildMap(data));
            })
            .catch(function (err) {
                console.warn("[axis-access]", err);
            });
    }

    function init() {
        var sections = document.querySelectorAll("[data-axis-why]");
        for (var i = 0; i < sections.length; i++) {
            loadSection(sections[i]);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
