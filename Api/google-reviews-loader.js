/**
 * MEMBERS REVIEWS — Swiper + Api/jbr-reviews-cache.json; optional live fetch via Places API when __AXIS_GOOGLE_PLACES_KEY__ is set.
 */
(function () {
    var MAPS_URL = "https://maps.app.goo.gl/L25K8wumDAcFRxXN8";
    var CACHE_URL = "Api/jbr-reviews-cache.json";
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

    function normalizeFromPlacesDetails(details) {
        var list = [];
        var reviews = details.reviews || [];
        for (var i = 0; i < reviews.length; i++) {
            var r = reviews[i];
            var auth = r.authorAttribution || {};
            var textObj = r.text || r.originalText || {};
            var text = typeof textObj === "object" ? textObj.text || "" : "";
            text = String(text).trim();
            if (!text) continue;
            list.push({
                author: auth.displayName || "Google user",
                rating: Number(r.rating) || 0,
                text: text,
                time: r.relativePublishTimeDescription || "",
                photoUri: auth.photoUri || "",
            });
        }
        return list;
    }

    function normalizeRow(r) {
        return {
            author: String(r.author || "Member").trim() || "Member",
            rating: Math.max(0, Math.min(5, Number(r.rating) || 0)),
            text: String(r.text || "").trim(),
            time: String(r.time || "").trim(),
            photoUri: String(r.photoUri || "").trim(),
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
        var topTitle = r.time || "Google Maps";
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
            '<span>Google Maps</span></h3></div>' +
            ratingStars(r.rating) +
            "</div>" +
            "</div>"
        );
    }

    function avgFromReviews(reviews) {
        if (!reviews.length) return null;
        var s = 0;
        for (var i = 0; i < reviews.length; i++) s += Number(reviews[i].rating) || 0;
        return Math.round((s / reviews.length) * 10) / 10;
    }

    function renderSummary(cache, reviews) {
        var maps = escapeHtml(cache.mapsUrl || MAPS_URL);
        var name = escapeHtml(cache.placeName || "AXIS SPORT JBR");
        var overall =
            cache.overallRating != null && cache.overallRating !== ""
                ? Number(cache.overallRating)
                : avgFromReviews(reviews);
        var count =
            cache.userRatingCount != null && cache.userRatingCount !== ""
                ? Number(cache.userRatingCount)
                : reviews.length;
        var stars = overall != null && !isNaN(overall) ? ratingStars(Math.round(overall), 28) : "";
        var scoreNum =
            overall != null && !isNaN(overall)
                ? '<span class="axis-reviews-score-num">' + overall.toFixed(1) + "</span>"
                : "";
        var countLabel =
            count && !isNaN(count)
                ? '<span class="axis-reviews-count">' +
                  count +
                  " Google reviews</span>"
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

    function buildSwiperHtml(reviews, cache) {
        var slides = "";
        for (var i = 0; i < reviews.length; i++) {
            slides +=
                '<div class="swiper-slide"><div class="axis-review-slide-in">' +
                renderCardInner(reviews[i]) +
                "</div></div>";
        }
        return (
            renderSummary(cache, reviews) +
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
                    "X-Goog-FieldMask": "reviews,displayName,id,rating,userRatingCount",
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


    function mergeLiveCache(details, prev) {
        var reviews = normalizeFromPlacesDetails(details);
        var mapped = reviews.map(normalizeRow);
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
            reviews: mapped,
        };
    }

    function runSwiper(root) {
        var el = root.querySelector(".axis-reviews-swiper");
        if (!el || typeof Swiper === "undefined") return;

        if (window.__axisReviewsSwiper) {
            try {
                window.__axisReviewsSwiper.destroy(true, true);
            } catch (e) {}
            window.__axisReviewsSwiper = null;
        }

        var n = el.querySelectorAll(".swiper-slide").length;
        var enableLoop = n > 3;

        window.__axisReviewsSwiper = new Swiper(el, {
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

    function paint(container, cache, reviews) {
        var list = reviews.map(normalizeRow).filter(function (r) {
            return r.text.length > 0;
        });
        if (!list.length) {
            list = [
                {
                    author: "AXIS",
                    rating: 5,
                    text: "Add a Google Places API key in index.html or run scripts/fetch_google_reviews.py (with Api/.env) to load live Google reviews here.",
                    time: "",
                    photoUri: "",
                },
            ];
        }
        container.innerHTML =
            '<div class="axis-reviews-root">' + buildSwiperHtml(list, cache) + "</div>";
        container.classList.remove("is-loading");

        requestAnimationFrame(function () {
            runSwiper(container);
        });
    }

    function loadFromPlacesThenPaint(container, cache, key) {
        return fetchReviewsFromPlaces(key)
            .then(function (details) {
                var merged = mergeLiveCache(details, cache);
                var rows = (merged.reviews || []).map(normalizeRow).filter(function (r) {
                    return r.text.length > 0;
                });
                if (!rows.length && (cache.reviews || []).length) {
                    var cached = (cache.reviews || []).map(normalizeRow).filter(function (r) {
                        return r.text.length > 0;
                    });
                    if (cached.length) {
                        paint(container, merged, cached);
                        return;
                    }
                }
                paint(container, merged, rows);
            })
            .catch(function () {
                var cached = (cache.reviews || []).map(normalizeRow).filter(function (r) {
                    return r.text.length > 0;
                });
                paint(container, cache, cached.length ? cached : []);
            });
    }

    function getPlacesKey() {
        return typeof window !== "undefined" && window.__AXIS_GOOGLE_PLACES_KEY__
            ? String(window.__AXIS_GOOGLE_PLACES_KEY__).trim()
            : "";
    }

    function init() {
        var container = document.getElementById("reviewdata");
        if (!container) return;
        container.classList.add("axis-reviews-root-wrap", "is-loading");

        var emptyCache = {
            placeName: "AXIS SPORT - Personal Training & Gym JBR",
            mapsUrl: MAPS_URL,
            overallRating: null,
            userRatingCount: null,
            reviews: [],
        };

        fetchJson(CACHE_URL)
            .then(function (cache) {
                var key = getPlacesKey();
                var cachedRows = (cache.reviews || []).map(normalizeRow).filter(function (r) {
                    return r.text.length > 0;
                });

                if (key) {
                    loadFromPlacesThenPaint(container, cache, key).catch(function () {
                        paint(container, cache, cachedRows.length ? cachedRows : []);
                    });
                    return;
                }

                paint(container, cache, cachedRows);
            })
            .catch(function () {
                var key = getPlacesKey();
                if (key) {
                    loadFromPlacesThenPaint(container, emptyCache, key).catch(function () {
                        paint(container, emptyCache, []);
                    });
                    return;
                }
                paint(container, emptyCache, []);
            });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
