/* sports-worldcup.js — hydrate the World Cup page from worldcup*.json. */
(function () {
  "use strict";
  var BASE = "/assets/data/sports/";
  var FLAG = {
    Argentina:"🇦🇷",Norway:"🇳🇴",Brazil:"🇧🇷",Japan:"🇯🇵",France:"🇫🇷",Senegal:"🇸🇳",
    England:"🏴",Mexico:"🇲🇽",Spain:"🇪🇸",Croatia:"🇭🇷",Germany:"🇩🇪",Morocco:"🇲🇦",
    Portugal:"🇵🇹",USA:"🇺🇸",Netherlands:"🇳🇱",Ecuador:"🇪🇨",Italy:"🇮🇹",Colombia:"🇨🇴"
  };
  function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
  function flag(t){return FLAG[t]||"⚽";}
  function pct(v){return Math.round((v||0)*100)+"%";}
  function get(n){return fetch(BASE+n,{cache:"no-store"}).then(function(r){if(!r.ok)throw 0;return r.json();});}
  function stageName(s){return (s||"").replace(/_/g," ").replace(/\b\w/g,function(c){return c.toUpperCase();});}

  function renderMatches(data){
    var el=document.querySelector("[data-wc-matches]"); if(!el||!data.matches)return;
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
  function renderQualifiers(data){
    var el=document.querySelector("[data-wc-qualifiers]"); if(!el||!data.matches)return;
    el.innerHTML=data.matches.map(function(m){
      var q=(m.qualification||{}).group_qualification_probability||{},names=Object.keys(q);
      var lead=names.sort(function(a,b){return q[b]-q[a];})[0];
      return '<li class="wc-qual-row"><div><span class="lr-league">'+esc(m.competition_type==="world_cup_qualifier"?"World Cup Qualifier":"Qualifier")+'</span>'+
        '<b>'+flag(m.home_team)+' '+esc(m.home_team)+' vs '+esc(m.away_team)+' '+flag(m.away_team)+'</b></div>'+
        (lead?'<span class="wc-qual-prob">'+esc(lead)+' '+pct(q[lead])+'</span>':'')+'</li>';
    }).join("");
  }
  function renderStandings(data){
    var el=document.querySelector("[data-wc-standings]"); if(!el||!data.groups)return;
    el.innerHTML=Object.keys(data.groups).map(function(g){
      var rows=data.groups[g].map(function(t){return '<tr><td>'+flag(t.team)+' '+esc(t.team)+'</td><td>'+t.played+'</td><td>'+(t.gd>=0?"+":"")+t.gd+'</td><td>'+t.points+'</td></tr>';}).join("");
      return '<table class="wc-table"><thead><tr><th>'+esc(g)+'</th><th>P</th><th>GD</th><th>Pts</th></tr></thead><tbody>'+rows+'</tbody></table>';
    }).join("");
  }
  function setStage(data){
    var el=document.querySelector("[data-wc-stage]");
    if(el&&data.matches&&data.matches[0])el.textContent=stageName(data.matches[0].stage);
  }
  function warn(){}
  function init(){
    get("worldcup-predictions.json").then(function(d){renderMatches(d);setStage(d);}).catch(warn);
    get("worldcup-qualifiers.json").then(renderQualifiers).catch(warn);
    get("worldcup-standings.json").then(renderStandings).catch(warn);
  }
  if(document.readyState!=="loading")init(); else document.addEventListener("DOMContentLoaded",init);
})();
