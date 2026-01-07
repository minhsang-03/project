# Repository Analysis - Football Data Analytics Pipeline

**Analysis Date:** 2026-01-07
**Analyzed By:** Claude Code

---

## Executive Summary

This is a **Football Data Analytics Pipeline** designed to analyze top European football leagues (Premier League, Bundesliga, La Liga, Serie A, and Ligue 1) from 2022-2024. The project builds an end-to-end data engineering and machine learning system that collects match data from APIs, scrapes financial data, stores it in a normalized MySQL database, and develops predictive models to identify top-5 finishing teams.

---

## Project Purpose

The project aims to:
- Collect match data from API-Sports (v3.football.api-sports.io)
- Scrape transfer market financial data from Transfermarkt.com
- Enrich datasets with geospatial coordinates for team stadiums
- Normalize and store data in a relational MySQL database
- Perform exploratory data analysis (EDA)
- Develop predictive models to identify whether teams will finish in the top 5 of their league

**Ultimate Goal:** Predict which teams will finish in the top 5 using machine learning models trained on historical performance metrics and financial data.

---

## Repository Structure

```
/project
├── sql/
│   └── schema.sql                    # MySQL database schema
├── scripts/                          # Data pipeline execution layer (6 Python scripts)
├── notebooks/                        # Analysis & modeling layer (2 Jupyter notebooks)
├── data/                            # External data files (coordinates & financial data)
├── archive/                         # Legacy notebooks (previous versions)
├── requirements.txt                 # Python dependencies
├── .env                            # Configuration (not tracked)
└── README.md                       # Comprehensive documentation
```

### Layered Architecture

1. **Initialization Layer**: Database schema setup
2. **Data Collection Layer**: API fetching and web scraping
3. **Data Enrichment Layer**: Adding external data
4. **Analysis Layer**: EDA and predictive modeling

---

## Main Components

### Database Schema (`sql/schema.sql`)

8 normalized tables:

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `leagues` | League metadata | id, name, country, logo |
| `seasons` | League-season combinations | league_id, year (15 records: 5 leagues × 3 years) |
| `teams` | Team core data | id, name, code, country, founded, latitude, longitude |
| `team_stadium_history` | Historical stadium data | team_id, season_id, stadium_name, capacity |
| `matches` | Individual match results | id, league_id, season_id, fixture_id, home_team_id, away_team_id, goals |
| `team_season_performance` | Final standings | team_id, season_id, rank, points, is_top_5 (target variable) |
| `team_enrichment_data` | Transfer market financials | team_id, season_id, expenditure, income, net_balance |
| `league_season_stats` | Aggregated league statistics | league_id, season_id, total_goals, avg_goals_per_match |

### Data Pipeline Scripts (6 executables)

| Script | Purpose | Data Source | Output |
|--------|---------|-------------|--------|
| `fetch_leagues_seasons.py` | Initialize leagues and seasons | Hardcoded config | 5 leagues, 15 season records |
| `fetch_teams_stadiums.py` | Get team & stadium data | API-Sports | Teams table, stadium history |
| `fetch_season_performance.py` | Fetch final standings | API-Sports | Team rankings, target variable (is_top_5) |
| `fetch_matches.py` | Get individual match results | API-Sports | Match data with goals |
| `scraper_financials_22_24.py` | Web scrape transfer spending | Transfermarkt.com | CSV: transfer expenditure/income |
| `enrich_all_leagues.py` | Link external data to DB | CSV files | Updates teams & financial tables |

**Proper Execution Order:**
1. Initialize database (`schema.sql`)
2. Run `fetch_leagues_seasons.py`
3. Run `fetch_teams_stadiums.py`
4. Run `fetch_season_performance.py`
5. Run `fetch_matches.py`
6. Run `scraper_financials_22_24.py`
7. Run `enrich_all_leagues.py`
8. Execute `01_eda.ipynb`
9. Execute `02_advanced_analytics_and_predictive_modelling.ipynb`

### External Data Files (`data/` folder)

**Coordinate Files** (League geospatial data):
- `coordinates_pl_22_24.csv` - Premier League team stadiums
- `coordinates_bl_22_24.csv` - Bundesliga
- `coordinates_ll_22_24.csv` - La Liga
- `coordinates_sa_22_24.csv` - Serie A
- `coordinates_l1_22_24.csv` - Ligue 1

Format: Team name, Stadium, Latitude, Longitude (parsed from degree formats like "51.5549° N")

**Financial Data**:
- `leagues_transfer_financials_22_24.csv` - Master file (18KB, 100+ rows)
- Contains: League, Season, Club, Expenditure (€), Income (€), Net Balance (€)
- Covers all clubs across 5 leagues for 3 seasons

### Analysis Notebooks (`notebooks/` folder)

**01_eda.ipynb** (681 KB):
- Data loading from MySQL database
- Summary statistics and distributions
- Correlation analysis
- Data quality validation
- Feature candidate identification

**02_advanced_analytics_and_predictive_modelling.ipynb** (514 KB):
- Feature engineering (derived metrics from matches/standings)
- K-Means clustering analysis (team grouping by performance)
- Logistic Regression modeling
- Random Forest classification for top-5 prediction
- Feature importance analysis

---

## Technologies and Frameworks

### Core Stack
- **Language**: Python 3
- **Database**: MySQL (local or remote)
- **Environment Management**: python-dotenv (for `.env` credentials)

### Data Processing
- **pandas**: Data manipulation, cleaning, CSV I/O
- **sqlalchemy**: ORM, database connections
- **pymysql**: MySQL driver

### Data Collection
- **requests**: HTTP calls to API-Sports
- **beautifulsoup4**: HTML parsing for Transfermarkt web scraping

### Machine Learning (in notebooks)
- **scikit-learn**: Logistic Regression, Random Forest, K-Means clustering
- **matplotlib/plotly**: Data visualization

### Configuration
Credentials stored in `.env` (not versioned):
- `FOOTBALL_API_KEY`: API-Sports authentication
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: MySQL connection

---

## Data Coverage

### Data Sources

**1. API-Sports (v3.football.api-sports.io)**
- Leagues: 5 European leagues (Premier League, Bundesliga, La Liga, Serie A, Ligue 1)
- Seasons: 2022, 2023, 2024
- Endpoints used:
  - `/teams?league={id}&season={year}` → Teams & stadiums
  - `/standings?league={id}&season={year}` → Final rankings
  - `/fixtures?league={id}&season={year}` → Match fixtures

**2. Transfermarkt.com** (Web-scraped)
- Transfer spending: Expenditure, Income, Net Balance per team/season
- URL pattern: `transfermarkt.com/wettbewerb/einnahmenausgaben/...`

**3. Manual/CSV Data**
- Stadium coordinates (latitude/longitude) for 5 leagues
- Named mapping dictionary (100+ team name variants handled)

### Coverage Statistics
- **Teams**: ~110-120 per league × 5 leagues = 550+ unique team instances
- **Matches**: ~380 per league × 5 leagues × 3 seasons = 5,700+ matches
- **Seasons**: 15 (5 leagues × 3 years)
- **Financial Records**: 300+ (teams × seasons with transfer data)

### Target Variable
- `is_top_5`: Binary classification (1 if team finishes in top 5, 0 otherwise)
- Used in prediction models

---

## Code Quality & Design Patterns

### Strengths

1. **Modular Database Connection**: Each script uses `get_db_engine()` function
2. **Error Handling**: Try-catch blocks with user-friendly error messages
3. **API Rate Limiting**: `time.sleep()` calls (2-3 seconds) to respect API limits
4. **Duplicate Prevention**: `INSERT IGNORE` and `ON DUPLICATE KEY UPDATE` patterns
5. **Team Name Mapping**: Extensive dictionary (100+ entries) to handle name discrepancies between sources
6. **Coordinate Parsing**: Regex-based conversion from "48.6685° N" format to decimal floats
7. **Re-runnable Scripts**: All scripts use upsert patterns to allow safe re-execution

### Data Quality Considerations

**Name Matching Challenge:**
- Teams have different names in API vs. Transfermarkt
- Examples: "Brighton & Hove Albion" (CSV) vs. "Brighton" (API)
- Solution: Fuzzy matching + mapping dictionary in `enrich_all_leagues.py`

**Missing Data Handling:**
- Defaults: 0.0 for financial data, None for coordinates
- Graceful degradation when enrichment data is unavailable

---

## Development History

Git commit analysis shows thoughtful refactoring:
- Initial single-league focus → expanded to multi-league coverage
- Legacy notebooks archived (not deleted) for reference
- Recent commit: "Refactor code structure for improved readability and maintainability"
- Remote: GitHub (minhsang-03/project)

---

## Potential Use Cases

1. **Predictive Analytics**: Forecast top-5 finishers using team metrics
2. **Financial Impact Analysis**: Correlate transfer spending with league position
3. **Geospatial Analysis**: Map team locations and performance
4. **Clustering Studies**: Group similar teams by playing style/financial capacity
5. **Time-series Trends**: Compare team performance across 3 seasons
6. **Investment Insights**: Identify undervalued teams based on spending vs. performance

---

## Deployment Notes

- **Lightweight and portable**: Runs locally with minimal setup
- **No containerization**: Direct Python execution (Docker could be added)
- **Virtual environment recommended**: Clean dependency isolation
- **Credentials isolated**: `.env` file keeps secrets secure
- **IDE compatible**: Works seamlessly with VS Code, Jupyter Lab, etc.

---

## Summary

This is a **well-structured, production-ready data analytics project** that demonstrates solid software engineering practices (modular code, error handling, comprehensive documentation) combined with robust data science workflows (EDA, feature engineering, ML modeling).

The project successfully integrates multiple data sources (APIs, web scraping, manual CSVs) into a normalized database, enabling comprehensive analysis of European football performance and financial metrics. The codebase is maintainable, extendable, and follows best practices for data pipeline development.

### Key Achievements
- Clean separation of concerns (data collection → storage → analysis)
- Robust error handling and API rate limiting
- Comprehensive data enrichment from multiple sources
- Well-documented workflows and execution order
- Predictive modeling with interpretable results

### Potential Improvements
- Containerization (Docker) for easier deployment
- Automated testing suite for pipeline scripts
- CI/CD pipeline for automated data refreshes
- Additional ML models (XGBoost, Neural Networks)
- Real-time data updates and dashboards
- Expanded feature engineering (player-level stats, injury data)

---

**End of Analysis**
