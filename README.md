## Football Data Analytics Pipeline

### Executive Summary
This project builds an end-to-end data pipeline for top European football leagues (2022-2024), combining API-derived match data with web-scraped transfer market spending and geospatial features. The pipeline normalizes raw inputs into a relational schema, enriches them with external CSVs, and produces analysis-ready tables for feature engineering.

Outputs include exploratory notebooks, feature calculations (e.g., home strength, goals conceded per game), and predictive models aimed at ranking performance (e.g., top-five finishes). Everything runs locally with a lightweight Python/SQL stack so you can rebuild, iterate, and extend the dataset as sources evolve.

### Project Description
The workflow starts by initializing a database schema, then populating leagues, seasons, teams, stadium histories, standings, and detailed match results via API calls. Transfer market spending is scraped with Beautiful Soup to capture income, expenses, and net balances, which are joined back to teams alongside coordinate-based features.

Exploratory analysis (EDA) and advanced modeling live in notebooks that sit atop the curated tables. This separation keeps ingestion, enrichment, and modeling decoupled, making it easy to refresh the raw data or adapt the pipeline to additional leagues without disrupting downstream notebooks.

## How to Run the Python Scripts
A virtual environment keeps dependencies (pandas, SQLAlchemy, requests, Beautiful Soup) isolated for this project.

1. Create the virtual environment
    - macOS/Linux/Windows: run `python -m venv venv` in the project root. This creates a `venv` folder.

2. Activate the environment (every new terminal)
    - macOS/Linux: `source venv/bin/activate`
    - Windows PowerShell: `./venv/Scripts/Activate.ps1`
    - Windows Command Prompt: `./venv/Scripts/activate`
    - You should see `(venv)` in the prompt when active.

3. Install required packages
    - With the env active: `pip install -r requirements.txt`

4. Configure VS Code to use the venv
    - Open a Python file, press Cmd+Shift+P / Ctrl+Shift+P, choose "Python: Select Interpreter", and pick the interpreter inside `./venv`.

## Executing Python in VS Code
1. Terminal-driven execution
    - Activate the venv, then run scripts directly, e.g. `python scripts/fetch_leagues_seasons.py`.

2. VS Code integrated execution
    - After selecting the interpreter, use the Run button in the editor. VS Code will activate the venv and execute the current file.

## Data Pipeline Steps
1. **schema.sql (initialization)**
    - Purpose: Create the empty database structure (tables, columns, data types).
    - When: Run once at the start or after structural changes.

2. **fetch_leagues_seasons.py (metadata)**
    - Purpose: Insert leagues (IDs 39, 78, 140, etc.) and seasons 2022-2024 from the API.
    - Why: Serves as the anchor; other tables reference these IDs.

3. **fetch_teams_stadiums.py (teams)**
    - Purpose: Fetch teams for each league/season plus stadium history into `teams` and `team_stadium_history`.
    - Why: Teams must exist before assigning matches or transfer data.

4. **fetch_season_performance.py (target variables)**
    - Purpose: Fetch final tables (standings) and populate `is_top_5`.
    - Why: Provides ground truth for modeling.

5. **fetch_matches.py (match details)**
    - Purpose: Load individual match results (full-time scores).
    - Benefit: Enables feature calculations such as home strength and goals conceded per game.

6. **scraper_financials_22_24.py (transfer spending)**
    - Purpose: Scrape transfer spending, income, and net spending from Transfermarkt using Beautiful Soup.
    - Why: Supplies financial features for enrichment and modeling.

7. **enrich_all_leagues.py (enrichment)**
    - Purpose: Link external CSVs (coordinates and transfer market data) to existing teams.
    - Note: To expand to additional leagues, extend the CSV inputs; otherwise fields remain NULL for unsupported leagues.

8. **01_eda.ipynb (exploratory analysis)**
    - Purpose: Visualize data, compute correlations, and prepare candidate features.
    - When: Run whenever the database is refreshed.

9. **02_advanced_analytics_and_predictive_modelling.ipynb (modeling)**
    - Purpose: Engineer final features, train predictive models (e.g., top-five finishers), and evaluate performance.
    - When: After EDA selects candidate features and the dataset is fully enriched.

