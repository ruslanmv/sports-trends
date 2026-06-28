---
layout: sports
title: "FIFA World Cup 2026 — AI Predictions"
permalink: /sports/football/world-cup/
description: "AI predictions for the FIFA World Cup 2026 — knockout games, to-advance odds, group standings, and qualifier classification, updated daily."
---

{% include sports/worldcup-hero.html %}

<section class="sports-section" id="wc-knockout">
  <h2 class="sports-section-title">Knockout Predictions</h2>
  {% include sports/worldcup-matches.html %}
</section>

<div class="sports-snapshot" style="grid-template-columns:1.2fr 1fr">
  <section class="sports-section" id="wc-qualifiers" style="margin-top:0">
    <h2 class="sports-section-title">Qualifiers — Road to the World Cup</h2>
    {% include sports/worldcup-qualifiers.html %}
  </section>
  <section class="sports-section" id="wc-standings" style="margin-top:0">
    <h2 class="sports-section-title">Group Standings</h2>
    {% include sports/worldcup-standings.html %}
  </section>
</div>

{% include sports/disclaimer.html %}
<script src="/assets/js/sports-worldcup.js" defer></script>
