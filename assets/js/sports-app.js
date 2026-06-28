/* sports-app.js — hydrate the /sports/ dashboard from the small public JSON
   files. Every section ships static fallback markup, so if a fetch fails the
   page still looks correct (graceful degradation, no layout shift). */

(function () {
  "use strict";

  var _b=(document.querySelector('meta[name="sports-base"]')||{}).content||"/"; var SITE=_b.replace(/\/$/,""); var BASE=SITE+"/assets/data/sports/";
  var SPORT_ICON = {
    football: "⚽", basketball: "🏀", tennis: "🎾",
    cricket: "🏏", baseball: "⚾", esports: "🎮"
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function icon(sport) { return SPORT_ICON[sport] || "🏆"; }
  function pct(v) { return Math.round((v || 0) * 100) + "%"; }

  function fetchJson(name) {
    return fetch(BASE + name, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status + " for " + name);
      return r.json();
    });
  }

  // ---- Status + stats ----
  function renderStatus(status) {
    var el = document.querySelector("[data-sports-status]");
    if (el && status.last_updated) {
      var d = new Date(status.last_updated);
      el.textContent = "Updated " + d.toLocaleString();
    }
    var stats = status.stats || {};
    var map = {
      top_matches: stats.top_matches,
      live_games: stats.live_games,
      global_fans: stats.global_fans
    };
    Object.keys(map).forEach(function (k) {
      var node = document.querySelector('[data-stat="' + k + '"]');
      if (node && map[k] != null) node.textContent = map[k];
    });
  }

  // ---- Tomorrow's top matches ----
  function renderTomorrow(data) {
    var list = document.querySelector("[data-tomorrow-matches]");
    if (!list || !data.matches) return;
    list.innerHTML = data.matches.slice(0, 4).map(function (m) {
      var p = m.probabilities || {};
      var home = (p.home_win || 0), draw = (p.draw || 0), away = (p.away_win || 0);
      var t = m.kickoff_label || "TBD";
      return (
        '<li class="match-row" data-sport="' + esc(m.sport) + '">' +
          '<div class="mr-top"><span class="sport-ic">' + icon(m.sport) + '</span>' +
            '<span class="mr-league">' + esc(m.league) + '</span>' +
            '<span class="mr-time"><b>' + esc(t) + '</b>Tomorrow</span></div>' +
          '<div class="mr-teams">' +
            '<span class="mr-team"><span class="mr-logo">' + icon(m.sport) + '</span>' + esc(m.home_team) + '</span>' +
            '<span class="mr-team away"><span class="mr-logo">' + icon(m.sport) + '</span>' + esc(m.away_team) + '</span>' +
          '</div>' +
          '<div class="mr-bar"><i class="home" style="width:' + pct(home) + '"></i>' +
            '<i class="draw" style="width:' + pct(draw) + '"></i>' +
            '<i class="away" style="width:' + pct(away) + '"></i></div>' +
          '<div class="mr-pcts"><span class="home">' + pct(home) + '</span>' +
            '<span class="draw">DRAW ' + pct(draw) + '</span>' +
            '<span class="away">' + pct(away) + '</span></div>' +
        '</li>'
      );
    }).join("");
  }

  // ---- Live results ----
  function renderLive(data) {
    var list = document.querySelector("[data-live-results]");
    if (!list || !data.matches) return;
    list.innerHTML = data.matches.map(function (m) {
      var finished = m.is_finished;
      var score = (m.away_score == null)
        ? esc(m.home_score)
        : esc(m.home_score) + " - " + esc(m.away_score);
      var scoreCls = (typeof m.home_score === "string" && m.home_score.indexOf(",") > -1) ? "lr-score sets" : "lr-score";
      var badge = finished ? '<span class="badge-done">FT</span>' : '<span class="badge-live">LIVE</span>';
      return (
        '<li class="live-row" data-sport="' + esc(m.sport) + '">' +
          '<span class="sport-ic">' + icon(m.sport) + '</span>' +
          '<div class="lr-main">' +
            '<div class="lr-league">' + esc(m.league) + '</div>' +
            '<div class="lr-teams">' + esc(m.home_team) + ' <span class="' + scoreCls + '">' + score + '</span> ' + esc(m.away_team) + '</div>' +
            '<div class="lr-detail">' + esc(m.status_detail || "") + '</div>' +
          '</div>' + badge +
        '</li>'
      );
    }).join("");
  }

  // ---- Trending ----
  function spark() {
    return '<svg class="trend-spark" viewBox="0 0 38 18" fill="none" aria-hidden="true">' +
      '<path d="M1 14 L8 11 L14 13 L21 6 L28 8 L37 2" stroke="currentColor" stroke-width="1.6" ' +
      'stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }
  function renderTrending(data) {
    var list = document.querySelector("[data-trending-matches]");
    if (!list || !data.matches) return;
    list.innerHTML = data.matches.map(function (m) {
      var rank = m.hot ? "🔥" : m.rank;
      return (
        '<li class="trend-row' + (m.hot ? " top" : "") + '">' +
          '<span class="trend-rank">' + esc(rank) + '</span>' +
          '<span class="trend-label">' + esc(m.label) + '</span>' +
          '<span class="trend-aud">' + esc(m.audience || "") + '</span>' + spark() +
        '</li>'
      );
    }).join("");
    var region = document.querySelector("[data-trending-region]");
    if (region && data.region) region.innerHTML = esc(data.region) + " ▾";
  }

  // ---- Explore counts ----
  function renderExplore(rankings) {
    if (!rankings || !rankings.explore_sports) return;
    rankings.explore_sports.forEach(function (s) {
      var card = document.querySelector('.explore-card[data-sport="' + s.sport + '"] .ex-live');
      if (card) card.innerHTML = '<i></i>' + Number(s.live).toLocaleString() + " Live";
    });
  }

  // ---- Season-aware featured / World Cup mini-card ----
  function renderFeatured(season) {
    var card = document.querySelector("[data-featured]");
    if (!card) return;
    var feat = season.featured || {};
    var title = document.querySelector("[data-featured-title]");
    var tag = document.querySelector("[data-featured-tag]");
    var body = document.querySelector("[data-featured-body]");
    var link = document.querySelector("[data-featured-link]");
    var cta = document.querySelector("[data-featured-cta]");

    // Toggle the World Cup promo banner with the season.
    var banner = document.querySelector(".wc-banner");
    if (banner) banner.style.display = season.worldcup_active ? "" : "none";

    if (season.worldcup_active) {
      if (title) title.innerHTML = "🏆 World Cup";
      if (link) { link.textContent = "Board"; link.href = SITE + "/sports/football/world-cup/"; }
      if (cta) cta.href = SITE + "/sports/football/world-cup/";
      fetchJson("worldcup-predictions.json").then(function (wc) {
        var ties = (wc.matches || []).filter(function (m) { return m.to_advance; }).slice(0, 2);
        if (tag && ties[0]) tag.textContent = (ties[0].stage || "").replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
        if (body) body.innerHTML = ties.map(function (m) {
          var r = m.result_90 || {}, adv = m.to_advance || {};
          var names = Object.keys(adv).sort(function (a, b) { return adv[b] - adv[a]; });
          var lead = names[0] || "";
          return '<li class="wc-mini-tie">' +
            '<div class="wc-mini-teams"><span>' + esc(m.home_team) + " vs " + esc(m.away_team) + '</span><b>' + pct(adv[lead]) + '</b></div>' +
            '<div class="mr-bar"><i class="home" style="width:' + pct(r.team1) + '"></i><i class="draw" style="width:' + pct(r.draw) + '"></i><i class="away" style="width:' + pct(r.team2) + '"></i></div>' +
            '<div class="wc-mini-sub">' + esc(lead) + " " + pct(adv[lead]) + " to advance</div></li>";
        }).join("");
      }).catch(warn);
    } else {
      // Off-season for the World Cup → feature the top in-season competition.
      if (title) title.innerHTML = (feat.emoji || "🏆") + " In Season";
      if (tag) tag.textContent = (feat.name || "Football");
      if (link) { link.textContent = "Sports"; link.href = SITE + "/"; }
      if (cta) { cta.textContent = "Explore →"; cta.href = SITE + "/"; }
      var active = (season.active || []).slice(0, 4);
      if (body) body.innerHTML = active.map(function (a) {
        return '<li class="wc-mini-tie"><div class="wc-mini-teams"><span>' + esc(a.emoji) + " " + esc(a.name) +
          '</span><b>' + esc(a.importance) + '</b></div>' +
          '<div class="wc-mini-sub">' + esc(a.sport) + " · " + esc(a.scope) + "</div></li>";
      }).join("");
    }
  }

  function hydrate() {
    fetchJson("status.json").then(renderStatus).catch(warn);
    fetchJson("tomorrow.json").then(renderTomorrow).catch(warn);
    fetchJson("live.json").then(renderLive).catch(warn);
    fetchJson("trending.json").then(renderTrending).catch(warn);
    fetchJson("rankings.json").then(renderExplore).catch(warn);
    fetchJson("season.json").then(renderFeatured).catch(warn);
  }
  function warn(e) { if (window.console) console.warn("[sports] using fallback:", e.message); }

  window.SportsApp = { hydrate: hydrate, fetchJson: fetchJson,
    render: { status: renderStatus, tomorrow: renderTomorrow, live: renderLive, trending: renderTrending, explore: renderExplore } };

  if (document.readyState !== "loading") hydrate();
  else document.addEventListener("DOMContentLoaded", hydrate);
})();
