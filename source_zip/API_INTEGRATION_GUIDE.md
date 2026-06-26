# API Integration Guide - Sports Prediction Platform

## Table of Contents

1. [API-Football Integration](#api-football-integration)
2. [Football-Data.org Integration](#football-dataorg-integration)
3. [StatsBomb Open Data](#statsbomb-open-data)
4. [Rate Limiting & Optimization](#rate-limiting--optimization)
5. [Error Handling & Retry Logic](#error-handling--retry-logic)
6. [Testing API Connections](#testing-api-connections)

---

## API-Football Integration

### Setup

```python
# api_integrations/api_football.py

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class APIFootballClient:
    """
    Client for API-Football (RapidAPI)
    Free Tier: 100 requests/day
    Docs: https://rapidapi.com/api-sports/api/api-football
    """
    
    BASE_URL = "https://api-football-v3.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'api-football-v3.p.rapidapi.com'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.request_count = 0
        self.limit_reset_time = None
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with error handling
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"API-Football request: {endpoint}")
            response = self.session.get(url, params=params, timeout=10)
            
            # Check rate limiting headers
            if 'X-RateLimit-requests-Remaining' in response.headers:
                remaining = int(response.headers['X-RateLimit-requests-Remaining'])
                logger.info(f"Remaining API calls: {remaining}/100")
                
                if remaining < 10:
                    logger.warning("⚠️ API quota running low!")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API-Football request failed: {e}")
            return {'errors': {'token': ['Token is missing']}}
    
    # ========== FIXTURES & MATCHES ==========
    
    def get_fixtures(self, league_id: int, season: int, 
                     status: str = None) -> List[Dict]:
        """
        Get fixtures for a league/season
        
        Args:
            league_id: 39=Premier League, 140=La Liga, 135=Serie A, etc.
            season: 2024, 2023, etc.
            status: 'NOT_STARTED', 'LIVE', 'FINISHED'
        
        Returns:
            List of fixture objects
        """
        params = {'league': league_id, 'season': season}
        if status:
            params['status'] = status
        
        response = self._make_request('fixtures', params)
        
        if 'response' in response:
            return response['response']
        return []
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """
        Get detailed match statistics
        Includes: possession, shots, passes, etc.
        """
        params = {'fixture': fixture_id}
        response = self._make_request('fixtures/statistics', params)
        
        if response.get('response'):
            return response['response']
        return {}
    
    def get_match_events(self, fixture_id: int) -> List[Dict]:
        """
        Get match events (goals, cards, substitutions)
        """
        params = {'fixture': fixture_id}
        response = self._make_request('fixtures/events', params)
        
        if response.get('response'):
            return response['response']
        return []
    
    def get_match_lineups(self, fixture_id: int) -> Dict:
        """
        Get team lineups for a match
        """
        params = {'fixture': fixture_id}
        response = self._make_request('fixtures/lineups', params)
        
        if response.get('response'):
            return response['response']
        return {}
    
    # ========== TEAM STATISTICS ==========
    
    def get_team_statistics(self, team_id: int, season: int, 
                           league_id: int) -> Dict:
        """
        Get team statistics for a season
        
        Returns: goals, xG, possession, form, etc.
        """
        params = {'team': team_id, 'season': season, 'league': league_id}
        response = self._make_request('teams/statistics', params)
        
        if response.get('response'):
            return response['response']
        return {}
    
    def get_team_info(self, team_id: int) -> Dict:
        """
        Get team information (name, venue, coach, etc.)
        """
        params = {'id': team_id}
        response = self._make_request('teams', params)
        
        if response.get('response'):
            return response['response'][0]
        return {}
    
    def get_team_season_statistics(self, team_id: int, season: int) -> Dict:
        """
        Comprehensive team statistics (all competitions)
        """
        params = {'team': team_id, 'season': season}
        response = self._make_request('teams/statistics', params)
        
        if response.get('response'):
            return response['response']
        return {}
    
    # ========== PLAYER DATA ==========
    
    def get_team_players(self, team_id: int) -> List[Dict]:
        """
        Get players in a team
        """
        params = {'team': team_id}
        response = self._make_request('players/squads', params)
        
        if response.get('response'):
            return response['response'][0].get('players', [])
        return []
    
    def get_player_statistics(self, player_id: int, season: int) -> List[Dict]:
        """
        Get player statistics for a season
        """
        params = {'player': player_id, 'season': season}
        response = self._make_request('players', params)
        
        if response.get('response'):
            return response['response']
        return []
    
    # ========== HEAD-TO-HEAD ==========
    
    def get_h2h_record(self, team_id_1: int, team_id_2: int, 
                      last_n: int = 10) -> List[Dict]:
        """
        Get head-to-head matches between two teams
        """
        params = {'h2h': f'{team_id_1}-{team_id_2}', 'last': last_n}
        response = self._make_request('fixtures/headtohead', params)
        
        if response.get('response'):
            return response['response']
        return []
    
    # ========== INJURIES & SUSPENSIONS ==========
    
    def get_player_injuries(self, league_id: int, season: int) -> List[Dict]:
        """
        Get injured players in a league
        """
        params = {'league': league_id, 'season': season}
        response = self._make_request('injuries', params)
        
        if response.get('response'):
            return response['response']
        return []

# Example Usage
if __name__ == "__main__":
    client = APIFootballClient(os.getenv('RAPIDAPI_KEY'))
    
    # Get Premier League fixtures
    fixtures = client.get_fixtures(league_id=39, season=2024, status='FINISHED')
    print(f"Found {len(fixtures)} fixtures")
    
    # Get Manchester City stats
    stats = client.get_team_statistics(team_id=50, season=2024, league_id=39)
    print(f"Manchester City stats: {stats}")
```

### Rate Limit Management

```python
# utils/rate_limiter.py

from functools import wraps
import time
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Implement rate limiting for API calls
    
    API-Football: 100 calls/day (roughly 1 call/14 minutes average)
    Football-Data: 10 calls/minute
    """
    
    def __init__(self, calls_per_day: int = 100):
        self.calls_per_day = calls_per_day
        self.min_interval = (24 * 3600) / calls_per_day  # Seconds between calls
        self.last_call_time = 0
    
    def wait_if_needed(self):
        """Block until safe to make next API call"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.info(f"Rate limit: waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def rate_limit(self, func: Callable) -> Callable:
        """Decorator to apply rate limiting"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
```

---

## Football-Data.org Integration

### Setup

```python
# api_integrations/football_data.py

import os
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FootballDataClient:
    """
    Client for Football-Data.org API
    Free Tier: 10 requests/minute
    Docs: https://www.football-data.org/
    
    Leagues:
    - 39: Premier League (England)
    - 140: La Liga (Spain)
    - 135: Serie A (Italy)
    - 78: Bundesliga (Germany)
    - 61: Ligue 1 (France)
    - 2014: World Cup
    - 2001: Champions League
    """
    
    BASE_URL = "https://www.football-data.org/api/v4"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {'X-Auth-Token': api_key}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"Football-Data request: {endpoint}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Football-Data request failed: {e}")
            return {}
    
    # ========== COMPETITIONS ==========
    
    def get_competitions(self) -> List[Dict]:
        """Get all available competitions"""
        response = self._make_request('competitions')
        return response.get('competitions', [])
    
    # ========== MATCHES ==========
    
    def get_matches(self, competition_id: int = None, 
                   status: str = 'FINISHED', limit: int = 100) -> List[Dict]:
        """
        Get matches with optional filtering
        
        Args:
            competition_id: Filter by competition (39=PL, 140=La Liga, etc.)
            status: 'SCHEDULED', 'LIVE', 'IN_PLAY', 'PAUSED', 'FINISHED'
            limit: Max results (10-100)
        """
        params = {'status': status, 'limit': limit}
        if competition_id:
            params['competitions'] = competition_id
        
        response = self._make_request('matches', params)
        return response.get('matches', [])
    
    def get_match(self, match_id: int) -> Dict:
        """Get detailed match info"""
        response = self._make_request(f'matches/{match_id}')
        return response.get('match', {})
    
    # ========== TEAMS ==========
    
    def get_teams(self, competition_id: int) -> List[Dict]:
        """Get all teams in a competition"""
        response = self._make_request(f'competitions/{competition_id}/teams')
        return response.get('teams', [])
    
    def get_team(self, team_id: int) -> Dict:
        """Get team details"""
        response = self._make_request(f'teams/{team_id}')
        return response
    
    def get_team_matches(self, team_id: int, limit: int = 50) -> List[Dict]:
        """Get team's historical matches"""
        params = {'limit': limit}
        response = self._make_request(f'teams/{team_id}/matches', params)
        return response.get('matches', [])
    
    # ========== STANDINGS ==========
    
    def get_standings(self, competition_id: int) -> Dict:
        """Get league table/standings"""
        response = self._make_request(f'competitions/{competition_id}/standings')
        return response
    
    # ========== SQUAD ==========
    
    def get_team_squad(self, team_id: int) -> List[Dict]:
        """Get team players"""
        response = self._make_request(f'teams/{team_id}')
        return response.get('squad', [])
    
    def get_player_matches(self, player_id: int) -> List[Dict]:
        """Get player's match history"""
        response = self._make_request(f'persons/{player_id}/matches')
        return response.get('matches', [])

# Example Usage
if __name__ == "__main__":
    client = FootballDataClient(os.getenv('FOOTBALL_DATA_KEY'))
    
    # Get Premier League matches
    matches = client.get_matches(competition_id=39, status='FINISHED', limit=50)
    print(f"Found {len(matches)} PL matches")
    
    # Get standings
    standings = client.get_standings(39)
    print(standings)
```

---

## StatsBomb Open Data

### Integration (No API Key Needed)

```python
# api_integrations/statsbomb.py

import json
import urllib.request
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class StatsbombClient:
    """
    Client for StatsBomb Open Data (GitHub)
    
    No authentication required!
    Data: Event-level data for 5000+ matches
    Repos: https://github.com/statsbomb/open-data
    
    Directory structure:
    /data/matches/{season}/{competition_id}.json
    /data/events/{season}/{match_id}.json
    """
    
    BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master"
    
    # Competition IDs
    COMPETITIONS = {
        '25': ('Premier League', 'England'),
        '11': ('La Liga', 'Spain'),
        '12': ('Serie A', 'Italy'),
        '9': ('Bundesliga', 'Germany'),
        '7': ('Ligue 1', 'France'),
        '37': ('World Cup', 'International'),
        '16': ('Champions League', 'International'),
        '2': ('Friendly', 'International'),
    }
    
    @staticmethod
    def _fetch_json(url: str) -> Optional[Dict]:
        """Fetch JSON from URL"""
        try:
            logger.info(f"Fetching: {url}")
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    @classmethod
    def get_matches(cls, season: int = 2023, 
                   competition_id: str = '25') -> List[Dict]:
        """
        Get all matches for a season/competition
        
        Args:
            season: 2023, 2022, 2021, etc.
            competition_id: '25'=Premier League, '11'=La Liga, etc.
        """
        url = f"{cls.BASE_URL}/data/matches/{season}/{competition_id}.json"
        return cls._fetch_json(url) or []
    
    @classmethod
    def get_match_events(cls, season: int, match_id: str) -> List[Dict]:
        """
        Get event-level data for a match
        
        Events include:
        - Passes, shots, dribbles, tackles, interceptions
        - Fouls, cards, substitutions, goal events
        - Each event has location, player, team, timestamp
        """
        url = f"{cls.BASE_URL}/data/events/{season}/{match_id}.json"
        return cls._fetch_json(url) or []
    
    @classmethod
    def calculate_team_xg(cls, match_events: List[Dict], 
                         team_id: int) -> float:
        """
        Calculate expected goals (xG) from event data
        
        xG = sum of shot probabilities
        """
        xg = 0.0
        
        for event in match_events:
            if event.get('type', {}).get('name') == 'Shot':
                if event.get('team', {}).get('id') == team_id:
                    # StatsBomb provides xG value in shot data
                    xg += event.get('shot', {}).get('expected_goals', 0)
        
        return round(xg, 2)
    
    @classmethod
    def get_team_passing_stats(cls, match_events: List[Dict], 
                              team_id: int) -> Dict:
        """
        Extract passing statistics from event data
        """
        passes = {'completed': 0, 'attempted': 0}
        
        for event in match_events:
            if event.get('type', {}).get('name') == 'Pass':
                if event.get('team', {}).get('id') == team_id:
                    passes['attempted'] += 1
                    if event.get('pass', {}).get('outcome') is None:
                        passes['completed'] += 1
        
        completion_rate = (passes['completed'] / passes['attempted'] * 100 
                          if passes['attempted'] > 0 else 0)
        
        return {
            'passes_completed': passes['completed'],
            'passes_attempted': passes['attempted'],
            'pass_completion_rate': round(completion_rate, 1)
        }
    
    @classmethod
    def get_team_possession(cls, match_events: List[Dict], 
                           team_ids: tuple) -> Dict:
        """
        Approximate possession from pass frequency
        """
        team_a_passes = 0
        team_b_passes = 0
        
        for event in match_events:
            if event.get('type', {}).get('name') == 'Pass':
                team_id = event.get('team', {}).get('id')
                if team_id == team_ids[0]:
                    team_a_passes += 1
                elif team_id == team_ids[1]:
                    team_b_passes += 1
        
        total = team_a_passes + team_b_passes
        team_a_possession = (team_a_passes / total * 100) if total > 0 else 0
        team_b_possession = (team_b_passes / total * 100) if total > 0 else 0
        
        return {
            'team_a_possession': round(team_a_possession, 1),
            'team_b_possession': round(team_b_possession, 1)
        }

# Example Usage
if __name__ == "__main__":
    # Get Premier League 2023 matches
    matches = StatsbombClient.get_matches(season=2023, competition_id='25')
    print(f"Found {len(matches)} PL matches")
    
    # Analyze first match
    if matches:
        match = matches[0]
        match_id = match['match_id']
        print(f"\nAnalyzing: {match['home_team']['name']} vs {match['away_team']['name']}")
        
        # Get events
        events = StatsbombClient.get_match_events(2023, str(match_id))
        
        # Calculate xG
        home_xg = StatsbombClient.calculate_team_xg(events, match['home_team']['id'])
        away_xg = StatsbombClient.calculate_team_xg(events, match['away_team']['id'])
        
        print(f"xG: {home_xg} - {away_xg}")
        
        # Get passing stats
        home_passes = StatsbombClient.get_team_passing_stats(events, match['home_team']['id'])
        print(f"Home passing: {home_passes}")
```

---

## Rate Limiting & Optimization

```python
# utils/api_coordinator.py

from functools import wraps
import time
from datetime import datetime, timedelta
from typing import Callable, Dict
import logging

logger = logging.getLogger(__name__)

class APICoordinator:
    """
    Coordinate API calls across multiple providers
    Ensure we stay within free tier rate limits
    """
    
    RATE_LIMITS = {
        'api_football': {
            'calls_per_day': 100,
            'reset_time': '00:00:00',  # UTC
        },
        'football_data': {
            'calls_per_minute': 10,
            'reset_time': 'every_minute',
        },
        'statsbomb': {
            'calls_per_second': 1,  # Be respectful
        }
    }
    
    def __init__(self):
        self.call_log: Dict[str, list] = {
            'api_football': [],
            'football_data': [],
            'statsbomb': []
        }
    
    def can_call(self, provider: str) -> bool:
        """Check if we're within rate limits for provider"""
        now = datetime.now()
        
        if provider == 'api_football':
            # Check daily limit
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            calls_today = len([
                c for c in self.call_log['api_football'] 
                if c > day_start
            ])
            return calls_today < self.RATE_LIMITS['api_football']['calls_per_day']
        
        elif provider == 'football_data':
            # Check per-minute limit
            minute_ago = now - timedelta(minutes=1)
            calls_this_minute = len([
                c for c in self.call_log['football_data'] 
                if c > minute_ago
            ])
            return calls_this_minute < self.RATE_LIMITS['football_data']['calls_per_minute']
        
        elif provider == 'statsbomb':
            # Check per-second limit (generous since no auth needed)
            second_ago = now - timedelta(seconds=1)
            calls_this_second = len([
                c for c in self.call_log['statsbomb'] 
                if c > second_ago
            ])
            return calls_this_second < 5  # Be conservative
        
        return False
    
    def log_call(self, provider: str):
        """Log API call for rate limiting"""
        self.call_log[provider].append(datetime.now())
        
        # Cleanup old entries
        cutoff = datetime.now() - timedelta(hours=25)
        self.call_log[provider] = [c for c in self.call_log[provider] if c > cutoff]
    
    def wait_until_available(self, provider: str, max_wait: int = 3600):
        """Wait until safe to make next API call"""
        start = time.time()
        
        while not self.can_call(provider):
            elapsed = time.time() - start
            if elapsed > max_wait:
                logger.error(f"Rate limit exceeded for {provider}")
                raise Exception(f"Rate limit exceeded: {provider}")
            
            sleep_time = min(60, max_wait - elapsed)
            logger.info(f"Rate limit: sleeping {sleep_time}s for {provider}")
            time.sleep(sleep_time)
        
        self.log_call(provider)

# Priority-based data fetching
class SmartDataFetcher:
    """
    Intelligently fetch data using free APIs
    Strategy: Use StatsBomb first (no rate limit), then Football-Data, then API-Football
    """
    
    def __init__(self, coordinator: APICoordinator, 
                 api_football_client, football_data_client):
        self.coordinator = coordinator
        self.api_football = api_football_client
        self.football_data = football_data_client
    
    def get_match_data(self, match_date: datetime, 
                      home_team: str, away_team: str) -> Dict:
        """
        Get complete match data using optimal API combination
        """
        data = {}
        
        # Try StatsBomb first (no rate limits)
        statsbomb_data = self._get_statsbomb_data(home_team, away_team, match_date)
        if statsbomb_data:
            data.update(statsbomb_data)
        
        # Fill gaps with Football-Data.org
        if not data.get('standings'):
            football_data = self._get_football_data(home_team, away_team)
            data.update(football_data)
        
        # Use API-Football sparingly for real-time data
        if not data.get('lineups'):
            api_football_data = self._get_api_football(home_team, away_team)
            data.update(api_football_data)
        
        return data
    
    def _get_statsbomb_data(self, home_team: str, away_team: str, 
                           match_date: datetime) -> Dict:
        """Fetch from StatsBomb (best event-level data)"""
        # Implementation depends on finding match by team names
        return {}
    
    def _get_football_data(self, home_team: str, away_team: str) -> Dict:
        """Fetch from Football-Data.org"""
        self.coordinator.wait_until_available('football_data')
        # Fetch data
        return {}
    
    def _get_api_football(self, home_team: str, away_team: str) -> Dict:
        """Fetch from API-Football (use sparingly)"""
        self.coordinator.wait_until_available('api_football')
        # Fetch data
        return {}
```

---

## Error Handling & Retry Logic

```python
# utils/retry_handler.py

import logging
import time
from functools import wraps
from typing import Callable, Any
import requests

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, 
                       base_delay: int = 1,
                       exponential_base: float = 2.0) -> Callable:
    """
    Retry decorator with exponential backoff
    
    Args:
        max_retries: Number of retry attempts
        base_delay: Initial delay in seconds
        exponential_base: Multiplier for each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except (requests.exceptions.ConnectionError,
                       requests.exceptions.Timeout,
                       requests.exceptions.RequestException) as e:
                    
                    if attempt == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
                    
                    delay = base_delay * (exponential_base ** attempt)
                    logger.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed. "
                                 f"Retrying in {delay}s: {e}")
                    time.sleep(delay)
        
        return wrapper
    return decorator

# Example usage
class RobustAPIClient:
    @retry_with_backoff(max_retries=3, base_delay=2)
    def fetch_with_retry(self, url: str):
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
```

---

## Testing API Connections

```python
# tests/test_api_connections.py

import unittest
import os
from dotenv import load_dotenv
from api_integrations.api_football import APIFootballClient
from api_integrations.football_data import FootballDataClient
from api_integrations.statsbomb import StatsbombClient

load_dotenv()

class TestAPIConnections(unittest.TestCase):
    """Test API connectivity and data quality"""
    
    def setUp(self):
        self.api_football = APIFootballClient(os.getenv('RAPIDAPI_KEY'))
        self.football_data = FootballDataClient(os.getenv('FOOTBALL_DATA_KEY'))
    
    def test_api_football_connection(self):
        """Test API-Football connectivity"""
        try:
            fixtures = self.api_football.get_fixtures(
                league_id=39, season=2024, status='FINISHED'
            )
            self.assertGreater(len(fixtures), 0, "No fixtures returned")
            print(f"✓ API-Football: {len(fixtures)} fixtures found")
        except Exception as e:
            self.fail(f"API-Football connection failed: {e}")
    
    def test_football_data_connection(self):
        """Test Football-Data.org connectivity"""
        try:
            matches = self.football_data.get_matches(
                competition_id=39, status='FINISHED', limit=10
            )
            self.assertGreater(len(matches), 0, "No matches returned")
            print(f"✓ Football-Data: {len(matches)} matches found")
        except Exception as e:
            self.fail(f"Football-Data connection failed: {e}")
    
    def test_statsbomb_data_fetch(self):
        """Test StatsBomb data availability"""
        try:
            matches = StatsbombClient.get_matches(season=2023, competition_id='25')
            self.assertGreater(len(matches), 0, "No matches from StatsBomb")
            print(f"✓ StatsBomb: {len(matches)} PL 2023 matches found")
        except Exception as e:
            self.fail(f"StatsBomb fetch failed: {e}")
    
    def test_data_quality(self):
        """Verify returned data has required fields"""
        fixtures = self.api_football.get_fixtures(39, 2024, 'FINISHED')
        
        required_fields = ['fixture', 'teams', 'goals']
        
        for fixture in fixtures[:5]:  # Test first 5
            for field in required_fields:
                self.assertIn(field, fixture, 
                            f"Missing field: {field} in {fixture}")
        
        print("✓ Data quality validation passed")

if __name__ == '__main__':
    unittest.main()
```

---

## Summary: Which API to Use When

| Task | Recommended API | Reason |
|------|-----------------|--------|
| Live scores, real-time data | API-Football | Best real-time coverage, good for live updates |
| Historical fixtures, standings | Football-Data.org | Reliable, 15+ seasons, perfect for training |
| Event-level analysis (shots, passes) | StatsBomb | Most detailed events, no rate limits, free |
| Team statistics (xG, possession) | API-Football + StatsBomb | Complementary data |
| Player performance | API-Football | Best player data availability |
| Injury information | API-Football | Only provider with injury data |

---

**Next Steps:**
1. Sign up for free API keys (RapidAPI, Football-Data.org)
2. Test connections using provided code
3. Implement data collection pipeline
4. Start training models with historical data
