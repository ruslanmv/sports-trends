# Sports Prediction Platform: Complete Technical Implementation Plan

**Version:** 1.0  
**Last Updated:** June 2025  
**Use Case:** ML-powered sports outcome prediction with historical team analysis and real-time game forecasting

---

## Executive Summary

This document outlines a complete architecture for building a scalable sports prediction platform using free APIs, open-source machine learning frameworks, and cloud infrastructure. The platform ingests historical match data, team statistics, and player information to train predictive models that forecast match outcomes with statistical confidence intervals.

The system is designed to be **modular, extensible, and cost-effective**, enabling integration with multiple sports (football/soccer, basketball, baseball, American football, ice hockey, tennis) and betting/analytics platforms.

---

## Part 1: Free Sports Data APIs

### 1.1 Primary Football/Soccer APIs

#### **API-Football (RapidAPI)**
- **Endpoint:** `https://api-football-v3.p.rapidapi.com`
- **Free Tier:** 100 requests/day
- **Key Data:**
  - Live scores, fixtures, leagues
  - Team statistics (goals, possession, shots, xG)
  - Player info and performance metrics
  - Head-to-head historical records
- **Authentication:** RapidAPI key
- **Rate Limit:** 100 req/day free tier
- **Leagues Covered:** Premier League, La Liga, Serie A, Bundesliga, Ligue 1, MLS, Champions League, World Cup, Europa League
- **Data Freshness:** Real-time (5-10 min delay)

**Code Example:**
```python
import requests

def fetch_api_football(endpoint, params):
    headers = {
        'X-RapidAPI-Key': os.getenv('RAPIDAPI_KEY'),
        'X-RapidAPI-Host': 'api-football-v3.p.rapidapi.com'
    }
    response = requests.get(endpoint, headers=headers, params=params)
    return response.json()

# Get team statistics
team_stats = fetch_api_football(
    'https://api-football-v3.p.rapidapi.com/statistics',
    {'team': 33, 'season': 2024, 'league': 39}  # Manchester United, PL 2024
)
```

---

#### **Football-Data.org**
- **Endpoint:** `https://www.football-data.org/api/v4`
- **Free Tier:** 10 requests/minute
- **Key Data:**
  - Fixtures, live scores
  - Team standings
  - Match statistics
  - Player lineups
- **Authentication:** API key (free registration)
- **Rate Limit:** 10 req/minute
- **Leagues Covered:** 17 major leagues (Premier League, La Liga, Serie A, etc.) + international competitions
- **Historical Data:** 15+ seasons available
- **Data Freshness:** 15-minute update window

**Code Example:**
```python
import requests

API_KEY = os.getenv('FOOTBALL_DATA_KEY')
BASE_URL = 'https://www.football-data.org/api/v4'

def get_team_matches(team_id, status='FINISHED'):
    """Fetch historical matches for a team"""
    url = f'{BASE_URL}/teams/{team_id}/matches'
    params = {'status': status, 'limit': 100}
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Example: Get Manchester City matches
man_city_matches = get_team_matches(50)
```

---

#### **Statssbomb Open Data (GitHub)**
- **Source:** `https://github.com/statsbomb/open-data`
- **Free Tier:** 100% open, no API calls needed
- **Key Data:**
  - Event-level data (shots, passes, tackles, dribbles, etc.)
  - xG (expected goals) models
  - Possession chains
  - Player position heat maps
- **Coverage:** 32 leagues, 5000+ matches, 200+ seasons
- **Format:** JSON files (no rate limits)
- **Data Freshness:** Quarterly updates
- **Advantage:** Extremely detailed event data for advanced analytics

**Code Example:**
```python
import json
import urllib.request

def load_statssbomb_matches(season=2023):
    """Load StatsBomb match data from GitHub"""
    url = f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{season}/25.json'
    # 25 = Premier League
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

matches = load_statssbomb_matches(2023)
for match in matches:
    print(f"{match['home_team']['name']} vs {match['away_team']['name']}")
```

---

#### **Understat (Unofficial Data)**
- **Unofficial API:** Reverse-engineered via requests (use with caution)
- **Key Data:**
  - xG, xGA (expected goals/goals against)
  - Shot maps
  - Player season statistics
  - Team progressive stats
- **Note:** No official free API; scraping may violate ToS. Consider for analysis only.

---

### 1.2 Multi-Sport APIs

#### **SportsData.io (Free Tier)**
- **Endpoint:** `https://api.sportsdata.io`
- **Sports:** NFL, NBA, MLB, NHL, soccer, golf
- **Free Tier:** Limited (key sports covered)
- **Key Data:** Scores, standings, player stats
- **Rate Limit:** Check tier-specific limits

#### **TheSportsDB**
- **Endpoint:** `https://www.thesportsdb.com/api/v1`
- **Free Tier:** 100% free
- **Key Data:** Teams, players, historical results
- **Sports:** Football, basketball, cricket, baseball
- **No Authentication Needed**

---

#### **ESPN API (Unofficial)**
- **Source:** Reverse-engineered from espn.com
- **Key Data:** Live scores, team schedules, standings
- **No Official Rate Limit** (be respectful; 1 req/second)
- **Code Example:**
```python
import requests

def get_espn_nfl_scores():
    url = 'https://site.api.espn.com/en/site/api/site/rankings/football/nfl/25/2024'
    response = requests.get(url)
    return response.json()
```

---

### 1.3 Free Data Sources (Non-API)

#### **Kaggle Datasets**
- **URL:** `https://www.kaggle.com/`
- **Available:** Soccer, NBA, NFL, MLB historical datasets
- **Format:** CSV, JSON
- **Popular Datasets:**
  - European Soccer Database (25k+ matches)
  - NBA games and player stats
  - World Cup data (1930-2018)

#### **GitHub Public Repositories**
- `awesome-soccer` collections
- `football-data` repos with season-by-season fixtures
- UEFA, FIFA official data releases

#### **Web Scraping Fallback**
- **FlashScore, Sofascore:** Unofficial scraping (Selenium/BeautifulSoup)
- **Official**: Respect robots.txt and terms of service
- **Recommended Libraries:** `selenium`, `beautifulsoup4`, `scrapy`

---

## Part 2: Data Architecture & Pipeline

### 2.1 Data Ingestion Pipeline

```
┌─────────────────────────┐
│  Free Public APIs       │
│ (API-Football, Fb-Data) │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Data Collection Service    │
│ (Python + APScheduler)      │
│ - Fetch fixtures daily      │
│ - Store in PostgreSQL       │
│ - Queue processing jobs     │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  PostgreSQL Data Warehouse   │
│ - teams table                │
│ - matches table              │
│ - player_stats table         │
│ - live_fixtures table        │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Feature Engineering Layer   │
│ (Pandas + Feature Store)     │
│ - Form streaks              │
│ - Home/away differential     │
│ - Head-to-head records       │
│ - Injury impact features     │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  ML Model Training           │
│ (scikit-learn, XGBoost,      │
│  LightGBM, CatBoost)         │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Prediction Engine + API     │
│ (FastAPI + Redis Cache)      │
│ - Real-time predictions      │
│ - Confidence scoring         │
│ - Betting odds integration   │
└──────────────────────────────┘
```

### 2.2 Database Schema

```sql
-- Teams Table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    external_id INT UNIQUE,
    name VARCHAR(255),
    league_id INT,
    season INT,
    avg_goals_for FLOAT,
    avg_goals_against FLOAT,
    form_last_5 FLOAT,
    home_record JSONB,
    away_record JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Matches Table
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    external_id INT UNIQUE,
    home_team_id INT REFERENCES teams(id),
    away_team_id INT REFERENCES teams(id),
    fixture_date TIMESTAMP,
    home_goals INT,
    away_goals INT,
    status VARCHAR(50),
    xg_home FLOAT,
    xg_away FLOAT,
    possession_home FLOAT,
    shots_on_target_home INT,
    league_id INT,
    season INT,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT no_duplicate_match UNIQUE(home_team_id, away_team_id, fixture_date)
);

-- Player Stats Table
CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    player_id INT,
    team_id INT REFERENCES teams(id),
    match_id INT REFERENCES matches(id),
    goals INT DEFAULT 0,
    assists INT DEFAULT 0,
    shots INT DEFAULT 0,
    passes_completed INT DEFAULT 0,
    tackles INT DEFAULT 0,
    interceptions INT DEFAULT 0,
    season INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Predictions Table
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    match_id INT REFERENCES matches(id),
    model_version VARCHAR(50),
    home_win_probability FLOAT,
    draw_probability FLOAT,
    away_win_probability FLOAT,
    predicted_winner VARCHAR(50),
    confidence FLOAT,
    over_2_5_probability FLOAT,
    under_2_5_probability FLOAT,
    predicted_at TIMESTAMP DEFAULT NOW()
);

-- Live Fixtures Queue
CREATE TABLE upcoming_fixtures (
    id SERIAL PRIMARY KEY,
    external_id INT UNIQUE,
    home_team_id INT REFERENCES teams(id),
    away_team_id INT REFERENCES teams(id),
    fixture_date TIMESTAMP,
    league_id INT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
```

---

## Part 3: Machine Learning Models

### 3.1 Baseline Models (Recommended for MVP)

#### **Model 1: Logistic Regression with Team ELO**

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

class ELOFootballModel:
    """
    Elo-based model with logistic regression for match outcome prediction
    """
    
    def __init__(self, k=32):
        self.k = k  # K-factor for Elo rating
        self.elo_ratings = {}
        self.model = LogisticRegression(max_iter=1000)
        
    def calculate_elo(self, team_id, opponent_rating, result, current_elo):
        """
        result: 1 = win, 0.5 = draw, 0 = loss
        """
        expected = 1 / (1 + 10**((opponent_rating - current_elo) / 400))
        new_elo = current_elo + self.k * (result - expected)
        return new_elo
    
    def preprocess_features(self, home_team, away_team):
        """Extract features for prediction"""
        features = [
            home_team['elo'] - away_team['elo'],  # Elo differential
            home_team['home_win_rate'],
            away_team['away_win_rate'],
            home_team['goals_per_game'],
            away_team['goals_per_game_allowed'],
            home_team['form_last_5'],
            away_team['form_last_5'],
            1 if home_team.get('injuries') > away_team.get('injuries') else 0,
        ]
        return np.array(features).reshape(1, -1)
    
    def predict(self, home_team, away_team):
        """Predict match outcome"""
        features = self.preprocess_features(home_team, away_team)
        proba = self.model.predict_proba(features)[0]
        return {
            'home_win_prob': proba[1],
            'draw_prob': proba[2] if len(proba) > 2 else 0,
            'away_win_prob': proba[0],
            'predicted_winner': ['Away', 'Home'][np.argmax(proba)]
        }
```

#### **Model 2: XGBoost Ensemble**

```python
import xgboost as xgb
import pandas as pd
from sklearn.model_selection import train_test_split

def build_xgboost_model(historical_matches_df):
    """
    XGBoost model with feature engineering
    
    Expected columns: [
        'home_team_elo', 'away_team_elo',
        'home_recent_form', 'away_recent_form',
        'home_xg', 'away_xg',
        'home_team_injuries', 'away_team_injuries',
        'head_to_head_home_wins',
        'home_goals_conceded_last_5',
        'target'  # 0=away_win, 1=draw, 2=home_win
    ]
    """
    
    feature_cols = [col for col in historical_matches_df.columns 
                    if col != 'target']
    
    X = historical_matches_df[feature_cols]
    y = historical_matches_df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=7,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='multi:softprob',
        num_class=3,  # home_win, draw, away_win
        random_state=42,
        early_stopping_rounds=50,
        eval_metric='mlogloss'
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("Top 10 Important Features:")
    print(feature_importance.head(10))
    
    return model

def predict_match_xgboost(model, match_features_df):
    """Predict probabilities for upcoming match"""
    probabilities = model.predict_proba(match_features_df)[0]
    return {
        'away_win_prob': probabilities[0],
        'draw_prob': probabilities[1],
        'home_win_prob': probabilities[2],
        'confidence': max(probabilities)
    }
```

#### **Model 3: Poisson Regression (Goals)**

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

def build_poisson_model(matches_df):
    """
    Poisson regression model for goal prediction
    Useful for: Over/Under 2.5, Both Teams Score, Exact Score
    """
    
    # Prepare data (home team perspective)
    model_data = matches_df[['home_team_attack_strength', 
                             'away_team_defense_weakness',
                             'home_goals']].copy()
    
    # Fit Poisson model for home goals
    formula_home = 'home_goals ~ home_team_attack_strength + away_team_defense_weakness'
    poisson_model_home = smf.glm(
        formula_home,
        data=model_data,
        family=sm.families.Poisson()
    ).fit()
    
    return poisson_model_home

def predict_goals(model, team_strengths):
    """Predict expected goals"""
    expected_goals = model.predict(team_strengths).values[0]
    
    # Calculate over/under 2.5 probability using Poisson distribution
    from scipy.stats import poisson
    
    prob_under_2_5 = sum(poisson.pmf(k, expected_goals) for k in range(3))
    prob_over_2_5 = 1 - prob_under_2_5
    
    return {
        'expected_goals': expected_goals,
        'over_2_5_prob': prob_over_2_5,
        'under_2_5_prob': prob_under_2_5
    }
```

### 3.2 Advanced Models (Production-Grade)

#### **Bayesian Hierarchical Model (PyMC)**
```python
import pymc as pm
import arviz as az

def build_bayesian_model(matches_df):
    """
    Bayesian hierarchical model accounting for:
    - Home advantage
    - Team strength (latent variables)
    - Seasonal variation
    - Measurement uncertainty
    """
    
    with pm.Model() as model:
        # Hyperpriors for team attack/defense
        home_attack = pm.Normal('home_attack', mu=0, sigma=1, shape=n_teams)
        home_defense = pm.Normal('home_defense', mu=0, sigma=1, shape=n_teams)
        away_attack = pm.Normal('away_attack', mu=0, sigma=1, shape=n_teams)
        away_defense = pm.Normal('away_defense', mu=0, sigma=1, shape=n_teams)
        
        # Home advantage
        home_advantage = pm.Normal('home_advantage', mu=0.3, sigma=0.1)
        
        # Expected goals
        home_xg = pm.math.exp(
            home_attack[home_team_ids] + 
            away_defense[away_team_ids] + 
            home_advantage
        )
        away_xg = pm.math.exp(
            away_attack[away_team_ids] + 
            home_defense[home_team_ids]
        )
        
        # Poisson likelihood
        home_goals = pm.Poisson('home_goals', mu=home_xg, 
                               observed=matches_df['home_goals'].values)
        away_goals = pm.Poisson('away_goals', mu=away_xg,
                               observed=matches_df['away_goals'].values)
        
        # Sample from posterior
        trace = pm.sample(2000, tune=1000, return_inferencedata=True)
    
    return model, trace
```

#### **Neural Network with LSTM for Form Sequences**
```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def build_lstm_model(sequence_length=10):
    """
    LSTM model that learns team form patterns
    Input: Last 10 match results + team stats
    """
    
    model = Sequential([
        LSTM(64, input_shape=(sequence_length, 8), return_sequences=True),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(3, activation='softmax')  # home_win, draw, away_win
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model
```

---

## Part 4: Feature Engineering

### 4.1 Essential Features for Prediction

```python
import pandas as pd
import numpy as np
from datetime import timedelta

class FeatureEngineer:
    """
    Comprehensive feature engineering for match prediction
    """
    
    @staticmethod
    def team_form(matches_df, team_id, last_n=5):
        """Recent form: average points last N matches"""
        recent = matches_df[
            (matches_df['home_team_id'] == team_id) | 
            (matches_df['away_team_id'] == team_id)
        ].tail(last_n)
        
        points = []
        for _, match in recent.iterrows():
            is_home = match['home_team_id'] == team_id
            goals_for = match['home_goals'] if is_home else match['away_goals']
            goals_against = match['away_goals'] if is_home else match['home_goals']
            
            if goals_for > goals_against:
                points.append(3)
            elif goals_for == goals_against:
                points.append(1)
            else:
                points.append(0)
        
        return np.mean(points) if points else 0
    
    @staticmethod
    def head_to_head(matches_df, home_id, away_id):
        """H2H record"""
        h2h = matches_df[
            ((matches_df['home_team_id'] == home_id) & 
             (matches_df['away_team_id'] == away_id)) |
            ((matches_df['home_team_id'] == away_id) & 
             (matches_df['away_team_id'] == home_id))
        ]
        
        if h2h.empty:
            return {'home_wins': 0, 'draws': 0, 'away_wins': 0}
        
        home_wins = len(h2h[
            ((h2h['home_team_id'] == home_id) & 
             (h2h['home_goals'] > h2h['away_goals'])) |
            ((h2h['away_team_id'] == home_id) & 
             (h2h['away_goals'] > h2h['home_goals']))
        ])
        
        return {
            'home_wins': home_wins,
            'draws': len(h2h[h2h['home_goals'] == h2h['away_goals']]),
            'away_wins': len(h2h) - home_wins - len(h2h[h2h['home_goals'] == h2h['away_goals']])
        }
    
    @staticmethod
    def goal_statistics(matches_df, team_id, venue='home'):
        """Goals for/against statistics"""
        if venue == 'home':
            matches = matches_df[matches_df['home_team_id'] == team_id]
            return {
                'goals_per_game': matches['home_goals'].mean(),
                'goals_conceded_per_game': matches['away_goals'].mean(),
                'clean_sheets': (matches['away_goals'] == 0).sum(),
                'matches_played': len(matches)
            }
        else:
            matches = matches_df[matches_df['away_team_id'] == team_id]
            return {
                'goals_per_game': matches['away_goals'].mean(),
                'goals_conceded_per_game': matches['home_goals'].mean(),
                'clean_sheets': (matches['home_goals'] == 0).sum(),
                'matches_played': len(matches)
            }
    
    @staticmethod
    def injury_impact(team_id, injury_db):
        """Impact of missing key players"""
        # Simplified: count missing players weighted by importance
        injuries = injury_db.filter(team_id=team_id, status='out')
        
        importance_weights = {
            'goalkeeper': 1.0,
            'defender': 0.7,
            'midfielder': 0.8,
            'forward': 0.9
        }
        
        impact_score = sum(
            importance_weights.get(inj.position, 0.5) 
            for inj in injuries
        )
        
        return impact_score
    
    @staticmethod
    def rest_days(match_date, prev_match_date):
        """Days since last match (fatigue factor)"""
        if prev_match_date is None:
            return 14
        return (match_date - prev_match_date).days
    
    @staticmethod
    def create_feature_matrix(matches_df, upcoming_matches, team_stats_db):
        """
        Create complete feature matrix for ML model
        """
        features_list = []
        
        for _, match in upcoming_matches.iterrows():
            home_id = match['home_team_id']
            away_id = match['away_team_id']
            match_date = match['fixture_date']
            
            feature_dict = {
                'home_elo': team_stats_db[home_id]['elo'],
                'away_elo': team_stats_db[away_id]['elo'],
                'elo_diff': team_stats_db[home_id]['elo'] - team_stats_db[away_id]['elo'],
                
                'home_form_5': FeatureEngineer.team_form(matches_df, home_id, 5),
                'away_form_5': FeatureEngineer.team_form(matches_df, away_id, 5),
                
                'home_goals_per_game': FeatureEngineer.goal_statistics(
                    matches_df, home_id, 'home')['goals_per_game'],
                'away_goals_per_game': FeatureEngineer.goal_statistics(
                    matches_df, away_id, 'away')['goals_per_game'],
                
                'home_goals_conceded': FeatureEngineer.goal_statistics(
                    matches_df, home_id, 'home')['goals_conceded_per_game'],
                'away_goals_conceded': FeatureEngineer.goal_statistics(
                    matches_df, away_id, 'away')['goals_conceded_per_game'],
                
                'h2h_home_wins': FeatureEngineer.head_to_head(
                    matches_df, home_id, away_id)['home_wins'],
                'h2h_away_wins': FeatureEngineer.head_to_head(
                    matches_df, home_id, away_id)['away_wins'],
                
                'home_injury_impact': FeatureEngineer.injury_impact(home_id, team_stats_db),
                'away_injury_impact': FeatureEngineer.injury_impact(away_id, team_stats_db),
            }
            
            features_list.append(feature_dict)
        
        return pd.DataFrame(features_list)
```

---

## Part 5: Prediction API & Backend

### 5.1 FastAPI Application

```python
# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import redis
import pickle
import json

app = FastAPI(
    title="Sports Prediction API",
    version="1.0.0",
    description="AI-powered match outcome and betting odds predictions"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Load models on startup
ml_models = {}

@app.on_event("startup")
async def load_models():
    global ml_models
    with open('models/xgboost_model.pkl', 'rb') as f:
        ml_models['xgboost'] = pickle.load(f)
    with open('models/elo_model.pkl', 'rb') as f:
        ml_models['elo'] = pickle.load(f)
    print("✓ Models loaded successfully")

# Pydantic models
class MatchPredictionRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    league_id: int
    fixture_date: datetime

class PredictionResponse(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    predicted_winner: str
    confidence: float
    expected_goals_home: float
    expected_goals_away: float
    over_2_5_probability: float
    over_1_5_probability: float
    both_teams_score_probability: float
    model_version: str
    generated_at: datetime

class OddsMapping(BaseModel):
    """Convert probabilities to betting odds"""
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    
    @staticmethod
    def prob_to_decimal_odds(prob):
        """Convert probability to decimal betting odds"""
        return 1 / prob if prob > 0 else float('inf')
    
    def to_odds(self):
        return {
            'home_win_odds': self.prob_to_decimal_odds(self.home_win_prob),
            'draw_odds': self.prob_to_decimal_odds(self.draw_prob),
            'away_win_odds': self.prob_to_decimal_odds(self.away_win_prob),
        }

# Endpoints

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/predict/match")
async def predict_match(request: MatchPredictionRequest):
    """
    Predict match outcome
    
    Returns probabilities for:
    - Home win, Draw, Away win
    - Over/Under 2.5 goals
    - Both teams score
    """
    
    # Check cache
    cache_key = f"pred_{request.home_team_id}_{request.away_team_id}_{request.fixture_date.date()}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    try:
        # Fetch team data from database
        home_team = db.query(Team).filter(Team.id == request.home_team_id).first()
        away_team = db.query(Team).filter(Team.id == request.away_team_id).first()
        
        if not home_team or not away_team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Create features
        features = FeatureEngineer.create_feature_matrix(
            matches_df=fetch_recent_matches(request.league_id),
            upcoming_matches=pd.DataFrame([{
                'home_team_id': request.home_team_id,
                'away_team_id': request.away_team_id,
                'fixture_date': request.fixture_date
            }]),
            team_stats_db=fetch_team_stats()
        )
        
        # Ensemble prediction
        xgb_pred = ml_models['xgboost'].predict_proba(features)[0]
        
        home_win_prob = float(xgb_pred[2])
        draw_prob = float(xgb_pred[1])
        away_win_prob = float(xgb_pred[0])
        
        confidence = max(xgb_pred)
        predicted_winner = ['Away', 'Draw', 'Home'][np.argmax(xgb_pred)]
        
        # Goal prediction
        expected_goals = {
            'home': home_team.avg_goals_for,
            'away': away_team.avg_goals_for
        }
        
        # Over/Under probabilities
        from scipy.stats import poisson
        prob_under_2_5_home = sum(poisson.pmf(k, expected_goals['home']) for k in range(3))
        prob_under_2_5_away = sum(poisson.pmf(k, expected_goals['away']) for k in range(3))
        over_2_5_prob = 1 - (prob_under_2_5_home * prob_under_2_5_away)
        
        response = PredictionResponse(
            match_id=request.match_id or 0,
            home_team=home_team.name,
            away_team=away_team.name,
            home_win_probability=round(home_win_prob, 3),
            draw_probability=round(draw_prob, 3),
            away_win_probability=round(away_win_prob, 3),
            predicted_winner=predicted_winner,
            confidence=round(confidence, 3),
            expected_goals_home=round(expected_goals['home'], 2),
            expected_goals_away=round(expected_goals['away'], 2),
            over_2_5_probability=round(over_2_5_prob, 3),
            over_1_5_probability=round(1 - (prob_under_2_5_home * prob_under_2_5_away) * 0.7, 3),
            both_teams_score_probability=round(
                (1 - poisson.pmf(0, expected_goals['home'])) * 
                (1 - poisson.pmf(0, expected_goals['away'])), 3
            ),
            model_version="v1.2.0",
            generated_at=datetime.now()
        )
        
        # Cache for 6 hours
        redis_client.setex(
            cache_key,
            21600,
            json.dumps(response.dict(), default=str)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fixtures/upcoming")
async def get_upcoming_fixtures(league_id: int, days_ahead: int = 7):
    """Get upcoming matches for next N days"""
    
    today = datetime.now().date()
    end_date = today + timedelta(days=days_ahead)
    
    fixtures = db.query(Match).filter(
        Match.league_id == league_id,
        Match.fixture_date >= today,
        Match.fixture_date <= end_date,
        Match.status == 'NOT_STARTED'
    ).order_by(Match.fixture_date).all()
    
    return [{
        'match_id': f.id,
        'home_team': f.home_team.name,
        'away_team': f.away_team.name,
        'fixture_date': f.fixture_date,
        'league': f.league.name
    } for f in fixtures]

@app.get("/leaderboard/model-accuracy")
async def model_accuracy_leaderboard():
    """Model performance metrics"""
    
    # Fetch last 100 predictions
    predictions = db.query(Prediction).order_by(
        Prediction.predicted_at.desc()
    ).limit(100).all()
    
    correct = 0
    total = len(predictions)
    
    for pred in predictions:
        match = pred.match
        if match.status == 'FINISHED':
            actual_winner = 'home' if match.home_goals > match.away_goals else \
                          'away' if match.away_goals > match.home_goals else 'draw'
            
            if pred.predicted_winner.lower() == actual_winner:
                correct += 1
    
    accuracy = correct / total if total > 0 else 0
    
    return {
        'accuracy': round(accuracy, 3),
        'predictions_evaluated': correct,
        'total_predictions': total,
        'win_rate_percentage': round(accuracy * 100, 1)
    }

@app.post("/admin/retrain-models")
async def trigger_model_retraining(background_tasks: BackgroundTasks):
    """Trigger background model retraining"""
    
    background_tasks.add_task(retrain_all_models)
    
    return {
        "status": "retraining_started",
        "message": "Model retraining initiated in background"
    }

def retrain_all_models():
    """Full model retraining pipeline"""
    print("🔄 Starting model retraining...")
    
    # Fetch latest data
    matches = fetch_all_matches(last_seasons=3)
    
    # Train models
    xgb_model = build_xgboost_model(matches)
    elo_model = build_elo_model(matches)
    
    # Save models
    with open('models/xgboost_model.pkl', 'wb') as f:
        pickle.dump(xgb_model, f)
    
    print("✓ Models retrained and saved")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Part 6: Frontend (Web Application)

### 6.1 React Dashboard

```javascript
// MatchPredictionDashboard.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function MatchPredictionDashboard() {
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUpcomingMatches();
  }, []);

  const fetchUpcomingMatches = async () => {
    try {
      const response = await axios.get('/api/fixtures/upcoming?league_id=39&days_ahead=7');
      setUpcomingMatches(response.data);
      
      // Fetch predictions for each match
      response.data.forEach(match => {
        fetchPrediction(match.match_id, match.home_team_id, match.away_team_id);
      });
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  };

  const fetchPrediction = async (matchId, homeTeamId, awayTeamId) => {
    try {
      const response = await axios.post('/api/predict/match', {
        home_team_id: homeTeamId,
        away_team_id: awayTeamId,
        league_id: 39,
        fixture_date: new Date().toISOString()
      });
      
      setPredictions(prev => ({
        ...prev,
        [matchId]: response.data
      }));
    } catch (error) {
      console.error('Error fetching prediction:', error);
    }
  };

  return (
    <div className="dashboard">
      <h1>🎯 Soccer Match Predictions</h1>
      
      <div className="matches-grid">
        {upcomingMatches.map(match => {
          const pred = predictions[match.match_id];
          
          return (
            <div key={match.match_id} className="match-card">
              <h3>{match.fixture_date}</h3>
              
              <div className="team-matchup">
                <span className="team home">{match.home_team}</span>
                <span className="vs">vs</span>
                <span className="team away">{match.away_team}</span>
              </div>
              
              {pred && (
                <>
                  <div className="probabilities">
                    <div className="prob-item home-win">
                      <span>Home Win</span>
                      <strong>{(pred.home_win_probability * 100).toFixed(1)}%</strong>
                    </div>
                    <div className="prob-item draw">
                      <span>Draw</span>
                      <strong>{(pred.draw_probability * 100).toFixed(1)}%</strong>
                    </div>
                    <div className="prob-item away-win">
                      <span>Away Win</span>
                      <strong>{(pred.away_win_probability * 100).toFixed(1)}%</strong>
                    </div>
                  </div>
                  
                  <div className="prediction-highlight">
                    <p><strong>Prediction:</strong> {pred.predicted_winner}</p>
                    <p><strong>Confidence:</strong> {(pred.confidence * 100).toFixed(1)}%</p>
                  </div>
                  
                  <div className="goals-section">
                    <span>Expected Goals: {pred.expected_goals_home.toFixed(1)} - {pred.expected_goals_away.toFixed(1)}</span>
                    <span>Over 2.5: {(pred.over_2_5_probability * 100).toFixed(1)}%</span>
                    <span>BTTS: {(pred.both_teams_score_probability * 100).toFixed(1)}%</span>
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default MatchPredictionDashboard;
```

---

## Part 7: Deployment Architecture

### 7.1 Docker Containerization

```dockerfile
# Dockerfile for API service
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile for data pipeline
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run scheduled data collection
CMD ["python", "data_pipeline/scheduler.py"]
```

### 7.2 Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: sports_predictions
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/sports_predictions
      REDIS_URL: redis://redis:6379
      RAPIDAPI_KEY: ${RAPIDAPI_KEY}
      FOOTBALL_DATA_KEY: ${FOOTBALL_DATA_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./models:/app/models

  data_pipeline:
    build:
      context: .
      dockerfile: Dockerfile.pipeline
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/sports_predictions
      RAPIDAPI_KEY: ${RAPIDAPI_KEY}
      FOOTBALL_DATA_KEY: ${FOOTBALL_DATA_KEY}
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

### 7.3 Cloud Deployment (AWS, GCP, Azure)

```yaml
# kubernetes-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sports-prediction-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sports-prediction-api
  template:
    metadata:
      labels:
        app: sports-prediction-api
    spec:
      containers:
      - name: api
        image: your-registry/sports-prediction-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: database-url
        - name: REDIS_URL
          value: redis://redis-service:6379
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: sports-prediction-api-service
spec:
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  selector:
    app: sports-prediction-api
```

---

## Part 8: Model Evaluation & Monitoring

### 8.1 Performance Metrics

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt

class ModelEvaluator:
    """
    Evaluate model performance with detailed metrics
    """
    
    @staticmethod
    def evaluate_classification(y_true, y_pred, y_pred_proba):
        """
        Evaluate 3-class outcome prediction (home win, draw, away win)
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'macro_precision': precision_score(y_true, y_pred, average='macro'),
            'macro_recall': recall_score(y_true, y_pred, average='macro'),
            'macro_f1': f1_score(y_true, y_pred, average='macro'),
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        return metrics, cm
    
    @staticmethod
    def calibration_analysis(y_true, y_pred_proba):
        """
        Analyze prediction calibration
        Are predicted probabilities well-calibrated with actual outcomes?
        """
        from sklearn.calibration import calibration_curve
        
        prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=10)
        
        return {
            'prob_true': prob_true,
            'prob_pred': prob_pred,
            'calibration_error': abs(prob_true - prob_pred).mean()
        }
    
    @staticmethod
    def betting_roi_analysis(predictions_df, actual_results_df, stake=1.0):
        """
        Calculate ROI if predictions were used for betting
        
        predictions_df columns: [match_id, predicted_winner, confidence]
        actual_results_df columns: [match_id, actual_winner, odds]
        """
        
        merged = predictions_df.merge(actual_results_df, on='match_id')
        
        total_stake = 0
        total_return = 0
        
        for _, row in merged.iterrows():
            if row['predicted_winner'] == row['actual_winner']:
                return_value = stake * row['odds']
                total_return += return_value
            total_stake += stake
        
        roi = (total_return - total_stake) / total_stake
        
        return {
            'total_stake': total_stake,
            'total_return': total_return,
            'roi_percentage': roi * 100,
            'roi': roi
        }
```

### 8.2 Continuous Monitoring

```python
import logging
from prometheus_client import Counter, Histogram, Gauge

# Prometheus metrics
prediction_counter = Counter(
    'predictions_total',
    'Total predictions made',
    ['league', 'model']
)

prediction_accuracy = Gauge(
    'prediction_accuracy',
    'Current model accuracy',
    ['model']
)

api_latency = Histogram(
    'prediction_api_latency_seconds',
    'API response latency'
)

class PredictionMonitor:
    """
    Monitor model predictions and system health
    """
    
    @staticmethod
    def log_prediction(match_id, prediction, actual_result=None):
        """Log prediction for audit trail"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'match_id': match_id,
            'prediction': prediction,
            'actual_result': actual_result,
            'correct': prediction == actual_result if actual_result else None
        }
        
        logging.info(json.dumps(log_entry))
        
        # Update metrics
        prediction_counter.labels(league='PL', model='xgboost').inc()
        
        if actual_result:
            if prediction == actual_result:
                prediction_accuracy.labels(model='xgboost').set(0.72)  # Update accordingly
    
    @staticmethod
    def alert_on_degradation(current_accuracy, threshold=0.65):
        """Alert if model accuracy drops below threshold"""
        if current_accuracy < threshold:
            logging.critical(
                f"⚠️ MODEL DEGRADATION: Accuracy {current_accuracy} below threshold {threshold}"
            )
            # Send alert (email, Slack, PagerDuty)
```

---

## Part 9: Legal & Responsible Use Considerations

### 9.1 Compliance Checklist

- [ ] **Data Privacy (GDPR)**: Ensure player data handling complies with GDPR
- [ ] **Terms of Service**: Respect API provider ToS; don't resell data
- [ ] **Betting Regulations**: Verify local gambling laws before monetizing
- [ ] **Fair Usage**: Implement rate limiting; don't overwhelm free APIs
- [ ] **Model Transparency**: Disclose that predictions are probabilistic, not guaranteed
- [ ] **Responsible Gambling**: Include warning about betting risks
- [ ] **Intellectual Property**: Don't use league/team logos without permission

### 9.2 Responsible AI Practices

```python
class ResponsiblePredictionFramework:
    """
    Ensure predictions are used responsibly
    """
    
    @staticmethod
    def add_disclaimer(prediction_response):
        """Add responsible gambling disclaimer"""
        
        prediction_response['disclaimer'] = {
            'risk_warning': 'Predictions are probabilistic estimates. Past performance does not guarantee future results.',
            'gambling_warning': 'Sports betting involves financial risk. Never bet more than you can afford to lose.',
            'model_confidence': f"This model has {prediction_response['confidence']*100:.1f}% confidence",
            'contact_for_help': 'Responsible Gambling Helpline: 1-800-GAMBLER'
        }
        
        return prediction_response
    
    @staticmethod
    def check_model_fairness(predictions_df, protected_attributes=['team_strength']):
        """Check for bias in predictions"""
        
        # Ensure no team is systematically favored/disfavored
        for attr in protected_attributes:
            group_accuracy = predictions_df.groupby(attr).apply(
                lambda x: (x['prediction'] == x['actual']).mean()
            )
            
            max_diff = group_accuracy.max() - group_accuracy.min()
            
            if max_diff > 0.15:  # >15% difference = potential bias
                logging.warning(f"⚠️ Potential bias detected in {attr}")
            
            return group_accuracy
```

---

## Part 10: Getting Started (Quick Start Guide)

### 10.1 Local Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/sports-prediction-platform.git
cd sports-prediction-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
# RAPIDAPI_KEY=your_key_here
# FOOTBALL_DATA_KEY=your_key_here
# DATABASE_URL=postgresql://user:password@localhost:5432/sports_predictions

# Initialize database
python scripts/init_db.py

# Download historical data
python scripts/download_historical_data.py

# Train initial models
python scripts/train_models.py

# Start API server
uvicorn main:app --reload

# In another terminal, start data pipeline
python data_pipeline/scheduler.py

# In another terminal, start frontend
cd frontend && npm start
```

### 10.2 Key Files Structure

```
sports-prediction-platform/
├── data_pipeline/
│   ├── apis/
│   │   ├── api_football.py
│   │   ├── football_data.py
│   │   └── statssbomb.py
│   ├── database.py
│   ├── models.py
│   └── scheduler.py
├── models/
│   ├── feature_engineering.py
│   ├── xgboost_trainer.py
│   ├── elo_model.py
│   └── evaluation.py
├── backend/
│   ├── main.py (FastAPI)
│   ├── routes/
│   │   ├── predictions.py
│   │   ├── fixtures.py
│   │   └── admin.py
│   └── monitoring/
│       └── metrics.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   └── package.json
├── tests/
│   ├── test_models.py
│   ├── test_api.py
│   └── test_predictions.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Part 11: Revenue & Monetization Models

### 11.1 Possible Monetization Strategies

| Model | Implementation | Pros | Cons |
|-------|----------------|------|------|
| **Freemium** | Free basic predictions, premium tier for detailed analysis | Low barrier to entry | High support costs |
| **API as a Service** | Charge developers per API call (like AWS) | Scalable | Requires enterprise sales |
| **Betting Affiliate** | Link to betting sites, earn commission | Passive income | Ethical concerns |
| **Subscription (B2B)** | Monthly fee for teams/analysts | Predictable revenue | Requires sales effort |
| **White Label** | License model to sports betting companies | High margins | Fewer clients |
| **Data Licensing** | Sell anonymized prediction data to research firms | Passive | Niche market |

---

## Part 12: Future Enhancements

- [ ] **Live Betting Integration**: Real-time in-match predictions
- [ ] **Player Injury Prediction**: Predict injuries based on workload
- [ ] **Transfer Market Analysis**: Predict player transfer fees
- [ ] **Sentiment Analysis**: Incorporate social media/news sentiment
- [ ] **Computer Vision**: Analyze game footage for tactical insights
- [ ] **Multi-League Correlation**: Model inter-league relationships
- [ ] **Mobile App**: React Native or Flutter app
- [ ] **Voice Assistant**: Alexa/Google Home integration

---

## References & Resources

**APIs**
- API-Football: https://rapidapi.com/api-sports/api/api-football
- Football-Data.org: https://www.football-data.org/
- StatsBomb: https://github.com/statsbomb/open-data
- Kaggle Datasets: https://www.kaggle.com/

**ML Libraries**
- XGBoost: https://xgboost.readthedocs.io/
- LightGBM: https://lightgbm.readthedocs.io/
- PyMC (Bayesian): https://www.pymc.io/
- TensorFlow/Keras: https://www.tensorflow.org/

**Deployment**
- Docker: https://www.docker.com/
- Kubernetes: https://kubernetes.io/
- AWS/GCP/Azure documentation

---

**Document Version:** 1.0  
**Last Updated:** June 2025  
**Author:** AI Research & Development  
**Status:** Ready for Implementation
