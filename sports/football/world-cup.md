---
layout: sports
title: "FIFA World Cup 2026 — AI Predictions & Full Schedule"
permalink: /sports/football/world-cup/
description: "FIFA World Cup 2026: full match schedule with kickoff times, AI predictions for every knockout tie, who-advances odds, live group standings and qualifier classification. Updated continuously."
---

<div class="wc">

{% include sports/worldcup-hero.html %}

{% include sports/worldcup-stats.html %}

<section class="sports-section" id="wc-schedule">
  {% include sports/worldcup-schedule.html %}
</section>

<section class="sports-section" id="wc-knockout">
  <h2 class="sports-section-title">Knockout Predictions</h2>
  {% include sports/worldcup-matches.html %}
</section>

<section class="sports-section" id="wc-bracket">
  <h2 class="sports-section-title">Road to the Final</h2>
  {% include sports/worldcup-bracket.html %}
</section>

<div class="sports-snapshot" style="grid-template-columns:1.2fr 1fr">
  <section class="sports-section" id="wc-standings" style="margin-top:0">
    <h2 class="sports-section-title">Group Standings — Live</h2>
    {% include sports/worldcup-standings.html %}
  </section>
  <section class="sports-section" id="wc-qualifiers" style="margin-top:0">
    <h2 class="sports-section-title">Qualifiers — Road to the World Cup</h2>
    {% include sports/worldcup-qualifiers.html %}
  </section>
</div>

{% include sports/disclaimer.html %}
</div>
<script src="{{ '/assets/js/sports-worldcup.js' | relative_url }}" defer></script>
