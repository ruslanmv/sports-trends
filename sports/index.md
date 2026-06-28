---
layout: sports
title: "Ruslan Magana Sports Intelligence"
permalink: /
description: "AI predictions, live results, and trending games updated every 30 minutes."
---

{% include sports/hero.html %}
{% include sports/stats-cards.html %}
{% include sports/status-bar.html %}
{% include sports/worldcup-banner.html %}

<section class="sports-section" id="snapshot">
  <h2 class="sports-section-title">Today&rsquo;s Sports Snapshot</h2>
  <div class="sports-snapshot">
    {% include sports/tomorrow-top-matches.html %}
    {% include sports/live-results.html %}
    {% include sports/trending-matches.html %}
    {% include sports/worldcup-minicard.html %}
  </div>
</section>

<section class="sports-section" id="explore">
  <h2 class="sports-section-title">Explore Sports</h2>
  {% include sports/sport-category-grid.html %}
</section>

{% include sports/disclaimer.html %}
