import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import re

load_dotenv()

# --- MAPPING DICTIONARY ---
# Key: Name in deiner CSV (Transfermarkt/Coordinates)
# Value: Exakter Name in deiner MySQL-Datenbank (aus der API)
TEAM_NAME_MAP = {
    "Brighton & Hove Albion": "Brighton",
    "Leicester City": "Leicester",
    "Tottenham Hotspur": "Tottenham",
    "Wolverhampton Wanderers": "Wolves",
    "West Ham United": "West Ham",
    "Leeds United": "Leeds",
    "Newcastle United": "Newcastle",
    "Sheffield United": "Sheffield Utd",
    "Norwich City": "Norwich",
    "Luton Town": "Luton"
}

def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db}")

def get_clean_name(csv_name):
    """Prüft zuerst das Dictionary, sonst Standard-Bereinigung."""
    if csv_name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[csv_name]
    # Entferne Standard-Anhänge für besseres Matching
    return csv_name.replace(' FC', '').replace('AFC ', '').strip()

def parse_coords(coord_str):
    if pd.isna(coord_str): return None
    match = re.search(r"(\d+\.\d+).*([NSEW])", coord_str)
    if match:
        val = float(match.group(1))
        direction = match.group(2)
        if direction in ['S', 'W']: val = -val
        return val
    return None

def enrich_database():
    engine = get_db_engine()
    
    # Daten laden
    df_coords = pd.read_csv('data/coordinates_pl_21_23.csv')
    df_transfers = pd.read_csv('data/pl_transfer_spending_21_23.csv')

    with engine.connect() as conn:
        # 1. Koordinaten aktualisieren
        print("Aktualisiere Koordinaten...")
        for _, row in df_coords.iterrows():
            db_name = get_clean_name(row['Team'])
            conn.execute(text("""
                UPDATE teams 
                SET latitude = :lat, longitude = :lon 
                WHERE name LIKE :name
            """), {"lat": parse_coords(row['Latitude']), 
                   "lon": parse_coords(row['Longitude']), 
                   "name": f"%{db_name}%"})
        
        # 2. Transferdaten laden
        print("Lade Transferdaten...")
        db_teams = pd.read_sql("SELECT team_id, name FROM teams", engine)
        
        success_count = 0
        for _, row in df_transfers.iterrows():
            # Name aus CSV transformieren
            target_name = get_clean_name(row['Club'])
            
            # Suche ID in der Datenbank
            match = db_teams[db_teams['name'].str.contains(target_name, case=False)]
            
            if not match.empty:
                t_id = int(match.iloc[0]['team_id'])
                conn.execute(text("""
                    INSERT INTO team_enrichment_data 
                    (team_id, season_year, transfer_spend_euro, transfer_income_euro, net_transfer_spend_euro)
                    VALUES (:tid, :year, :spend, :income, :net)
                    ON DUPLICATE KEY UPDATE 
                        transfer_spend_euro = VALUES(transfer_spend_euro),
                        transfer_income_euro = VALUES(transfer_income_euro),
                        net_transfer_spend_euro = VALUES(net_transfer_spend_euro)
                """), {
                    "tid": t_id, "year": row['Season'], "spend": row['Expenditure'],
                    "income": row['Income'], "net": row['Net Balance']
                })
                success_count += 1
            else:
                print(f"⚠️ Warnung: Konnte Team '{row['Club']}' (gemappt auf '{target_name}') nicht in der DB finden.")
        
        conn.commit()
    print(f"✅ Fertig! {success_count} Transfer-Datensätze erfolgreich verarbeitet.")

if __name__ == "__main__":
    enrich_database()