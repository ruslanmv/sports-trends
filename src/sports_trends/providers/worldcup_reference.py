"""Reference tables for the 2026 FIFA World Cup (48 teams, 16 host cities).

Single source of truth for national-team Elo seeds, confederations, flag emoji
and host-city metadata. Shared by the offline mock, the live providers and the
prediction feature so every qualified nation renders with accurate data even
when no keyed API is configured.

Sources: public-domain FIFA / Elo rating context (https://www.eloratings.net)
and the FIFA World Cup 2026 host-city list. Values are approximate seeds used
only for the offline/no-key prediction fallback.
"""

from __future__ import annotations

HOSTS_2026 = {"USA", "Canada", "Mexico"}

# Approximate national-team Elo seeds (relative strength) for all 48 finalists.
# Used only for the offline / no-key prediction fallback.
NATIONAL_ELO: dict[str, float] = {
    # CONMEBOL
    "Argentina": 2105, "Brazil": 2050, "Uruguay": 1915, "Colombia": 1900,
    "Ecuador": 1820, "Paraguay": 1760,
    # UEFA
    "France": 2080, "Spain": 2040, "England": 2030, "Portugal": 2000,
    "Netherlands": 1985, "Germany": 1975, "Italy": 1965, "Croatia": 1905,
    "Belgium": 1955, "Switzerland": 1860, "Austria": 1855, "Norway": 1830,
    "Sweden": 1820, "Scotland": 1800, "Turkey": 1830, "Czech Republic": 1815,
    "Bosnia & Herzegovina": 1760,
    # CAF
    "Morocco": 1890, "Senegal": 1845, "Ivory Coast": 1800, "Algeria": 1800,
    "Egypt": 1810, "Tunisia": 1760, "Ghana": 1760, "Cape Verde": 1690,
    "South Africa": 1730, "DR Congo": 1730,
    # AFC
    "Japan": 1850, "South Korea": 1810, "Iran": 1800, "Australia": 1780,
    "Saudi Arabia": 1700, "Qatar": 1700, "Uzbekistan": 1680, "Iraq": 1660,
    "Jordan": 1620,
    # CONCACAF
    "USA": 1825, "Mexico": 1815, "Canada": 1770, "Panama": 1700,
    "Haiti": 1600, "Curaçao": 1590,
    # OFC
    "New Zealand": 1660,
}

CONFEDERATION: dict[str, str] = {
    # CONMEBOL
    "Argentina": "CONMEBOL", "Brazil": "CONMEBOL", "Uruguay": "CONMEBOL",
    "Colombia": "CONMEBOL", "Ecuador": "CONMEBOL", "Paraguay": "CONMEBOL",
    # UEFA
    "France": "UEFA", "Spain": "UEFA", "England": "UEFA", "Portugal": "UEFA",
    "Netherlands": "UEFA", "Germany": "UEFA", "Italy": "UEFA", "Croatia": "UEFA",
    "Belgium": "UEFA", "Switzerland": "UEFA", "Austria": "UEFA", "Norway": "UEFA",
    "Sweden": "UEFA", "Scotland": "UEFA", "Turkey": "UEFA", "Czech Republic": "UEFA",
    "Bosnia & Herzegovina": "UEFA",
    # CAF
    "Morocco": "CAF", "Senegal": "CAF", "Ivory Coast": "CAF", "Algeria": "CAF",
    "Egypt": "CAF", "Tunisia": "CAF", "Ghana": "CAF", "Cape Verde": "CAF",
    "South Africa": "CAF", "DR Congo": "CAF", "Nigeria": "CAF",
    # AFC
    "Japan": "AFC", "South Korea": "AFC", "Iran": "AFC", "Australia": "AFC",
    "Saudi Arabia": "AFC", "Qatar": "AFC", "Uzbekistan": "AFC", "Iraq": "AFC",
    "Jordan": "AFC",
    # CONCACAF
    "USA": "CONCACAF", "Mexico": "CONCACAF", "Canada": "CONCACAF",
    "Panama": "CONCACAF", "Haiti": "CONCACAF", "Curaçao": "CONCACAF",
    # OFC
    "New Zealand": "OFC",
}

# Flag emoji for every finalist (and a few qualifier nations) — keeps the UI
# rich without bundling image assets. Mirrored in assets/js/sports-worldcup.js.
FLAG: dict[str, str] = {
    "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Uruguay": "🇺🇾", "Colombia": "🇨🇴",
    "Ecuador": "🇪🇨", "Paraguay": "🇵🇾", "France": "🇫🇷", "Spain": "🇪🇸",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Portugal": "🇵🇹", "Netherlands": "🇳🇱", "Germany": "🇩🇪",
    "Italy": "🇮🇹", "Croatia": "🇭🇷", "Belgium": "🇧🇪", "Switzerland": "🇨🇭",
    "Austria": "🇦🇹", "Norway": "🇳🇴", "Sweden": "🇸🇪", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Turkey": "🇹🇷", "Czech Republic": "🇨🇿", "Bosnia & Herzegovina": "🇧🇦",
    "Morocco": "🇲🇦", "Senegal": "🇸🇳", "Ivory Coast": "🇨🇮", "Algeria": "🇩🇿",
    "Egypt": "🇪🇬", "Tunisia": "🇹🇳", "Ghana": "🇬🇭", "Cape Verde": "🇨🇻",
    "South Africa": "🇿🇦", "DR Congo": "🇨🇩", "Nigeria": "🇳🇬", "Japan": "🇯🇵",
    "South Korea": "🇰🇷", "Iran": "🇮🇷", "Australia": "🇦🇺", "Saudi Arabia": "🇸🇦",
    "Qatar": "🇶🇦", "Uzbekistan": "🇺🇿", "Iraq": "🇮🇶", "Jordan": "🇯🇴",
    "USA": "🇺🇸", "Mexico": "🇲🇽", "Canada": "🇨🇦", "Panama": "🇵🇦",
    "Haiti": "🇭🇹", "Curaçao": "🇨🇼", "New Zealand": "🇳🇿",
}

# 16 host cities → country (used to mark neutral venues / host advantage).
HOST_CITY_COUNTRY: dict[str, str] = {
    "Atlanta": "USA", "Boston": "USA", "Dallas": "USA", "Houston": "USA",
    "Kansas City": "USA", "Los Angeles": "USA", "Miami": "USA",
    "New York/New Jersey": "USA", "Philadelphia": "USA",
    "San Francisco Bay Area": "USA", "Seattle": "USA",
    "Toronto": "Canada", "Vancouver": "Canada",
    "Mexico City": "Mexico", "Guadalajara": "Mexico", "Monterrey": "Mexico",
}


def confederation_of(team: str) -> str:
    return CONFEDERATION.get(team, "INTERNATIONAL")


def host_country_for_venue(venue: str | None) -> str:
    """Best-effort host country for an OpenFootball ground string."""
    if not venue:
        return "USA"
    for city, country in HOST_CITY_COUNTRY.items():
        if city.split("/")[0].split(" (")[0] in venue or city in venue:
            return country
    return "USA"
