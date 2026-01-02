Process for getting league data (PL):

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
