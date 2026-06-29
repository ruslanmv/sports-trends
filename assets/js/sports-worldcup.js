/* sports-worldcup.js — hydrate the premium World Cup page from worldcup*.json.
   Powers: stat ribbon, hero countdown, the full match schedule (with segmented
   filters), knockout predictions, the road-to-the-final bracket, live group
   standings and qualifiers. Degrades silently when a feed is missing. */
(function () {
  "use strict";
  var _b = (document.querySelector('meta[name="sports-base"]') || {}).content || "/";
  var BASE = (_b.replace(/\/$/, "")) + "/assets/data/sports/";

  var FLAG = {
    Argentina:"🇦🇷",Brazil:"🇧🇷",Uruguay:"🇺🇾",Colombia:"🇨🇴",Ecuador:"🇪🇨",Paraguay:"🇵🇾",
    France:"🇫🇷",Spain:"🇪🇸",England:"🏴󠁧󠁢󠁥󠁮󠁧󠁿",Portugal:"🇵🇹",Netherlands:"🇳🇱",Germany:"🇩🇪",
    Italy:"🇮🇹",Croatia:"🇭🇷",Belgium:"🇧🇪",Switzerland:"🇨🇭",Austria:"🇦🇹",Norway:"🇳🇴",
    Sweden:"🇸🇪",Scotland:"🏴󠁧󠁢󠁳󠁣󠁴󠁿",Turkey:"🇹🇷","Czech Republic":"🇨🇿","Bosnia & Herzegovina":"🇧🇦",
    Morocco:"🇲🇦",Senegal:"🇸🇳","Ivory Coast":"🇨🇮",Algeria:"🇩🇿",Egypt:"🇪🇬",Tunisia:"🇹🇳",
    Ghana:"🇬🇭","Cape Verde":"🇨🇻","South Africa":"🇿🇦","DR Congo":"🇨🇩",Nigeria:"🇳🇬",
    Japan:"🇯🇵","South Korea":"🇰🇷",Iran:"🇮🇷",Australia:"🇦🇺","Saudi Arabia":"🇸🇦",Qatar:"🇶🇦",
    Uzbekistan:"🇺🇿",Iraq:"🇮🇶",Jordan:"🇯🇴",USA:"🇺🇸",Mexico:"🇲🇽",Canada:"🇨🇦",Panama:"🇵🇦",
    Haiti:"🇭🇹","Curaçao":"🇨🇼","New Zealand":"🇳🇿"
  };
  var KNOCKOUTS = ["round_of_32","round_of_16","quarterfinals","semifinals","third_place","final"];

  function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
  function flag(t){return FLAG[t]||"⚽";}
  function pct(v){return Math.round((v||0)*100)+"%";}
  function get(n){return fetch(BASE+n,{cache:"no-store"}).then(function(r){if(!r.ok)throw 0;return r.json();});}
  function stageName(s){return (s||"").replace(/_/g," ").replace(/\b\w/g,function(c){return c.toUpperCase();});}
  function isKnockout(s){return KNOCKOUTS.indexOf(s)>=0;}
  function $(sel){return document.querySelector(sel);}

  function dayKey(iso,date){
    var d = iso?new Date(iso):(date?new Date(date+"T00:00:00Z"):null);
    return d&&!isNaN(d)?d:null;
  }
  function dayLabel(d){
    return d.toLocaleDateString(undefined,{weekday:"long",day:"numeric",month:"long"});
  }
  function timeLabel(iso){
    if(!iso)return "TBD";
    var d=new Date(iso); if(isNaN(d))return "TBD";
    return d.toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"});
  }

  /* ---------------- Stat ribbon ---------------- */
  function renderStats(fx){
    var el=$("[data-wc-statribbon]"); if(!el||!fx)return;
    var all=flatten(fx);
    var played=all.filter(function(m){return m.status==="finished";}).length;
    set(el,"upcoming",fx.upcoming!=null?fx.upcoming:all.length-played);
    set(el,"played",played);
    set(el,"total",fx.total||all.length);
  }
  function set(el,k,v){var n=el.querySelector('[data-stat="'+k+'"]'); if(n)n.textContent=v;}
  function flatten(fx){return (fx.sections||[]).reduce(function(a,s){return a.concat(s.matches||[]);},[]);}

  /* ---------------- Hero countdown ---------------- */
  var cdTimer=null;
  function renderCountdown(fx){
    var all=flatten(fx).filter(function(m){return m.status!=="finished"&&m.kickoff;});
    all.sort(function(a,b){return new Date(a.kickoff)-new Date(b.kickoff);});
    var next=all[0]; if(!next)return;
    var box=$("[data-wc-countdown]"), lab=$("[data-wc-next]");
    if(lab){lab.hidden=false; lab.innerHTML="Next: <b>"+flag(next.home_team)+" "+esc(next.home_team)+" vs "+esc(next.away_team)+" "+flag(next.away_team)+"</b> · "+esc(stageName(next.stage));}
    if(!box)return; box.hidden=false;
    function tick(){
      var diff=new Date(next.kickoff)-new Date();
      if(diff<=0){clearInterval(cdTimer); box.hidden=true; if(lab)lab.innerHTML="Next: <b>"+esc(next.home_team)+" vs "+esc(next.away_team)+"</b> · kicking off now";return;}
      var s=Math.floor(diff/1000);
      setCd(box,"d",Math.floor(s/86400)); setCd(box,"h",Math.floor(s%86400/3600));
      setCd(box,"m",Math.floor(s%3600/60)); setCd(box,"s",s%60);
    }
    tick(); cdTimer=setInterval(tick,1000);
  }
  function setCd(box,k,v){var n=box.querySelector('[data-cd="'+k+'"]'); if(n)n.textContent=v<10?"0"+v:v;}

  /* ---------------- Match schedule (the future-matches board) ---------------- */
  var SCHED=null, CURRENT="upcoming";
  function fixtureRow(m){
    var finished=m.status==="finished", live=m.status==="live";
    var mid = live?'<span class="wc-fx-live">LIVE</span>'
      : finished?'<span class="wc-fx-score">'+(m.home_score==null?"–":m.home_score)+" : "+(m.away_score==null?"–":m.away_score)+'</span>'
      : '<span class="wc-fx-time">'+esc(timeLabel(m.kickoff))+'</span>';
    var sub = finished?'<span class="wc-fx-tag">Full time</span>'
      : '<span class="wc-fx-venue">'+esc(m.venue||m.host_city||"")+'</span>';
    var tag = m.group?('Group '+esc(m.group)):esc(stageName(m.stage));
    return '<div class="wc-fixture">'+
      '<div class="wc-fx-team home"><span class="wc-fx-flag">'+flag(m.home_team)+'</span><span class="wc-fx-name">'+esc(m.home_team)+'</span></div>'+
      '<div class="wc-fx-mid">'+mid+'<span class="wc-fx-when">'+tag+'</span>'+sub+'</div>'+
      '<div class="wc-fx-team away"><span class="wc-fx-name">'+esc(m.away_team)+'</span><span class="wc-fx-flag">'+flag(m.away_team)+'</span></div>'+
      '</div>';
  }
  function selectMatches(filter){
    var all=flatten(SCHED);
    if(filter==="group_stage")return all.filter(function(m){return m.stage==="group_stage";});
    if(filter==="knockouts")return all.filter(function(m){return isKnockout(m.stage);});
    if(filter==="results")return all.filter(function(m){return m.status==="finished";}).reverse();
    return all.filter(function(m){return m.status!=="finished";}); // upcoming
  }
  function renderSchedule(filter){
    var el=$("[data-wc-schedule]"); if(!el||!SCHED)return;
    CURRENT=filter;
    var list=selectMatches(filter);
    if(!list.length){el.innerHTML='<div class="wc-empty">No matches in this view yet.</div>';return;}
    // group by calendar day
    var days=[],map={};
    list.forEach(function(m){
      var d=dayKey(m.kickoff,m.date); var key=d?d.toISOString().slice(0,10):"TBD";
      if(!map[key]){map[key]={label:d?dayLabel(d):"Date TBD",rows:[]};days.push(key);}
      map[key].rows.push(m);
    });
    if(filter==="results")days.reverse();
    el.innerHTML=days.map(function(k){
      var n=map[k].rows.length;
      return '<div class="wc-sched-day"><div class="wc-sched-daylabel">'+esc(map[k].label)+
        ' <span>· '+n+(n===1?" match":" matches")+'</span></div>'+
        map[k].rows.map(fixtureRow).join("")+'</div>';
    }).join("");
  }
  function wireFilters(){
    var bar=$("[data-wc-filter]"); if(!bar)return;
    bar.addEventListener("click",function(e){
      var btn=e.target.closest(".wc-seg-btn"); if(!btn)return;
      bar.querySelectorAll(".wc-seg-btn").forEach(function(b){b.classList.toggle("is-active",b===btn);});
      renderSchedule(btn.getAttribute("data-filter"));
    });
  }

  /* ---------------- Knockout predictions ---------------- */
  function renderMatches(data){
    var el=$("[data-wc-matches]"); if(!el||!data.matches)return;
    el.innerHTML=data.matches.map(function(m){
      var r=m.result_90||{},adv=m.to_advance||{},names=Object.keys(adv);
      var advTxt=names.map(function(n){return esc(n)+" "+pct(adv[n]);}).join(" · ");
      return '<article class="snap-card wc-card">'+
        '<div class="wc-card-top"><span class="wc-stage">'+esc(stageName(m.stage))+'</span><span class="wc-viral">🔥 '+esc(m.interest_score)+'</span></div>'+
        '<div class="wc-teams"><span>'+flag(m.home_team)+' '+esc(m.home_team)+'</span><span class="wc-vs">vs</span><span>'+esc(m.away_team)+' '+flag(m.away_team)+'</span></div>'+
        '<div class="wc-bar-label">90-minute result · kickoff '+esc(m.kickoff_label||"TBD")+'</div>'+
        '<div class="mr-bar"><i class="home" style="width:'+pct(r.team1)+'"></i><i class="draw" style="width:'+pct(r.draw)+'"></i><i class="away" style="width:'+pct(r.team2)+'"></i></div>'+
        '<div class="mr-pcts"><span class="home">'+pct(r.team1)+'</span><span class="draw">DRAW '+pct(r.draw)+'</span><span class="away">'+pct(r.team2)+'</span></div>'+
        (advTxt?'<div class="wc-advance"><span>To advance</span><b>'+advTxt+'</b></div>':'')+
        '</article>';
    }).join("");
  }
  function setStage(data){
    var el=$("[data-wc-stage]");
    if(el&&data.matches&&data.matches[0])el.textContent=stageName(data.matches[0].stage);
    var up=$("[data-wc-upcoming]");
    if(up&&data.matches)up.textContent=data.matches.length+" upcoming fixtures";
  }

  /* ---------------- Road-to-final bracket ---------------- */
  function renderBracket(data){
    var el=$("[data-wc-bracket]"); if(!el)return;
    var preds=(data&&data.matches)||[];
    var cols=[["round_of_32","Round of 32"],["round_of_16","Round of 16"],
              ["quarterfinals","Quarter-finals"],["semifinals","Semi-finals"],["final","Final"]];
    var html=cols.map(function(c){
      var ties=preds.filter(function(m){return m.stage===c[0];}).slice(0,8);
      if(!ties.length)return "";
      return '<div class="wc-bracket-col"><h4>'+esc(c[1])+'</h4>'+ties.map(function(m){
        var adv=m.to_advance||{},h=adv[m.home_team]||0,a=adv[m.away_team]||0;
        return '<div class="wc-bracket-tie">'+
          '<div class="wc-bt-row'+(h>=a?' win':'')+'"><span><span class="wc-fx-flag">'+flag(m.home_team)+'</span><span class="wc-fx-name">'+esc(m.home_team)+'</span></span><b class="wc-bt-prob">'+pct(h)+'</b></div>'+
          '<div class="wc-bt-row'+(a>h?' win':'')+'"><span><span class="wc-fx-flag">'+flag(m.away_team)+'</span><span class="wc-fx-name">'+esc(m.away_team)+'</span></span><b class="wc-bt-prob">'+pct(a)+'</b></div>'+
          '</div>';
      }).join("")+'</div>';
    }).join("");
    el.innerHTML=html||'<div class="wc-empty">Bracket will populate as knockout ties are set.</div>';
  }

  /* ---------------- Qualifiers ---------------- */
  function renderQualifiers(data){
    var el=$("[data-wc-qualifiers]"); if(!el||!data.matches)return;
    el.innerHTML=data.matches.map(function(m){
      var q=(m.qualification||{}).group_qualification_probability||{},names=Object.keys(q);
      var lead=names.sort(function(a,b){return q[b]-q[a];})[0];
      return '<li class="wc-qual-row"><div><span class="lr-league">'+esc(m.competition_type==="world_cup_qualifier"?"World Cup Qualifier":"Qualifier")+'</span>'+
        '<b>'+flag(m.home_team)+' '+esc(m.home_team)+' vs '+esc(m.away_team)+' '+flag(m.away_team)+'</b></div>'+
        (lead?'<span class="wc-qual-prob">'+esc(lead)+' '+pct(q[lead])+'</span>':'')+'</li>';
    }).join("");
  }

  /* ---------------- Standings ---------------- */
  function renderStandings(data){
    var el=$("[data-wc-standings]"); if(!el||!data.groups)return;
    var keys=Object.keys(data.groups);
    if(!keys.length){el.innerHTML='<div class="wc-empty">Group tables appear once matches are played.</div>';return;}
    el.innerHTML=keys.map(function(g){
      var rows=data.groups[g].map(function(t,i){
        return '<tr'+(i<2?' class="qualifies"':'')+'><td>'+flag(t.team)+' '+esc(t.team)+'</td><td>'+t.played+'</td><td>'+(t.gd>=0?"+":"")+t.gd+'</td><td>'+t.points+'</td></tr>';
      }).join("");
      return '<div class="snap-card"><table class="wc-table"><thead><tr><th>'+esc(g)+'</th><th>P</th><th>GD</th><th>Pts</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
    }).join("");
  }

  function warn(){}
  function init(){
    wireFilters();
    get("worldcup-fixtures.json").then(function(d){
      SCHED=d; renderStats(d); renderCountdown(d); renderSchedule("upcoming");
    }).catch(function(){
      var el=$("[data-wc-schedule]"); if(el)el.innerHTML='<div class="wc-empty">Schedule is being prepared — check back shortly.</div>';
    });
    get("worldcup-predictions.json").then(function(d){renderMatches(d);setStage(d);renderBracket(d);}).catch(warn);
    get("worldcup-qualifiers.json").then(renderQualifiers).catch(warn);
    get("worldcup-standings.json").then(renderStandings).catch(warn);
  }
  if(document.readyState!=="loading")init(); else document.addEventListener("DOMContentLoaded",init);
})();
