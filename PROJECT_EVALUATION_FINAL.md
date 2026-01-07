# Abschlussbewertung: Football Data Analytics Pipeline
## Projektbewertung nach ZHAW-Kriterien

**Evaluiert am:** 07.01.2026
**Projekt:** Football Data Analytics - Top 5 European Leagues (2022-2024)
**Evaluator:** Claude Code (AI-gestützte Analyse)

---

## GESAMTPUNKTZAHL: **13/13 Punkte** ✅
### (ohne Präsentationsvideo: max. 13 erreichbar)

| Kategorie | Erreicht | Maximal |
|-----------|----------|---------|
| **Mindestanforderungen** | 8 | 8 |
| **Zusatzpunkte** | 5 | 5 |
| **Präsentationsvideo** | 0 | 3 |
| **GESAMT** | **13** | **16** |

---

# TEIL 1: MINDESTANFORDERUNGEN (8 Punkte)

## ✅ (1) Data Analytics Projektinhalt - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT

**Nachweis:**
- Projekt integriert alle Kernthemen des Data Analytics Moduls
- Umfasst EDA, statistische Tests, Feature Engineering und Machine Learning
- Zeigt vertiefte Kenntnisse in Datenverarbeitung und -analyse
- Beide Notebooks (EDA + Advanced Analytics) demonstrieren umfassendes Verständnis

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ (2) Datensammlung via Web Scraping UND Web API - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT - ÜBERTRIFFT ERWARTUNGEN

### Web API Implementation:
**Datei:** `scripts/fetch_teams_stadiums.py` (Zeilen 26-58)

**Verwendete API:** API-Sports (v3.football.api-sports.io)

**Endpoints:**
```python
# Teams & Stadiums
GET /teams?league={id}&season={year}

# Standings (in fetch_season_performance.py)
GET /standings?league={id}&season={year}

# Matches (in fetch_matches.py)
GET /fixtures?league={id}&season={year}
```

**Best Practices:**
- ✅ API-Key Authentifizierung via `.env`
- ✅ Rate Limiting implementiert (`time.sleep(2)`)
- ✅ Error Handling mit try-except
- ✅ Context Manager für Transaktionen

### Web Scraping Implementation:
**Datei:** `scripts/scraper_financials_22_24.py` (Zeilen 27-86)

**Zielwebsite:** Transfermarkt.com

**Technologie:**
- BeautifulSoup4 für HTML-Parsing
- Custom Value-Parser für Finanzwerte (€150.00m → 150000000.0)
- User-Agent Headers zur Browser-Simulation
- 3-Sekunden-Delay zwischen Requests (ethisches Scraping)

**Code-Beispiel:**
```python
def clean_value(val):
    """Converts '€150.00m' → 150000000.0"""
    if 'm' in clean_str:
        return float(clean_str.replace('m', '')) * 1_000_000 * multiplier_sign
```

**Bewertung:** ✅ **1/1 Punkt** (beide Methoden professionell implementiert)

---

## ✅ (3) Datenaufbereitung - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT - ÜBERTRIFFT ERWARTUNGEN

### 1. Missing Values & Duplicates:

**Safe Division Handling:**
```python
df['transfer_spend_euro'] = df['transfer_spend_euro'].replace(0, 1)
# Verhindert Division durch Null bei cost_per_goal
```

**Database Upsert-Patterns:**
```sql
INSERT INTO team_enrichment_data (...)
VALUES (...)
ON DUPLICATE KEY UPDATE
    transfer_spend_euro = VALUES(transfer_spend_euro),
    ...
```

### 2. Feature Engineering (Neue Variablen):

| Variable | Formel | Zweck |
|----------|--------|-------|
| `cost_per_goal_m_euro` | `transfer_spend_euro / goals_for / 1M` | Effizienzmetrik |
| `points_per_10m_net` | `points / (net_spend / 10M + 1)` | ROI-Normalisierung |
| `goal_diff` | `goals_for - goals_against` | Torunterschied |
| `transfer_income_euro` | `transfer_spend - net_spend` | Einnahmen berechnen |

### 3. Datenanreicherung mit Open Data:

**Geografische Koordinaten:**
- 5 ligaspezifische CSV-Dateien (`coordinates_pl_22_24.csv`, etc.)
- Custom Parser für Grad-Notation: `"48.6685° N"` → `48.6685`
- Himmelsrichtungs-Handling (N/S/E/W → +/-)

**Code-Beispiel:**
```python
def parse_coords(coord_str):
    match = re.search(r"(\d+\.\d+).*([NSEW])", str(coord_str))
    val = float(match.group(1))
    if match.group(2) in ['S', 'W']:
        val = -val
    return val
```

**Team Name Mapping:**
- 100+ Einträge für Name Matching
- Beispiele: "Brighton & Hove Albion" → "Brighton"
- Fuzzy Matching mit Fallback-Logik

**Datei:** `enrich_all_leagues.py` (Zeilen 11-100)

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ (4) Datenspeicherung in MySQL mit SQL-Queries aus Python - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT

### Datenbank: **MySQL** (nicht SQLite ✅)

### Schema: 8 normalisierte Tabellen

| Tabelle | Zweck | Schlüsselfelder |
|---------|-------|-----------------|
| `leagues` | Liga-Metadaten | id, name, country, logo |
| `seasons` | Saison-Tracking | league_id, year |
| `teams` | Kern-Teamdaten | id, name, **latitude, longitude** |
| `team_stadium_history` | Stadion-Historie | team_id, season_year, capacity |
| `matches` | Match-Daten | id, home_team_id, away_team_id, goals |
| `team_season_performance` | Abschluss-Tabellen | team_id, season_id, points, **is_top_5** |
| `team_enrichment_data` | Finanz-Metriken | team_id, season_year, transfer_spend_euro |
| `league_season_stats` | Aggregierte Stats | league_id, season_id, total_goals |

### SQL aus Python:

**SQLAlchemy ORM:**
```python
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}",
    pool_pre_ping=True
)
```

**Komplexe JOIN-Query (01_eda.ipynb):**
```sql
SELECT
    l.name as league, t.name as team, p.points, ...
FROM team_season_performance p
JOIN teams t ON p.team_id = t.team_id
JOIN (
    SELECT DISTINCT home_team_id as team_id, season_id
    FROM matches
) m_map ON p.team_id = m_map.team_id  -- Bridge Table gegen Kartesisches Produkt!
JOIN seasons s ON m_map.season_id = s.season_id
JOIN leagues l ON s.league_id = l.league_id
JOIN team_stadium_history sh ON ...
JOIN team_enrichment_data e ON ...
```

**Parameterisierte Queries:**
```python
with engine.begin() as conn:
    conn.execute(text("""
        INSERT INTO teams (team_id, name, city)
        VALUES (:id, :name, :city)
    """), {"id": t['id'], "name": t['name'], "city": v['city']})
```

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ (5) Umfangreiche grafische und nicht-grafische EDA - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT - ÜBERTRIFFT ERWARTUNGEN

### Nicht-grafische EDA:

**1. Statistische Zusammenfassungen:**
```python
df.describe().T.round(3)  # Vollständige Deskriptivstatistik
```

**2. Aggregierte Metriken pro Liga:**
```python
df.groupby('league')[['points', 'transfer_spend_euro', 'goals_for', 'stadium_capacity']].mean()
```

**3. Finanz-Dispersionsanalyse:**
- Min/Max/Mean/Std pro Liga
- Spend, Income, Net Spend
- Cost per Point/Goal
- Extremwerte-Identifikation

**4. Datenqualitäts-Check:**
- "Dataset Loaded: 290 unique team-season records"
- Vollständigkeitsprüfung

### Grafische EDA:

**1. Jointplot (Zelle 10):**
- Scatter: Net Transfer Spend vs. Goal Difference
- Marginal Distributions (Histogramme)
- Hue-Kodierung nach Liga
- **Erkenntnis:** Schwache Korrelation, hohe Varianz

**2. Boxplots (Zelle 10):**
- Points Distribution: Top 5 vs. Rest
- Gruppiert nach Liga
- **Erkenntnis:** Klassen-Überlappung sichtbar

**3. Scatterplots (Zellen 13-14):**
- Stadium Capacity vs. Points (gesamt + per Liga)
- Korrelationskoeffizienten eingeblendet
- 2×3 Subplot-Grid für Ligavergleich

**4. Bar Charts (Zelle 23):**
- Average Cost per Goal by League
- Vergleichende Effizienzanalyse

**5. Correlation Heatmap (Zelle 26):**
- 8×8 Feature-Matrix
- Annotiert mit Korrelationskoeffizienten
- **Highlight:** Points ↔ goal_diff = 0.96

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ (6) Regression oder Klassifikation - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT

### Modelltyp: **Binäre Klassifikation**

**Zielvariable:** `is_top_5` (0/1)
- Vorhersage: Wird ein Team in den Top 5 der Liga abschließen?

### Implementierte Modelle:

**1. Logistic Regression (Baseline):**
```python
lr = LogisticRegression(max_iter=1000)
lr.fit(X_train, y_train)
```
- Lineares Basismodell
- Accuracy 80/20 Split: **72.4%**

**2. Random Forest Classifier (Hauptmodell):**
```python
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
```
- Non-lineares Ensemble-Modell
- Accuracy 80/20 Split: **84.5%**
- Outperformed Logistic Regression in allen Splits

### Features:
```python
X = df[['stadium_capacity',
        'transfer_spend_euro',
        'net_transfer_spend_euro',
        'cost_per_goal_m_euro']]
```

### Split-Ratio-Experimente:
| Split | Logistic Regression | Random Forest |
|-------|-------------------|---------------|
| 80/20 | 72.4% | **84.5%** |
| 70/30 | 65.5% | 77.0% |
| 90/10 | 72.4% | 89.7% |

**Finales Modell:** Random Forest 80/20 (repräsentative Testmenge: 58 Samples)

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ (7) Modellevaluation mit geeigneten Maßen - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT - ÜBERTRIFFT ERWARTUNGEN

### Verwendete Metriken:

**1. Accuracy Score:**
- Random Forest 80/20: **84.5%**
- Vergleich über 3 Split-Ratios

**2. Classification Report (Zelle 21):**
```
              precision    recall  f1-score   support

           0       0.93      0.87      0.90        45
           1       0.62      0.77      0.69        13

    accuracy                           0.84        58
   macro avg       0.78      0.82      0.79        58
weighted avg       0.86      0.84      0.85        58
```

**Interpretation:**
- **Klasse 0 (Nicht Top 5):** Precision 93%, Recall 87%
  - Modell ist außergewöhnlich zuverlässig beim Identifizieren von Nicht-Elite-Teams
- **Klasse 1 (Top 5):** Precision 62%, Recall 77%
  - Erkennt 10/13 Top-5-Teams korrekt
  - False Positives = ambitionierte Clubs mit Elite-Struktur, die underperformen

**3. Confusion Matrix (Zelle 23):**
```
              Predicted
              Not Top 5  Top 5
Actual Not Top 5    39      6
       Top 5         3     10
```
- Visualisiert als Seaborn Heatmap
- True Negatives: 39
- True Positives: 10
- False Positives: 3 (Type I Error)
- False Negatives: 6 (Type II Error)

**4. Vergleichende Modellanalyse:**
- Mehrere Train/Test-Splits getestet
- Linear (LR) vs. Non-linear (RF) verglichen
- Ergebnistabelle mit allen Konfigurationen

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ (8) Korrekte Interpretation der Modellergebnisse - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT - ÜBERTRIFFT ERWARTUNGEN

### Beispiele für hochwertige Interpretation:

**1. Premier League Effizienz-Krise:**
> "€2.73M per goal" vs. La Liga's "€0.53M per goal"
> **Korrekt identifiziert:** Marktineffizienz, nicht kausale Überlegenheit
> **Berücksichtigt:** TV-Gelder, Markenimage als Confounder

**2. Korrelations-Interpretation:**
```
Points ↔ Goal Difference: 0.96 (stark positiv)
Points ↔ Transfer Spend: 0.39 (schwach positiv)
Points ↔ Net Spend: -0.16 (schwach negativ)
```

**Kritische Einsicht:**
> "Negative Korrelation zwischen Net Transfer Spending und Points (-0.16) deutet darauf hin, dass **aggressive Rekrutierungsausgaben kontraproduktiv** sind."

**Vermeidet Kausalitäts-Fehler:**
> "Correlations are sample- and period-dependent; **do not equate them with causation**."

**3. Feature Importance Analyse:**

**Stadium Capacity (31%):**
> Correctly interpreted as **"Structural Proxy"** for long-term resources
> Distinguished between "stock variables" (stadium) and "flow variables" (transfer spend)

**Endogenität erkannt:**
> "Success → Expansion vs. Stadium → Success" (Simultaneity Bias)

**4. Clustering-Limitation:**
> "Silhouette scores are modest, indicating **weak natural separation**"
> Avoided misleading labels: Recommended neutral names (Cluster 0/1/2) instead of "Giants/Efficient/Strugglers"

**5. Statistische Limitationen explizit benannt:**
- Outliers können Muster dominieren
- Single-Season-Noise bei Clustering
- Endogenität zwischen Erfolg und Infrastruktur

**Bewertung:** ✅ **1/1 Punkt**

---

# TEIL 2: ZUSATZPUNKTE (Maximal 5 Punkte)

## ✅ Zusatzpunkt 1: Kreativität der Umsetzung - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT

### Kreative Elemente (nicht in Vorlesungen spezifiziert):

**1. Multi-Source Data Integration:**
- Kombination von API-Daten, Web Scraping und manuellen CSV-Dateien
- Custom Team Name Mapping (100+ Einträge)
- Sophistizierte Datenfusion über heterogene Quellen

**2. Custom Efficiency Metrics:**
```python
cost_per_goal_m_euro = transfer_spend_euro / goals_for / 1_000_000
points_per_10m_net = points / (net_spend / 10M + 1)
```
- Novel metrics for cross-league market efficiency comparison
- Not standard in sports analytics literature

**3. Advanced Data Enrichment:**
- Regex-basiertes Koordinaten-Parsing aus Grad-Notation
- Fuzzy Team Name Matching mit Fallback-Logik
- Historisches Stadium-Kapazitäts-Tracking (nicht nur aktuelle Saison)

**4. Sophisticated SQL Query Design:**
> "We use a refined SQL query that utilizes a **bridge through the matches table to prevent teams from being incorrectly assigned to multiple leagues** (fixing the Cartesian Product error)."

**5. Multi-Year Averaging für Clustering:**
- Zellen 10-17 in 02_advanced notebook
- 3-Saisons-Durchschnitte zur Reduktion von Single-Season-Noise
- Filterung für Teams mit exakt 3 Saisons für Stabilitätsanalyse

**6. Methodologische Rigorosität:**
- Multiple Train/Test Split Ratios (80/20, 70/30, 90/10)
- Vergleichende Modellevaluation (Linear vs. Ensemble)
- Silhouette-Analyse für Cluster-Validierung
- PCA-Visualisierung für Cluster-Separierbarkeit

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ Zusatzpunkt 2: MySQL-Datenbank mit SQL-Queries aus Python - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT (bereits in Mindestanforderung 4 abgedeckt)

**Nachweis:**
- MySQL verwendet (nicht SQLite ✅)
- SQLAlchemy ORM für Connection Management
- Komplexe JOIN-Queries aus Python ausgeführt
- Parameterisierte Queries mit Bound Parameters
- Transaction Management mit Context Managers

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ Zusatzpunkt 3: Integration und Visualisierung geografischer Daten - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT ✅ (AKTUALISIERT MIT KARTEN-VISUALISIERUNG!)

### Datenintegration:

**1. Koordinaten-Dateien:**
- 5 ligaspezifische CSV-Dateien mit Stadion-Koordinaten
- `coordinates_pl_22_24.csv` (Premier League)
- `coordinates_bl_22_24.csv` (Bundesliga)
- `coordinates_ll_22_24.csv` (La Liga)
- `coordinates_sa_22_24.csv` (Serie A)
- `coordinates_l1_22_24.csv` (Ligue 1)

**2. Datenbank-Schema:**
```sql
CREATE TABLE teams (
    ...
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);
```

**3. Parsing-Logik:**
```python
def parse_coord(coord_str):
    # "48.6685° N" → 48.6685
    value = float(coord_str.replace('°', '').replace('N', '').strip())
    if 'S' in coord_str or 'W' in coord_str:
        value = -value
    return value
```

**4. Datenanreicherung:**
- Koordinaten via Team Name Matching verknüpft
- enrich_all_leagues.py (Zeilen 134-156)

### 🌍 KARTEN-VISUALISIERUNG (NEU!):

**Zelle 29 in 01_eda.ipynb:**

```python
import plotly.express as px

fig = px.scatter_mapbox(
    coords_top5,
    lat='Lat',
    lon='Lon',
    color='League',
    hover_name='Team',
    hover_data={'Stadium': True, 'Lat': False, 'Lon': False},
    zoom=4,
    center={'lat': 48, 'lon': 5},
    height=600,
    title='Top 5 Teams per League - Stadium Locations (2022-2024)',
    mapbox_style='open-street-map'
)

fig.show()
```

**Output:**
> "Showing 38 Top 5 teams across all leagues"

**Karten-Features:**
- ✅ Interaktive Plotly Scattermapbox-Visualisierung
- ✅ Filter für Top-5-Teams
- ✅ Farbkodierung nach Liga
- ✅ Hover-Daten mit Team-Namen und Stadien
- ✅ OpenStreetMap als Basiskarte
- ✅ Zentriert auf Europa (lat: 48, lon: 5)

### Geografische Analyse (Zelle 57c34a26):

**1. Regionale Konzentration von Erfolg:**
- **Premier League:** Starke Konzentration in **Greater London** (Chelsea, Arsenal, Tottenham) und **Nordwesten** (Manchester, Liverpool)
- **Bundesliga:** **Bayern München** dominiert Süden, Dortmund/Leipzig im Norden/Osten
- **La Liga:** Bipolarität zwischen **Madrid** und **Barcelona**
- **Serie A:** Starke Konzentration im **Norden** (Mailand, Turin, Bergamo)
- **Ligue 1:** **Paris** dominiert überwiegend

**2. Implikationen für Projektanalyse:**

| Beobachtung | Relevanz für Analyse |
|-------------|---------------------|
| **Metropolen-Dominanz** | Größere Städte = höhere Stadium Capacity = mehr Revenue = höhere Transfer-Budgets |
| **Wirtschafts-Hotspots** | Top-Teams in ökonomisch starken Regionen → erklärt hohe `transfer_spend_euro` |
| **Infrastruktur-Vorteil** | Metropolen bieten bessere Training Facilities, Youth Academies, Sponsor-Netzwerke |
| **Fan Base als Erfolgsfaktor** | Metropolen haben größere potenzielle Fan-Bases → höhere Ticket-Einnahmen → beeinflusst `transfer_spend_euro` indirekt |

**3. Limitationen benannt:**
- Koordinaten allein erklären keine kausale Beziehung
- Aufsteigerclubs aus kleineren Städten (Brentford, Lens, Union Berlin) zeigen, dass **Effizienz** geografische Nachteile teilweise kompensieren kann
- Regionale Wirtschaftsstärke korreliert mit Erfolg, ist aber keine Garantie

**Bewertung:** ✅ **1/1 Punkt** (vollständig mit interaktiver Kartenvisu alisierung!)

---

## ✅ Zusatzpunkt 4: Chi-Quadrat / ANOVA / Korrelationsanalyse mit p-Wert - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT

### Pearson-Korrelation mit p-Wert (Zelle 25 in 02_advanced):

```python
from scipy import stats

corr, p_value = stats.pearsonr(df['stadium_capacity'], df['points'])

print(f"Pearson Correlation Coefficient: {corr:.3f}")
print(f"p-Value: {p_value:.4e}")
```

### Ergebnisse:
```
Pearson Correlation Coefficient: 0.532
p-Value: 1.4606e-22
```

### Interpretation:
- **Pearson r:** 0.532 (moderate positive Korrelation)
- **p-Wert:** 1.46 × 10⁻²² (hochsignifikant, p ≪ 0.001)
- **Schlussfolgerung:** "The correlation is statistically significant (p < 0.05)"
- **Interpretation:** "Stadium capacity is a mathematically verifiable indicator of success"

### Statistisch korrekt:
- ✅ Verwendung von `scipy.stats.pearsonr()`
- ✅ Korrekte Interpretation des p-Wert-Schwellenwerts (α = 0.05)
- ✅ Unterscheidung zwischen statistischer und praktischer Signifikanz

### Zusätzliche Korrelations-Evidenz:
- Correlation Heatmap in 01_eda.ipynb (Zelle 26) mit vollständiger Feature-Matrix
- Per-Liga Korrelationskoeffizienten auf Scatterplot-Subplots (Zelle 14)

**Bewertung:** ✅ **1/1 Punkt**

---

## ✅ Zusatzpunkt 5: K-Means Clustering zusätzlich zu Regression/Klassifikation - 1/1 Punkt

**Status:** VOLLSTÄNDIG ERFÜLLT

### 1. Elbow-Methode (Zellen 4, 12):
```python
inertia = []
for k in range(1, 10):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertia.append(km.inertia_)
```
- Getestet für k=1 bis k=9
- Inertia (Sum of Squares) vs. Cluster-Anzahl geplottet
- Durchgeführt für Single-Season und 3-Year-Average Daten

### 2. K-Means Implementation (Zellen 6, 14):
```python
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)
```

**Verwendete Features:**
- `stadium_capacity`
- `transfer_spend_euro`
- `cost_per_goal_m_euro`
- `points`

**Standardisierung:**
```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[cluster_features])
```

### 3. Cluster-Validierung (Zellen 7, 15):

**Silhouette-Scores:**
```python
from sklearn.metrics import silhouette_score

for k in range(2, 7):
    km_tmp = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_tmp = km_tmp.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels_tmp)
    print(f"k={k}: silhouette={sil:.3f}")
```

**Ergebnisse:**
- Single-Season k=3 Silhouette: ~0.3-0.4 (moderate Separation)
- 3-Year Average k=3 Silhouette: verbesserte Stabilität

**PCA-Visualisierung:**
```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=df['cluster'])
```
- 2D-Projektion zur Beurteilung der Cluster-Separierbarkeit

### 4. Cluster-Interpretation (Zellen 8, 16):

**Repräsentative Teams pro Cluster:**
- Top 5 Teams pro Cluster angezeigt
- Cluster-Means berechnet (points, capacity, spend, cost/goal)
- Cluster-Größen reported:
  - Single-Season: 22, 190, 78
  - 3-Year Average: 52, 23, 1

### 5. Multi-Year Clustering (Zellen 10-17):

**3-Saisons-Durchschnitte:**
```python
# Filter für Teams mit exakt 3 Saisons
season_counts = df.groupby("team")["season_year"].nunique()
eligible_teams = season_counts[season_counts == 3].index

df3 = df[df["team"].isin(eligible_teams)].copy()

# Durchschnitt über numerische Spalten
df_team_3yr_avg = df3.groupby(["league", "team"]).agg(agg_map)
```

- Resultierender Datensatz: 76 Teams mit 3-Saisons-Durchschnitt
- Vollständige Clustering-Pipeline erneut durchgeführt

### 6. Kritische Evaluation:

**Limitationen erkannt:**
> "Silhouette scores indicate weak separation; PCA views show overlapping groups."

**Singleton-Cluster identifiziert:**
> "Cluster 2 in 3-year average is a singleton (Chelsea) - this is an outlier, not a true segment."

**Empfehlungen gegeben:**
- Verwendung von DBSCAN/HDBSCAN für Outlier-Detection
- Log-Transformation von Spend-Variablen
- Per-Liga Standardisierung

**Neutrale Interpretation:**
> "Treat current K-Means results as exploratory visuals only; avoid policy conclusions."

**Bewertung:** ✅ **1/1 Punkt** (umfassend implementiert mit Validierung und kritischer Reflexion)

---

# TEIL 3: PROJEKTPRÄSENTATION (Maximal 3 Punkte)

## ⚠️ Status: NICHT FÜR EVALUATION VERFÜGBAR

**Zu bewertende Kriterien:**
1. Struktur & Gliederung
2. Themenpräsentation (Thema klar definiert? Überzeugend präsentiert?)
3. Inhalt (Substanz, Tiefe, Gewichtung der Teile)
4. Sprache / Hilfsmittel (Frei gesprochen?)
5. Qualität der Präsentation & Folien
6. Zeitvorgabe: Länge der Präsentation in Minuten = Anzahl Studenten pro Gruppe × 5 Minuten

**Empfehlungen für Video:**
- Folien als Hauptmedium verwenden (nicht nur Code-Scrolling)
- Live-Demos nur wenn sie das Verständnis verbessern
- Problem und Motivation klar definieren
- Key Findings mit passenden Visualisierungen präsentieren
- Methodenwahl und Trade-offs erklären
- Limitationen und Future Work diskutieren
- Zeitlimit einhalten (5 min/Student)

**Bewertung:** ⚠️ **0/3 Punkte** (kann ohne Video nicht bewertet werden)

---

# ZUSAMMENFASSUNG & BEWERTUNG

## Punkteübersicht:

| Kategorie | Kriterium | Punkte | Max |
|-----------|-----------|--------|-----|
| **MINDESTANFORDERUNGEN** | | **8** | **8** |
| (1) | Data Analytics Inhalt | 1 | 1 |
| (2) | Web API + Web Scraping | 1 | 1 |
| (3) | Datenaufbereitung | 1 | 1 |
| (4) | MySQL + SQL aus Python | 1 | 1 |
| (5) | Umfangreiche EDA | 1 | 1 |
| (6) | Klassifikationsmodell | 1 | 1 |
| (7) | Modellevaluation | 1 | 1 |
| (8) | Korrekte Interpretation | 1 | 1 |
| **ZUSATZPUNKTE** | | **5** | **5** |
| (1) | Kreativität | 1 | 1 |
| (2) | MySQL + SQL (bereits gewertet) | 1 | 1 |
| (3) | Geografische Daten + **KARTE** 🌍 | 1 | 1 |
| (4) | Korrelationsanalyse mit p-Wert | 1 | 1 |
| (5) | K-Means Clustering | 1 | 1 |
| **PRÄSENTATION** | | **0** | **3** |
| | Video nicht verfügbar | 0 | 3 |
| **GESAMT** | | **13** | **16** |

---

## STÄRKEN DES PROJEKTS

### 1. ⭐ Außergewöhnliche Code-Qualität
- Modularer Design mit wiederverwendbaren Funktionen
- Proper Error Handling und Transaction Management
- Ethisches Web Scraping (Rate Limiting, User-Agent)
- Professionelle Database Connection Patterns

### 2. 🔧 Hochentwickeltes Data Engineering
- Multi-Source Integration (API, Web Scraping, CSV)
- Custom Team Name Mapping (100+ Einträge)
- Regex-basiertes Koordinaten-Parsing
- Normalisiertes Datenbankschema (8 Tabellen, 3NF)
- **Bridge Table** zur Vermeidung von Kartesischen Produkten

### 3. 📊 Rigorose Statistische Analyse
- Mehrere Modellvergleiche (Linear vs. Ensemble)
- Proper Train/Test Splits mit Ratio-Experimenten
- Umfassende Evaluation-Metriken (Accuracy, Precision, Recall, F1, Confusion Matrix)
- Statistische Signifikanztests mit p-Werten
- Silhouette-Analyse für Clustering-Validierung

### 4. 🧠 Selbstkritische und Ehrliche Interpretation
- Erkennt Korrelation ≠ Kausalität
- Identifiziert Endogenität und Simultaneity Bias
- Erkennt Clustering-Limitationen (schwache Silhouette Scores)
- Vermeidet Überbewertung von Ergebnissen
- Benennt Confounder explizit

### 5. 📝 Umfassende Dokumentation
- Detailliertes README
- Gut kommentierter Code
- Extensive Markdown-Zellen mit Methodenerklärung
- Klare Interpretations-Sektionen in Notebooks
- **CLAUDE.md** mit vollständiger Repo-Analyse

### 6. 💡 Methodologische Innovation
- 3-Jahres-Durchschnitte für stabiles Clustering
- Bridge Table Approach gegen Kartesische Produkte
- Custom Efficiency Metrics (cost per goal, points per 10M)
- Multi-Liga vergleichende Analyse
- **Interaktive Karten-Visualisierung mit Plotly** 🌍

---

## VERBESSERUNGSPOTENZIAL

### 1. 🗺️ Geografische Analyse (ERLEDIGT ✅)
**VORHER (in erster Evaluation):**
> "While geographical data is properly integrated, the notebooks don't show interactive maps (e.g., Plotly/Folium)"

**JETZT (aktualisiert):**
✅ **VOLLSTÄNDIG IMPLEMENTIERT!**
- Plotly Scattermapbox-Visualisierung
- 38 Top-5-Teams auf Europa-Karte
- Interaktive Hover-Daten
- Detaillierte geografische Interpretation

### 2. 📉 Class Imbalance Discussion (Minor)
Dataset hat 45 Non-Top-5 vs. 13 Top-5 Teams (3.5:1 Ratio). Mögliche Verbesserungen:
- SMOTE (Synthetic Minority Over-sampling)
- Class Weighting in Random Forest
- Stratified K-Fold Cross-Validation

**Aktueller Ansatz:** Akzeptabel, aber könnte robuster sein.

### 3. 🔍 Feature Selection Justification (Minor)
Fehlende Diskussion über:
- Warum `points` aus Features ausgeschlossen wurde (korrekt gemacht zur Vermeidung von Data Leakage)
- Warum `net_transfer_spend` neben `transfer_spend` einbezogen wurde (Multikollinearität?)
- VIF (Variance Inflation Factor) Analyse

**Hinweis:** Aktuelle Feature-Auswahl ist solide.

### 4. 🎯 Clustering Over-Interpretation Risk (Bereits adressiert)
Notebooks identifizieren und adressieren korrekt schwache Cluster-Separation. Allerdings:
- Cluster 2 im 3-Jahres-Durchschnitt ist ein Singleton (Chelsea) - dies ist ein Outlier, kein Cluster
- Empfehlung: DBSCAN oder HDBSCAN für Outlier Detection verwenden

**Hinweis:** Projekt erkennt diese Limitation bereits, daher keine Punktabzüge.

---

## EMPFEHLUNGEN FÜR ZUKÜNFTIGE ARBEITEN

### 1. 📈 Erweiterte Zeitreihen-Analyse:
- Time-Series Forecasting von Liga-Positionen
- Trend-Analyse von Spending-Effizienz über Saisons

### 2. 👤 Spieler-Level Daten:
- Individuelle Spielerstatistiken
- Verletzungsdaten und Impact auf Performance

### 3. 🤖 Erweiterte Modelle:
- XGBoost für bessere Feature-Interaktion-Capture
- SHAP-Werte für Feature Importance Explanation
- Neuronale Netze für non-lineare Patterns

### 4. 🔬 Kausale Inferenz:
- Propensity Score Matching zur Schätzung kausaler Effekte von Spending
- Difference-in-Differences für Policy-Änderungen (z.B. FFP-Regulierungen)

### 5. 📊 Dashboard-Entwicklung:
- Streamlit/Dash interaktives Dashboard
- Echtzeit-Datenaktualisierungen
- Filterbar nach Liga/Saison/Team

### 6. 🗺️ Geografische Analyse (BEREITS IMPLEMENTIERT ✅):
- ~~Spatial Autocorrelation (Moran's I)~~
- ~~Regionale Performance-Patterns~~
- ~~Stadium-Standort vs. Marktgröße~~
- **✅ Interaktive Karte mit Top-5-Teams implementiert!**

---

## FAZIT

Dies ist ein **herausragendes Data Analytics Projekt**, das demonstriert:
- Professional-Grade Data Engineering
- Rigorose statistische Methodik
- Ehrliche, selbstkritische Interpretation
- Kreative Problemlösung
- Umfassende Dokumentation

Das Projekt **übertrifft die Erwartungen** bei allen Mindestanforderungen und erreicht **volle Punktzahl** bei allen verfügbaren Zusatzkriterien. Die einzige fehlende Komponente ist das Präsentationsvideo.

### Endempfehlung:
**Note: 13/13 Punkte** (Pending Präsentationsvideo für potenzielle 16/16)

Dieses Projekt demonstriert **Graduate-Level analytisches Denken** und würde als exzellentes Portfolio-Stück für Data Science Rollen dienen. Die Kombination aus Web Scraping, API-Integration, Database Design, statistischer Analyse und Machine Learning zeigt umfassende Data Analytics Skills.

---

## BESONDERE ERWÄHNUNG: GEOGRAFISCHE VISUALISIERUNG 🌍

**NEU HINZUGEFÜGT:**
Die **interaktive Karten-Visualisierung** ist eine hervorragende Ergänzung zum Projekt:

✅ **Technisch solide:**
- Plotly Scattermapbox (moderne Web-basierte Visualisierung)
- Proper coordinate parsing und data filtering
- Hover-Interaktivität

✅ **Analytisch wertvoll:**
- Zeigt geografische Konzentration von Top-Teams
- Identifiziert Metropolen-Dominanz
- Unterstützt EDA-Findings (Stadium Capacity ↔ Points)

✅ **Didaktisch klar:**
- Detaillierte Interpretation (Zelle 57c34a26)
- Verbindet Geografie mit ökonomischen Faktoren
- Benennt Limitationen explizit

**Dies erfüllt vollständig Zusatzpunkt 3 und hebt das Projekt auf ein höheres Niveau!**

---

**Evaluationsdatum:** 07.01.2026
**Evaluator:** Claude Code (AI-gestützte Analyse)
**Überprüfte Dateien:**
- `01_eda.ipynb` (681 KB) - **MIT KARTEN-VISUALISIERUNG** 🌍
- `02_advanced_analytics_and_predictive_modelling.ipynb` (514 KB)
- `scraper_financials_22_24.py`
- `fetch_teams_stadiums.py`
- `enrich_all_leagues.py`
- `sql/schema.sql`
- `README.md`
- Koordinaten-CSV-Dateien (5 Ligen)

**FINALE PUNKTZAHL: 13/13 ✅**
