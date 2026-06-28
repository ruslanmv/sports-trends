/* sports-live.js — refresh live results + status on the same 30-minute cadence
   as the backend pipeline, without a full page reload. */

(function () {
  "use strict";

  var REFRESH_MS = 30 * 60 * 1000; // 30 minutes

  function refresh() {
    if (!window.SportsApp) return;
    window.SportsApp.fetchJson("live.json").then(window.SportsApp.render.live).catch(noop);
    window.SportsApp.fetchJson("status.json").then(window.SportsApp.render.status).catch(noop);
    window.SportsApp.fetchJson("trending.json").then(window.SportsApp.render.trending).catch(noop);
  }
  function noop() {}

  function start() {
    document.documentElement.dataset.sportsLiveReady = "true";
    setInterval(refresh, REFRESH_MS);
    // Refresh when the tab regains focus and enough is unknown to be stale.
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") refresh();
    });
  }

  if (document.readyState !== "loading") start();
  else document.addEventListener("DOMContentLoaded", start);
})();
