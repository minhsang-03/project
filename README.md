# How to Run the Python Scripts
A virtual environment is a self-contained directory that contains a specific Python installation and all the additional packages (like pandas or sqlalchemy) required for this project.

1. Create the Virtual Environment
Open your terminal (Mac) or Command Prompt/PowerShell (Windows) in the project root folder and run:
`# General command`
`python -m venv venv`
_This creates a folder named venv in your project directory._

2. Activate the Environment
You must activate the environment every time you open a new terminal window to work on the project.
    1. macOS / Linux: Bash
    `source venv/bin/activate`

    2. Windows: PowerShell
    `.\venv\Scripts\Activate.ps1`

    3. Windows: DOS
    `.\venv\Scripts\activate`
_Note: Once activated, you will see (venv) appearing at the start of your terminal prompt._

3. Install Required Packages
With the environment activated, install all necessary libraries listed in the requirements.txt file:
    `pip install -r requirements.txt`

4. Setting up VS Code
If you are using VS Code, follow these steps to ensure the editor uses the correct environment:
    1. Open a Python file.
    2. Click on the Python Version in the bottom right corner (or press Cmd+Shift+P / Ctrl+Shift+P and type "Python: Select Interpreter").
    3. Select the interpreter that starts with ./venv or ('venv': venv).

## Executing Python in VS Code:
1. Execution via Terminal
Once activated, simply use the python command followed by the path to your script. Since the environment is active, this command automatically uses the libraries (like SQLAlchemy or requests) installed inside your venv.
    `python scripts/fetch_leagues_seasons.py`

3. Execution via VS Code (Integrated)
If you prefer not to type commands, VS Code can handle the venv for you:
Select Interpreter: Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows) and type "Python: Select Interpreter". Choose the one inside your ./venv folder.
Run File: Click the Play button in the top right corner of the editor. VS Code will automatically open a terminal, activate the venv, and run the script.

# Process for getting league data (PL):

1. schema.sql (Initialisierung)
Zweck: Erstellt die leere Datenbankstruktur (Tabellen, Spalten, Datentypen).

Wann: Nur ein einziges Mal ganz am Anfang oder wenn du die Struktur (wie für die Transfer-Einnahmen) geändert hast.

2. fetch_leagues_seasons.py (Die Metadaten)
Zweck: Erstellt die Einträge für die Ligen (ID 39, 78, 140, etc.) und die Jahre (2021-2023).

Wichtig: Das ist der "Anker". Alle anderen Tabellen beziehen sich auf diese IDs.

3. fetch_teams_stadiums.py (Die Akteure)
Zweck: Holt alle Teams der entsprechenden Ligen und Saisons und speichert sie in teams sowie die Stadion-Historie in team_stadium_history.

Warum hier: Ein Team muss in der Datenbank existieren, bevor wir ihm Spiele oder Transferdaten zuordnen können.

4. fetch_season_performance.py (Die Zielvariablen)
Zweck: Holt die Abschlusstabellen (Standings). Hier wird das Feld is_top_5 gefüllt.

Warum hier: Dies liefert uns die "Ground Truth" (die Wahrheit) für unser späteres Modell.

5. fetch_matches.py (Die Details)
Zweck: Lädt jedes einzelne Spielergebnis (Fulltime Scores).

Nutzen: Daraus berechnen wir später Features wie "Heimstärke" oder "Gegentore pro Spiel".

6. enrichment_pl_geo_spending_21-23.py (Die Veredelung)
Zweck: Verknüpft deine externen CSV-Daten (Koordinaten & Transfermarkt) mit den bestehenden Teams in der DB.

Wichtig: Da du nun auf 5 Ligen ausweiten willst, musst du dieses Skript entweder für die neuen Ligen anpassen (CSVs bereitstellen) oder akzeptieren, dass diese Felder für die Nicht-PL-Ligen erst einmal NULL bleiben.

7. 01_eda_and_features.ipynb (Die Analyse)
Zweck: Das ist dein Labor. Hier werden die Daten visualisiert, Korrelationen berechnet und die Features für das Modell vorbereitet.

Wann: Immer dann, wenn die Datenbank mit neuen Daten gefüllt wurde.
