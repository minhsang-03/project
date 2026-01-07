# Football Data Analytics Pipeline

## Executive Summary

This project builds an end-to-end data pipeline for top European football leagues (2022-2024), combining API-derived match data with web-scraped transfer market spending and geospatial features. The pipeline normalizes raw inputs into a relational schema, enriches them with external CSVs, and produces analysis-ready tables.

**Key Outputs:**
- **Exploratory Data Analysis (EDA)**: Data visualization, correlation analysis, and feature exploration
- **Advanced Analytics & Predictive Modeling**: Feature engineering, clustering analysis, and machine learning models for predicting top-five finishers
- **Analysis-ready Database**: Curated tables with match statistics, team performance, geospatial team data, and financial data

Everything runs locally with Python 3, a lightweight SQL database, and standard data science libraries (pandas, scikit-learn, SQLAlchemy).

## Project Architecture

### Data Flow
1. **Database Initialization** (`schema.sql`) → Create relational schema
2. **API Data Collection** → Fetch leagues, teams, matches, and standings
3. **Web Scraping** → Extract transfer market financial data
4. **Data Enrichment** → Link external geospatial and financial data
5. **Analysis & Modeling** → Jupyter notebooks for EDA and predictive modeling

### Technology Stack
- **Language**: Python 3
- **Database**: MySQL (local or remote)
- **Libraries**: pandas, SQLAlchemy, requests, Beautiful Soup, scikit-learn, matplotlib, plotly
- **Environment Management**: python-dotenv for secure configuration

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MySQL database (local or remote)
- `.env` file with required database credentials

### Environment Configuration (.env file)

Create a `.env` file in the project root with the following required variables:

```
FOOTBALL_API_KEY=your_api_key
DB_HOST=your_mysql_host
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name
```

**Note**: These credentials are used by all Python scripts to connect to the database. The `.env` file is automatically loaded by `python-dotenv` and should **never be committed to version control**.

### Virtual Environment Setup

1. **Create the virtual environment**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the environment** (required for every new terminal session)
   - macOS/Linux: `source venv/bin/activate`
   - Windows PowerShell: `./venv/Scripts/Activate.ps1`
   - Windows Command Prompt: `venv\Scripts\activate`
   - You should see `(venv)` in your terminal prompt when active

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Python interpreter in VS Code**
   - Open a Python file, press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Select "Python: Select Interpreter"
   - Choose the interpreter inside `./venv` folder

## Running the Project

### Data Pipeline Execution (Python Scripts)

Execute scripts in the following order to build the complete database:

1. **schema.sql** (initialization)
   ```bash
   # Execute the SQL file directly in your MySQL client
   # Creates the empty database structure
   ```

2. **fetch_leagues_seasons.py**
   ```bash
   python scripts/fetch_leagues_seasons.py
   ```
   Populates leagues (Premier League, Bundesliga, La Liga, Serie A, Ligue 1) and seasons (2022-2024).

3. **fetch_teams_stadiums.py**
   ```bash
   python scripts/fetch_teams_stadiums.py
   ```
   Fetches teams and stadium history for each league/season.

4. **fetch_season_performance.py**
   ```bash
   python scripts/fetch_season_performance.py
   ```
   Loads final season standings and identifies top-5 finishers (target variable for modeling).

5. **fetch_matches.py**
   ```bash
   python scripts/fetch_matches.py
   ```
   Loads individual match results, enabling feature calculations (e.g., home strength, goals conceded per game).

6. **scraper_financials_22_24.py** (optional – data already available in data/)
   ```bash
   python scripts/scraper_financials_22_24.py
   ```
   Scrapes transfer spending data from Transfermarkt (income, expenses, net spending).

7. **enrich_all_leagues.py**
   ```bash
   python scripts/enrich_all_leagues.py
   ```
   Links external CSV data (coordinates and transfer financials) to team records.

### Notebook Execution

After the database is fully populated:

#### Notebook 1: Exploratory Data Analysis (01_eda.ipynb)
- **Purpose**: Understand data distributions, identify patterns, and validate data quality
- **Contents**:
  - Data loading from database
  - Summary statistics and distributions
  - Correlation analysis
  - Visualization of key relationships
  - Feature candidate selection for modeling

#### Notebook 2: Advanced Analytics & Predictive Modeling (02_advanced_analytics_and_predictive_modelling.ipynb)
- **Purpose**: Engineer features, train machine learning models, and predict top-five finishers
- **Contents**:
  - Feature engineering (derived metrics from raw data)
  - Team clustering analysis (grouping similar-performing teams)
  - Logistic Regression modeling
  - Random Forest classification for top-5 prediction
  - Model evaluation and feature importance analysis

## Running in VS Code

**Terminal Method:**
1. Activate the venv: `source venv/bin/activate` (macOS/Linux)
2. Run any script: `python scripts/fetch_leagues_seasons.py`
3. Open notebooks: `jupyter notebook notebooks/01_eda.ipynb`

**VS Code Integrated Execution:**
1. After selecting the venv interpreter, use the "Run" button in the editor
2. Open notebooks directly in VS Code and run cells with the play button

## Project Structure

```
/project
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env                               # Database credentials (not in version control)
├── sql/
│   └── schema.sql                     # Database schema initialization
├── scripts/
│   ├── fetch_leagues_seasons.py       # Populate leagues and seasons
│   ├── fetch_teams_stadiums.py        # Fetch team data
│   ├── fetch_season_performance.py    # Load standings and targets
│   ├── fetch_matches.py               # Fetch match results
│   ├── scraper_financials_22_24.py    # Web scrape transfer data
│   └── enrich_all_leagues.py          # Link external data
├── notebooks/
│   ├── 01_eda.ipynb                   # Exploratory Data Analysis
│   └── 02_advanced_analytics_and_predictive_modelling.ipynb  # Feature engineering & modeling
├── data/
│   ├── coordinates_*.csv              # Geospatial data by league
│   └── leagues_transfer_financials_*.csv # Transfer market data
└── archive/
    └── legacy notebooks               # Previous versions
```

## Dependencies

All Python dependencies are listed in `requirements.txt`:
- **pandas**: Data manipulation and analysis
- **sqlalchemy**: Database ORM and connection management
- **pymysql**: MySQL database driver
- **requests**: API calls for football data
- **python-dotenv**: Load environment variables from `.env` file
- **beautifulsoup4**: Web scraping for transfer market data
- **scikit-learn**: Machine learning models (loaded by notebooks)
- **matplotlib/plotly**: Visualization (loaded by notebooks)

