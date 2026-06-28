/* sports-pages.js — hydrate the sport pages and list pages (football, live,
   tomorrow, predictions, trending, rankings) from the public JSON. Filters by
   the board's sport and adds the World Cup + in-season blocks for football. */
(function () {
  "use strict";
  var meta = document.querySelector('meta[name="sports-base"]');
  var SITE = (meta ? meta.content : "/").replace(/\/$/, "");
  var BASE = SITE + "/assets/data/sports/";
  var ICON = { football:"⚽", basketball:"🏀", tennis:"🎾", cricket:"🏏", baseball:"⚾", esports:"🎮" };

  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function pct(v){return Math.round((v||0)*100)+"%";}
  function icon(s){return ICON[s]||"🏆";}
  function get(n){return fetch(BASE+n,{cache:"no-store"}).then(function(r){if(!r.ok)throw 0;return r.json();});}
  function title(s){return (s||"").replace(/_/g," ").replace(/\b\w/g,function(c){return c.toUpperCase();});}

  var board = document.querySelector("[data-sport-board]");
  if (!board) return;
  var SPORT = board.getAttribute("data-sport-board") || "all";
  function keep(m){ return SPORT === "all" || m.sport === SPORT; }

  function matchCard(m){
    var p = m.probabilities || {};
    var home=p.home_win||0, draw=p.draw||0, away=p.away_win||0;
    return '<article class="board-card" data-sport="'+esc(m.sport)+'">'+
      '<div class="board-card-top"><span class="sport-ic">'+icon(m.sport)+'</span>'+
        '<span class="board-league">'+esc(m.league)+'</span>'+
        '<span class="board-time">'+esc(m.kickoff_label||"TBD")+'</span></div>'+
      '<div class="board-teams"><span>'+esc(m.home_team)+'</span><span class="board-vs">vs</span><span>'+esc(m.away_team)+'</span></div>'+
      '<div class="mr-bar"><i class="home" style="width:'+pct(home)+'"></i><i class="draw" style="width:'+pct(draw)+'"></i><i class="away" style="width:'+pct(away)+'"></i></div>'+
      '<div class="mr-pcts"><span class="home">'+pct(home)+'</span><span class="draw">DRAW '+pct(draw)+'</span><span class="away">'+pct(away)+'</span></div>'+
      (m.prediction_label?'<div class="board-ai">✦ '+esc(m.prediction_label.replace(/^AI:\s*/,""))+' · '+pct(m.confidence)+' confidence</div>':'')+
      '</article>';
  }

  function fill(sel, html, empty){
    var el = document.querySelector(sel); if(!el) return;
    el.innerHTML = html || ('<p class="board-empty">'+empty+'</p>');
  }

  // Upcoming (tomorrow.json) — used by sport pages, /tomorrow/, /predictions/
  if (document.querySelector("[data-board-upcoming]")) {
    get("tomorrow.json").then(function(d){
      var ms=(d.matches||[]).filter(keep);
      fill("[data-board-upcoming]", ms.map(matchCard).join(""), "No upcoming fixtures.");
    }).catch(function(){});
  }
  if (document.querySelector("[data-board-predictions]")) {
    get("predictions.json").then(function(d){
      var ms=(d.matches||[]).filter(keep);
      fill("[data-board-predictions]", ms.map(matchCard).join(""), "No predictions yet.");
    }).catch(function(){});
  }

  // Live (live.json)
  if (document.querySelector("[data-board-live]")) {
    get("live.json").then(function(d){
      var ms=(d.matches||[]).filter(keep);
      var html=ms.map(function(m){
        var fin=m.is_finished, score=(m.away_score==null)?esc(m.home_score):esc(m.home_score)+" - "+esc(m.away_score);
        var cls=(typeof m.home_score==="string"&&m.home_score.indexOf(",")>-1)?"lr-score sets":"lr-score";
        return '<li class="live-row"><span class="sport-ic">'+icon(m.sport)+'</span><div class="lr-main">'+
          '<div class="lr-league">'+esc(m.league)+'</div><div class="lr-teams">'+esc(m.home_team)+' <span class="'+cls+'">'+score+'</span> '+esc(m.away_team)+'</div>'+
          '<div class="lr-detail">'+esc(m.status_detail||"")+'</div></div>'+(fin?'<span class="badge-done">FT</span>':'<span class="badge-live">LIVE</span>')+'</li>';
      }).join("");
      fill("[data-board-live]", html, "No live games right now.");
    }).catch(function(){});
  }

  // Trending (trending.json)
  if (document.querySelector("[data-board-trending]")) {
    get("trending.json").then(function(d){
      var html=(d.matches||[]).map(function(m){
        return '<li class="trend-row'+(m.hot?" top":"")+'"><span class="trend-rank">'+(m.hot?"🔥":m.rank)+'</span>'+
          '<span class="trend-label">'+esc(m.label)+'</span><span class="trend-aud">'+esc(m.audience||"")+'</span></li>';
      }).join("");
      fill("[data-board-trending]", html, "No trending matches.");
    }).catch(function(){});
  }

  // Explore (rankings.json)
  if (document.querySelector("[data-board-explore]")) {
    get("rankings.json").then(function(d){
      var html=(d.explore_sports||[]).map(function(s){
        return '<a class="explore-card" data-sport="'+esc(s.sport)+'" href="'+SITE+'/sports/'+esc(s.sport)+'/">'+
          '<span class="ex-ic">'+icon(s.sport)+'</span><span class="ex-body"><strong>'+esc(s.label)+'</strong>'+
          '<span class="ex-live"><i></i>'+Number(s.live).toLocaleString()+' Live</span></span></a>';
      }).join("");
      fill("[data-board-explore]", html, "");
    }).catch(function(){});
  }

  // In-season strip (season.json), filtered by sport
  if (document.querySelector("[data-board-season]")) {
    get("season.json").then(function(s){
      var act=(s.active||[]).filter(function(a){return SPORT==="all"||a.sport===SPORT;});
      if(!act.length) return;
      var wrap=document.querySelector("[data-season-wrap]"); if(wrap) wrap.removeAttribute("hidden");
      fill("[data-board-season]", act.map(function(a){
        return '<span class="season-chip">'+esc(a.emoji)+' '+esc(a.name)+'</span>';
      }).join(""), "");
    }).catch(function(){});
  }

  // World Cup ties for the football page
  if (document.querySelector("[data-wc-ties]")) {
    get("worldcup-predictions.json").then(function(wc){
      var ties=(wc.matches||[]).filter(function(m){return m.to_advance;}).slice(0,4);
      var st=document.querySelector("[data-wc-stage]"); if(st&&ties[0]) st.textContent=title(ties[0].stage);
      fill("[data-wc-ties]", ties.map(function(m){
        var adv=m.to_advance||{}, names=Object.keys(adv).sort(function(a,b){return adv[b]-adv[a];}), lead=names[0]||"";
        return '<li class="board-tie"><span>'+esc(m.home_team)+' vs '+esc(m.away_team)+'</span><b>'+esc(lead)+' '+pct(adv[lead])+'</b></li>';
      }).join(""), "World Cup ties appear during the tournament.");
    }).catch(function(){});
  }
})();
