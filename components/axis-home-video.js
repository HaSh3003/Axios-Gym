/**
 * Homepage hero video — autoplay (muted) with optional sound via controls.
 */
(function () {
    'use strict';
    if (window.__AXIS_HOME_VIDEO__) return;
    window.__AXIS_HOME_VIDEO__ = true;

    function startVideo(video) {
        if (!video) return;
        video.muted = true;
        video.defaultMuted = true;
        video.setAttribute('muted', '');
        video.playsInline = true;
        video.setAttribute('playsinline', '');
        video.autoplay = true;
        video.loop = true;
        var playPromise = video.play();
        if (playPromise && typeof playPromise.catch === 'function') {
            playPromise.catch(function () {});
        }
    }

    function init() {
        var videos = document.querySelectorAll(
            '.gym-video-section .axis-video-frame video'
        );
        for (var i = 0; i < videos.length; i++) {
            startVideo(videos[i]);
            videos[i].addEventListener('loadeddata', function () {
                startVideo(this);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
