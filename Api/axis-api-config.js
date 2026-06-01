/**
 * Central WordPress API base for admin.axissportclub.com.
 * Pretty /wp-json/ URLs return 404 on this host; use index.php?rest_route= instead.
 */
(function () {
    "use strict";

    var ORIGIN = "https://admin.axissportclub.com";

    function findConfigScript() {
        if (document.currentScript && document.currentScript.src) {
            return document.currentScript;
        }
        var scripts = document.getElementsByTagName("script");
        for (var i = scripts.length - 1; i >= 0; i--) {
            var s = scripts[i];
            if (s.src && /axis-api-config\.js/i.test(s.src)) return s;
        }
        return null;
    }

    var configScript = findConfigScript();
    var apiBaseHref = configScript
        ? configScript.src.replace(/\/axis-api-config\.js(\?.*)?$/i, "/")
        : ORIGIN + "/Api/";
    var siteRootHref = new URL("..", apiBaseHref).href;

    /** @param {string} path e.g. "/wp/v2/membership?per_page=100" */
    function url(path) {
        var p = path.charAt(0) === "/" ? path : "/" + path;
        var qIndex = p.indexOf("?");
        var route = qIndex >= 0 ? p.slice(0, qIndex) : p;
        var query = qIndex >= 0 ? p.slice(qIndex + 1) : "";
        var out = ORIGIN + "/index.php?rest_route=" + route;
        if (query) out += "&" + query;
        return out;
    }

    function assetUrl(relativePath) {
        var rel = String(relativePath || "").replace(/^\//, "");
        try {
            return new URL(rel, siteRootHref).href;
        } catch (e) {
            return rel;
        }
    }

    window.AXIS_API = {
        origin: ORIGIN,
        url: url,
        assetUrl: assetUrl,
    };
})();
