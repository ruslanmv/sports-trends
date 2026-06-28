/* sports-predict.js — prediction-first sport page (hero + status + featured +
   master table), with seasonal Mundial 2026 mode for football. JSON-driven. */
(function () {
  "use strict";
  var root = document.querySelector("[data-pred]");
  if (!root) return;
  var SPORT = root.getAttribute("data-pred");
  var meta = document.querySelector('meta[name="sports-base"]');
  var BASE = ((meta ? meta.content : "/").replace(/\/$/, "")) + "/assets/data/sports/";

  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function pct(v){return Math.round((v||0)*100)+"%";}
  function get(n){return fetch(BASE+n,{cache:"no-store"}).then(function(r){if(!r.ok)throw 0;return r.json();});}
  function title(s){return (s||"").replace(/_/g," ").replace(/\b\w/g,function(c){return c.toUpperCase();});}
  function mono(name){return (name||"").split(/\s+/).map(function(w){return w[0];}).join("").slice(0,2).toUpperCase();}
  function cleanPick(s){return (s||"").replace(/^AI:\s*/,"");}

  function clubMatch(m){
    var p=m.probabilities||{};
    return {id:m.match_id,home:m.home_team,away:m.away_team,comp:m.league,stage:"",
      kickoff:m.kickoff_label||"TBD",h:p.home_win||0,d:p.draw||0,a:p.away_win||0,
      pick:cleanPick(m.prediction_label),conf:Math.round((m.confidence||0)*100),
      interest:m.interest_score||0,adv:null,reasons:m.explanation||[],wc:false};
  }
  function wcMatch(m){
    var p=m.prediction||{};
    return {id:m.match_id,home:m.home_team,away:m.away_team,comp:"Mundial 2026",stage:title(m.stage),
      kickoff:m.kickoff_label||"TBD",h:p.home_win||0,d:p.draw||0,a:p.away_win||0,
      pick:cleanPick(p.ai_pick),conf:p.confidence||0,interest:m.interest_score||0,
      adv:{home:p.home_to_advance,away:p.away_to_advance},reasons:[],wc:true};
  }

  var STATE={matches:[],wc:false,tab:"All",sort:"kickoff",q:""};

  Promise.all([
    get("predictions.json").catch(function(){return {matches:[]};}),
    SPORT==="football"?get("football-config.json").catch(function(){return {};}):Promise.resolve({}),
    SPORT==="football"?get("world-cup-2026.json").catch(function(){return {matches:[]};}):Promise.resolve({matches:[]})
  ]).then(function(res){
    var preds=res[0],cfg=res[1],wc=res[2];
    var club=(preds.matches||[]).filter(function(m){return SPORT==="all"||m.sport===SPORT;}).map(clubMatch);
    var wcm=(wc.matches||[]).map(wcMatch);
    STATE.wc = SPORT==="football" && cfg.page_mode==="world_cup_2026" && wcm.length>0;
    STATE.matches = STATE.wc ? wcm.concat(club) : club;
    STATE.tab = (cfg.default_tab)|| "All";

    applyConfig(cfg);
    renderStatus(cfg);
    renderMundial(wc, wcm);
    renderTabs();
    renderFeatured();
    renderTable();
    wireControls();
  });

  function applyConfig(cfg){
    if(SPORT!=="football"||!cfg.headline) return;
    set("[data-hero-eyebrow]",cfg.eyebrow); set("[data-hero-title]",cfg.headline); set("[data-hero-sub]",cfg.subtitle);
  }
  function set(sel,txt){var e=document.querySelector(sel); if(e&&txt) e.textContent=txt;}

  function renderStatus(cfg){
    var leagues={}; STATE.matches.forEach(function(m){leagues[m.comp]=1;});
    set("[data-ps-upcoming]",String(STATE.matches.length));
    set("[data-ps-leagues]",String(Object.keys(leagues).length));
    var mode=document.querySelector("[data-ps-mode]");
    if(mode) mode.textContent = STATE.wc ? "Mundial 2026" : "Tomorrow";
  }

  function renderMundial(wc, wcm){
    var strip=document.querySelector("[data-mundial-strip]");
    if(!strip||!STATE.wc){return;}
    strip.hidden=false;
    set("[data-pm-round]", title(wc.stage)||"Round of 32");
    set("[data-pm-count]", wcm.length+" knockout matches");
    var fav=wcm.slice().sort(function(a,b){return (b.adv.home||0)-(a.adv.home||0);})[0];
    if(fav) set("[data-pm-fav]", fav.home+" "+pct(fav.adv.home));
    var upset=wcm.slice().sort(function(a,b){return Math.abs(a.adv.home-0.5)-Math.abs(b.adv.home-0.5);})[0];
    if(upset) set("[data-pm-upset]", upset.home+" vs "+upset.away);
  }

  function renderFeatured(){
    var pool = STATE.wc ? STATE.matches.filter(function(m){return m.wc;}) : STATE.matches;
    if(!pool.length) pool=STATE.matches;
    var m = pool.slice().sort(function(a,b){return b.interest-a.interest;})[0];
    if(!m) return;
    set("[data-pf-meta]", m.comp+(m.stage?" · "+m.stage:"")+" · "+m.kickoff);
    document.querySelector("[data-pf-home-crest]").textContent=mono(m.home);
    document.querySelector("[data-pf-away-crest]").textContent=mono(m.away);
    set("[data-pf-home]",m.home); set("[data-pf-away]",m.away);
    document.querySelector("[data-pf-bar-h]").style.width=pct(m.h);
    document.querySelector("[data-pf-bar-d]").style.width=pct(m.d);
    document.querySelector("[data-pf-bar-a]").style.width=pct(m.a);
    set("[data-pf-hp]",pct(m.h)); set("[data-pf-hl]",m.home.toUpperCase());
    set("[data-pf-dp]",pct(m.d));
    set("[data-pf-ap]",pct(m.a)); set("[data-pf-al]",m.away.toUpperCase());
    var adv=document.querySelector("[data-pf-advance]");
    if(m.adv && m.adv.home!=null){adv.hidden=false; adv.innerHTML="<b>To advance:</b> "+esc(m.home)+" "+pct(m.adv.home)+" · "+esc(m.away)+" "+pct(m.adv.away);}
    else adv.hidden=true;
    set("[data-pf-pick]","AI Pick: "+m.pick);
    set("[data-pf-conf]",m.conf+"/100");
    var rb=document.querySelector("[data-pf-reason]");
    rb.innerHTML=(m.reasons.length?m.reasons:["Win probabilities from a calibrated, sport-optimized model.","Ranked by global interest and model confidence."]).map(function(r){return "<li>"+esc(r)+"</li>";}).join("");
  }

  function renderTabs(){
    var leagues=[]; var seen={};
    STATE.matches.forEach(function(m){if(!m.wc&&m.comp&&!seen[m.comp]){seen[m.comp]=1;leagues.push(m.comp);}});
    var tabs=["All"].concat(STATE.wc?["Mundial 2026"]:[]).concat(["Trending","Highest Confidence"]).concat(leagues.slice(0,4));
    var wrap=document.querySelector("[data-pt-tabs]");
    wrap.innerHTML=tabs.map(function(t){return '<button class="pt-tab'+(t===STATE.tab?" active":"")+'" data-tab="'+esc(t)+'">'+esc(t)+'</button>';}).join("");
    wrap.querySelectorAll(".pt-tab").forEach(function(b){b.addEventListener("click",function(){STATE.tab=b.getAttribute("data-tab");wrap.querySelectorAll(".pt-tab").forEach(function(x){x.classList.remove("active");});b.classList.add("active");renderTable();});});
  }

  function filtered(){
    var rows=STATE.matches.slice();
    if(STATE.tab==="Mundial 2026") rows=rows.filter(function(m){return m.wc;});
    else if(STATE.tab==="Trending") rows=rows.sort(function(a,b){return b.interest-a.interest;}).slice(0,8);
    else if(STATE.tab==="Highest Confidence") rows=rows.sort(function(a,b){return b.conf-a.conf;});
    else if(STATE.tab!=="All") rows=rows.filter(function(m){return m.comp===STATE.tab;});
    if(STATE.q){var q=STATE.q.toLowerCase();rows=rows.filter(function(m){return (m.home+" "+m.away+" "+m.comp).toLowerCase().indexOf(q)>-1;});}
    if(STATE.sort==="kickoff") rows.sort(function(a,b){return String(a.kickoff).localeCompare(String(b.kickoff));});
    else if(STATE.sort==="confidence") rows.sort(function(a,b){return b.conf-a.conf;});
    else if(STATE.sort==="interest") rows.sort(function(a,b){return b.interest-a.interest;});
    return rows;
  }

  function renderTable(){
    var rows=filtered(); var showAdv=STATE.wc;
    var head='<div class="pt-row pt-th">'+
      '<span class="c-match">Match</span><span class="c-comp">Competition</span>'+
      (showAdv?'<span class="c-stage">Stage</span>':'')+
      '<span class="c-time">Kickoff</span><span class="c-pick">AI Pick</span>'+
      '<span class="c-p">Home</span><span class="c-p">Draw</span><span class="c-p">Away</span>'+
      (showAdv?'<span class="c-adv">To Advance</span>':'')+
      '<span class="c-conf">Confidence</span><span class="c-det"></span></div>';
    var body=rows.map(function(m,i){
      var advTxt=m.adv&&m.adv.home!=null?(m.home+" "+pct(m.adv.home)):"—";
      return '<div class="pt-row" data-row="'+i+'">'+
        '<span class="c-match"><span class="pt-crest">'+esc(mono(m.home))+'</span>'+esc(m.home)+' <em>vs</em> '+esc(m.away)+'</span>'+
        '<span class="c-comp">'+esc(m.comp)+'</span>'+
        (showAdv?'<span class="c-stage">'+esc(m.stage||"—")+'</span>':'')+
        '<span class="c-time">'+esc(m.kickoff)+'</span>'+
        '<span class="c-pick">'+esc(m.pick||"—")+'</span>'+
        '<span class="c-p home">'+pct(m.h)+'</span><span class="c-p">'+pct(m.d)+'</span><span class="c-p">'+pct(m.a)+'</span>'+
        (showAdv?'<span class="c-adv">'+esc(advTxt)+'</span>':'')+
        '<span class="c-conf"><span class="conf-ring" style="--p:'+m.conf+'">'+m.conf+'/100</span></span>'+
        '<span class="c-det"><button class="pt-more" data-more="'+i+'" aria-label="Details">&#8250;</button></span>'+
        '</div>'+
        '<div class="pt-detail" data-detail="'+i+'" hidden><div class="ptd-inner">'+
          '<b>Why:</b> '+(m.reasons.length?esc(m.reasons.join(" ")):"Calibrated model probabilities, ranked by interest and confidence.")+
          '<div class="ptd-meta">Interest '+m.interest+'/100 · Kickoff '+esc(m.kickoff)+(m.adv&&m.adv.home!=null?' · To advance '+esc(m.home)+' '+pct(m.adv.home):'')+'</div>'+
        '</div></div>';
    }).join("");
    var t=document.querySelector("[data-pt-table]");
    t.className="pt-table"+(showAdv?" with-adv":"");
    t.innerHTML=head+(rows.length?body:'<div class="pt-empty">No matches for this filter.</div>');
    t.querySelectorAll(".pt-row[data-row]").forEach(function(r){
      r.addEventListener("click",function(){var i=r.getAttribute("data-row");var d=t.querySelector('[data-detail="'+i+'"]');if(d)d.hidden=!d.hidden;});
    });
  }

  function wireControls(){
    var s=document.querySelector("[data-pred-search]");
    if(s) s.addEventListener("input",function(){STATE.q=s.value;renderTable();});
    var so=document.querySelector("[data-pt-sort]");
    if(so) so.addEventListener("change",function(){STATE.sort=so.value;renderTable();});
    var rb=document.querySelector("[data-pf-reason-toggle]");
    if(rb) rb.addEventListener("click",function(){var b=document.querySelector("[data-pf-reason]");var open=b.hidden;b.hidden=!open;rb.setAttribute("aria-expanded",open?"true":"false");});
  }
})();
