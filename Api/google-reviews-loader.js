/**
 * MEMBERS REVIEWS — Google summary (AXIS Sport) + WordPress member review cards.
 * Supports multiple sections via [data-axis-reviews].
 */
(function () {
    var MAPS_URL = "https://maps.app.goo.gl/L25K8wumDAcFRxXN8";
    var WP_REVIEWS_URL =
        window.AXIS_API && window.AXIS_API.url
            ? window.AXIS_API.url("/wp/v2/members_reviews?per_page=100&status=publish")
            : "https://admin.axissportclub.com/index.php?rest_route=/wp/v2/members_reviews&per_page=100&status=publish";
    var CACHE_URL =
        window.AXIS_API && window.AXIS_API.assetUrl
            ? window.AXIS_API.assetUrl("Api/jbr-reviews-cache.json")
            : "Api/jbr-reviews-cache.json";
    var QUOTE_SRC = "public/svgs/review-quote.svg";

    function escapeHtml(s) {
        return String(s == null ? "" : s)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/"/g, "&quot;");
    }

    function starDataUri(filled) {
        var fill = filled ? "#d12b2f" : "#e0e0e0";
        var svg =
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="' +
            fill +
            '" d="M12 3l2.6 6.3 6.8.6-5.2 4.5 1.6 6.6L12 17.8 5.2 21l1.6-6.6L1.6 9.9l6.8-.6z"/></svg>';
        return "data:image/svg+xml," + encodeURIComponent(svg);
    }

    function ratingStars(n, size) {
        n = Math.max(0, Math.min(5, Math.round(Number(n) || 0)));
        var w = size || 35;
        var html = '<ul class="rating-star">';
        for (var i = 0; i < 5; i++) {
            html += '<li><img src="' + starDataUri(i < n) + '" width="' + w + '" height="' + w + '" alt=""></li>';
        }
        html += "</ul>";
        return html;
    }

    function pickWpField(item, field) {
        if (!item) return "";
        if (item[field] != null && item[field] !== "") return item[field];
        if (item.acf && item.acf[field] != null && item.acf[field] !== "") return item.acf[field];
        if (item.meta && item.meta[field] != null && item.meta[field] !== "") return item.meta[field];
        return "";
    }

    function formatReviewDate(value) {
        var raw = String(value || "").trim();
        if (!raw) return "";
        var d = new Date(raw);
        if (isNaN(d.getTime())) return raw;
        return d.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
        });
    }

    function normalizeFromWpItem(item) {
        var text = String(pickWpField(item, "comment_")).trim();
        if (!text) return null;
        var refer = String(pickWpField(item, "refer")).trim() || "Member";
        return {
            author: String(pickWpField(item, "name_")).trim() || "Member",
            rating: Math.max(0, Math.min(5, Number(pickWpField(item, "stars_")) || 5)),
            text: text,
            time: formatReviewDate(pickWpField(item, "data_")),
            photoUri: "",
            source: refer,
        };
    }

    function normalizeFromWpList(items) {
        if (!Array.isArray(items)) return [];
        var out = [];
        for (var i = 0; i < items.length; i++) {
            var row = normalizeFromWpItem(items[i]);
            if (row) out.push(normalizeRow(row));
        }
        return out;
    }

    function fetchWpReviews() {
        return fetch(WP_REVIEWS_URL, { mode: "cors" }).then(function (res) {
            if (!res.ok) throw new Error("wp reviews " + res.status);
            return res.json();
        });
    }

    function normalizeRow(r) {
        return {
            author: String(r.author || "Member").trim() || "Member",
            rating: Math.max(0, Math.min(5, Number(r.rating) || 0)),
            text: String(r.text || "").trim(),
            time: String(r.time || "").trim(),
            photoUri: String(r.photoUri || "").trim(),
            source: String(r.source || "Member").trim() || "Member",
        };
    }

    function avatarHtml(photoUri) {
        if (photoUri) {
            return (
                '<img src="' +
                escapeHtml(photoUri) +
                '" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
            );
        }
        return (
            '<img src="data:image/svg+xml,' +
            encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="#e8eef2"/><text x="32" y="40" text-anchor="middle" font-size="26" fill="#022a3a" font-family="system-ui,sans-serif">★</text></svg>'
            ) +
            '" alt="">'
        );
    }

    function renderCardInner(r) {
        var av = avatarHtml(r.photoUri);
        var source = r.source || "Member";
        var topTitle = r.time || source;
        return (
            '<div class="review-item axis-review-card">' +
            '<div class="review-top">' +
            '<span class="quote-img"><img src="' +
            QUOTE_SRC +
            '" width="31" height="26" alt=""></span>' +
            '<span class="review-img">' +
            av +
            "</span>" +
            '<div class="title">' +
            escapeHtml(topTitle) +
            "</div>" +
            "</div>" +
            '<div class="review-content"><p>' +
            escapeHtml(r.text) +
            "</p></div>" +
            '<div class="review-btm">' +
            '<div class="author"><span>' +
            av +
            "</span>" +
            "<h3>" +
            escapeHtml(r.author) +
            "<span>" +
            escapeHtml(source) +
            "</span></h3></div>" +
            ratingStars(r.rating) +
            "</div>" +
            "</div>"
        );
    }

    function renderSummary(googleCache) {
        var maps = escapeHtml(googleCache.mapsUrl || MAPS_URL);
        var name = escapeHtml(googleCache.placeName || "AXIS SPORT - Personal Training & Gym JBR");
        var overall =
            googleCache.overallRating != null && googleCache.overallRating !== ""
                ? Number(googleCache.overallRating)
                : null;
        var count =
            googleCache.userRatingCount != null && googleCache.userRatingCount !== ""
                ? Number(googleCache.userRatingCount)
                : null;
        var stars = overall != null && !isNaN(overall) ? ratingStars(Math.round(overall), 28) : "";
        var scoreNum =
            overall != null && !isNaN(overall)
                ? '<span class="axis-reviews-score-num">' + overall.toFixed(1) + "</span>"
                : "";
        var countLabel =
            count && !isNaN(count)
                ? '<span class="axis-reviews-count">' + count + " Google reviews</span>"
                : "";

        return (
            '<div class="axis-reviews-summary">' +
            '<div class="axis-reviews-summary-inner">' +
            '<div class="axis-reviews-summary-main">' +
            '<span class="axis-reviews-place">' +
            name +
            "</span>" +
            '<div class="axis-reviews-score-row">' +
            scoreNum +
            stars +
            "</div>" +
            countLabel +
            "</div>" +
            '<a class="axis-reviews-maps-pill" href="' +
            maps +
            '" target="_blank" rel="noopener noreferrer">View on Maps</a>' +
            "</div></div>"
        );
    }

    function buildCardsSwiperHtml(reviews) {
        var slides = "";
        for (var i = 0; i < reviews.length; i++) {
            slides +=
                '<div class="swiper-slide"><div class="axis-review-slide-in">' +
                renderCardInner(reviews[i]) +
                "</div></div>";
        }
        return (
            '<div class="swiper axis-reviews-swiper">' +
            '<div class="swiper-wrapper">' +
            slides +
            "</div>" +
            '<div class="swiper-pagination axis-reviews-pagination"></div>' +
            '<div class="swiper-button-prev axis-reviews-prev" aria-label="Previous reviews"></div>' +
            '<div class="swiper-button-next axis-reviews-next" aria-label="Next reviews"></div>' +
            "</div>"
        );
    }

    function fetchJson(url) {
        return fetch(url, { credentials: "same-origin" }).then(function (res) {
            if (!res.ok) throw new Error("bad status");
            return res.json();
        });
    }

    function fetchReviewsFromPlaces(apiKey) {
        var headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": apiKey,
            "X-Goog-FieldMask": "places.id,places.displayName",
        };
        var body = JSON.stringify({
            textQuery: "AXIS SPORT Personal Training Gym JBR Dubai",
            locationBias: {
                circle: {
                    center: { latitude: 25.0744576, longitude: 55.1314458 },
                    radius: 120,
                },
            },
        });
        return fetch("https://places.googleapis.com/v1/places:searchText", {
            method: "POST",
            headers: headers,
            body: body,
        })
            .then(function (res) {
                return res.json().then(function (data) {
                    if (!res.ok) throw new Error(JSON.stringify(data));
                    return data;
                });
            })
            .then(function (data) {
                var places = data.places || [];
                if (!places.length) throw new Error("no places");
                var pid = places[0].id;
                var h2 = {
                    "X-Goog-Api-Key": apiKey,
                    "X-Goog-FieldMask": "displayName,id,rating,userRatingCount",
                };
                return fetch("https://places.googleapis.com/v1/places/" + encodeURIComponent(pid), {
                    headers: h2,
                }).then(function (r2) {
                    return r2.json().then(function (d2) {
                        if (!r2.ok) throw new Error(JSON.stringify(d2));
                        return d2;
                    });
                });
            });
    }

    function mergeGoogleSummary(details, prev) {
        var dn = details.displayName;
        var placeName =
            typeof dn === "object" && dn
                ? dn.text || dn.name || prev.placeName
                : dn || prev.placeName;
        return {
            placeName: placeName || prev.placeName,
            mapsUrl: prev.mapsUrl || MAPS_URL,
            overallRating: details.rating != null ? Number(details.rating) : prev.overallRating,
            userRatingCount:
                details.userRatingCount != null
                    ? Number(details.userRatingCount)
                    : prev.userRatingCount,
            fetchedAt: new Date().toISOString(),
        };
    }

    function runSwiper(root) {
        var el = root.querySelector(".axis-reviews-swiper");
        if (!el || typeof Swiper === "undefined") return;

        if (el.axisSwiperInstance) {
            try {
                el.axisSwiperInstance.destroy(true, true);
            } catch (e) {}
            el.axisSwiperInstance = null;
        }

        var n = el.querySelectorAll(".swiper-slide").length;
        var enableLoop = n > 3;

        el.axisSwiperInstance = new Swiper(el, {
            slidesPerView: 1,
            spaceBetween: 20,
            loop: enableLoop,
            watchOverflow: true,
            speed: 480,
            grabCursor: true,
            pagination: {
                el: root.querySelector(".axis-reviews-pagination"),
                clickable: true,
                dynamicBullets: n > 5,
            },
            navigation: {
                prevEl: root.querySelector(".axis-reviews-prev"),
                nextEl: root.querySelector(".axis-reviews-next"),
            },
            breakpoints: {
                640: { slidesPerView: 1, spaceBetween: 22 },
                768: { slidesPerView: 2, spaceBetween: 22 },
                1200: { slidesPerView: 3, spaceBetween: 24 },
            },
        });
    }

    function paint(container, googleCache, cardReviews) {
        var list = cardReviews.map(normalizeRow).filter(function (r) {
            return r.text.length > 0;
        });
        if (!list.length) {
            list = [
                {
                    author: "AXIS",
                    rating: 5,
                    text: "Member reviews will appear here once published on the website.",
                    time: "",
                    photoUri: "",
                    source: "AXIS",
                },
            ];
        }
        container.innerHTML =
            '<div class="axis-reviews-root">' +
            renderSummary(googleCache) +
            buildCardsSwiperHtml(list) +
            "</div>";
        container.classList.remove("is-loading");

        requestAnimationFrame(function () {
            runSwiper(container);
        });
    }

    function getPlacesKey() {
        return typeof window !== "undefined" && window.__AXIS_GOOGLE_PLACES_KEY__
            ? String(window.__AXIS_GOOGLE_PLACES_KEY__).trim()
            : "";
    }

    function defaultGoogleCache() {
        return {
            placeName: "AXIS SPORT - Personal Training & Gym JBR",
            mapsUrl: MAPS_URL,
            overallRating: null,
            userRatingCount: null,
        };
    }

    function loadGoogleSummary() {
        var base = defaultGoogleCache();
        return fetchJson(CACHE_URL)
            .then(function (cache) {
                var summary = {
                    placeName: cache.placeName || base.placeName,
                    mapsUrl: cache.mapsUrl || base.mapsUrl,
                    overallRating: cache.overallRating,
                    userRatingCount: cache.userRatingCount,
                };
                var key = getPlacesKey();
                if (!key) return summary;
                return fetchReviewsFromPlaces(key)
                    .then(function (details) {
                        return mergeGoogleSummary(details, summary);
                    })
                    .catch(function () {
                        return summary;
                    });
            })
            .catch(function () {
                var key = getPlacesKey();
                if (!key) return base;
                return fetchReviewsFromPlaces(key)
                    .then(function (details) {
                        return mergeGoogleSummary(details, base);
                    })
                    .catch(function () {
                        return base;
                    });
            });
    }

    function loadCardReviews() {
        return fetchWpReviews()
            .then(function (items) {
                return normalizeFromWpList(items);
            })
            .catch(function () {
                return [];
            });
    }

    function initContainer(container, googleCache, cardReviews) {
        container.classList.add("axis-reviews-root-wrap", "is-loading");
        paint(container, googleCache, cardReviews);
    }

    function init() {
        var containers = document.querySelectorAll("[data-axis-reviews]");
        if (!containers.length) {
            var legacy = document.getElementById("reviewdata");
            if (legacy) legacy.setAttribute("data-axis-reviews", "");
            containers = document.querySelectorAll("[data-axis-reviews]");
        }
        if (!containers.length) return;

        Promise.all([loadGoogleSummary(), loadCardReviews()]).then(function (results) {
            var googleCache = results[0];
            var cardReviews = results[1];
            for (var i = 0; i < containers.length; i++) {
                initContainer(containers[i], googleCache, cardReviews);
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
