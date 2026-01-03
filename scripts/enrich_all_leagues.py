import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import re

load_dotenv()

# --- EXTENDED MAPPING DICTIONARY ---
# Add known discrepancies between Transfermarkt/CSV names and API names here.
TEAM_NAME_MAP = {
    # England
    "Brighton & Hove Albion": "Brighton",
    "Ipswich Town": "Ipswich",
    "Leicester City": "Leicester",
    "Leeds United": "Leeds",
    "Luton Town": "Luton",
    "Tottenham Hotspur": "Tottenham",
    "Wolverhampton Wanderers": "Wolves",
    "West Ham United": "West Ham",
    "Newcastle United": "Newcastle",
    "Sheffield United": "Sheffield Utd",
    # Germany
    "Bayern Munich": "Bayern München",
    "Borussia Mönchengladbach": "Borussia Mönchengladbach",
    "Bayer 04 Leverkusen": "Bayer Leverkusen",
    "1.FC Union Berlin": "Union Berlin",
    "1.FC Heidenheim 1846": "1. FC Heidenheim",
    "SV Werder Bremen": "Werder Bremen",
    "RB Leipzig": "Leipzig",
    "1.FC Köln": "Köln",
    "1.FSV Mainz 05": "Mainz 05",
    "TSG 1899 Hoffenheim": "Hoffenheim",
    # Italy
    "Inter Milan": "Inter",
    "AC Milan": "Milan",
    "AS Roma": "Roma",
    "Hellas Verona": "Verona",
    "Atalanta BC": "Atalanta",
    "SSC Napoli": "Napoli",
    "US Salernitana 1919": "Salernitana",
    "Udinese Calcio": "Udinese",
    "Bologna FC 1909": "Bologna",
    "US Sassuolo": "Sassuolo",
    "AC Monza": "Monza",
    "SS Lazio": "Lazio",
    "ACF Fiorentina": "Fiorentina",
    "US Cremonese": "Cremonese",
    "Spezia Calcio": "Spezia",
    "FC Empoli": "Empoli",
    "UC Sampdoria": "Sampdoria",
    "US Lecce": "Lecce",
    "Genoa CFC": "Genoa",
    "Cagliari Calcio": "Cagliari",
    "Frosinone Calcio": "Frosinone",
    "Como 1907": "Como",
    "Parma Calcio 1913": "Parma",
    # France
    "Paris Saint-Germain": "Paris Saint Germain",
    "Olympique Lyonnais": "Lyon",
    "Olympique Marseille": "Marseille",
    "OGC Nice": "Nice",
    "Stade Rennais FC": "Rennes",
    "RC Lens": "Lens",
    "AS Monaco": "Monaco",
    "Olympique Lyon": "Lyon",
    "FC Lorient": "Lorient",
    "LOSC Lille": "Lille",
    "Stade Reims": "Reims",
    "FC Toulouse": "Toulouse",
    "FC Nantes": "Nantes",
    "Montpellier HSC": "Montpellier",
    "RC Strasbourg Alsace": "Strasbourg",
    "Angers SCO": "Angers",
    "Clermont Foot 63": "Clermont",
    "AJ Auxerre": "Auxerre",
    "AC Ajaccio": "Ajaccio",
    "FC Metz": "Metz",
    "Le Havre AC": "Le Havre",
    "AS Saint-Étienne": "Saint Etienne",
    # Spain
    "Atlético de Madrid": "Atletico Madrid",
    "Real Sociedad": "Real Sociedad",
    "FC Barcelona": "Barcelona",
    "UD Almería": "Almeria",
    "Real Betis Balompié": "Real Betis",
    "Celta de Vigo": "Celta Vigo",
    "RCD Espanyol Barcelona": "Espanyol",
    "Getafe CF": "Getafe",
    "RCD Mallorca": "Mallorca",
    "Elche CF": "Elche",
    "Valencia CF": "Valencia",
    "Real Valladolid CF": "Valladolid",
    "Cádiz CF": "Cadiz",
    "Villarreal CF": "Villarreal",
    "CA Osasuna": "Osasuna",
    "Athletic Bilbao": "Athletic Club",
    "Deportivo Alavés": "Alaves",
    "CD Leganés": "Leganes",
}

def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db}")

def get_clean_name(name):
    """Checks the mapping dictionary, then performs standard cleaning."""
    if name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[name]
    # Remove common suffixes for better fuzzy matching
    clean = name.replace(' FC', '').replace('AFC ', '').replace('CF ', '').replace('UD ', '').strip()
    return clean

def parse_coords(coord_str):
    """Parses coordinate strings like '48.6685° N' into floats."""
    if pd.isna(coord_str): return None
    # Extract number and direction
    match = re.search(r"(\d+\.\d+).*([NSEW])", str(coord_str))
    if match:
        val = float(match.group(1))
        direction = match.group(2)
        if direction in ['S', 'W']: val = -val
        return val
    return None

def enrich_database():
    engine = get_db_engine()
    shorthands = ['pl', 'bl', 'll', 'sa', 'l1']
    
    with engine.connect() as conn:
        # 1. Update Coordinates League by League
        print("--- Updating Coordinates ---")
        for sh in shorthands:
            file_name = f'data/coordinates_{sh}_22_24.csv'
            if not os.path.exists(file_name):
                print(f"Skipping {sh}: File {file_name} not found.")
                continue
            
            print(f"Processing coordinates for: {sh.upper()}")
            df_coords = pd.read_csv(file_name)
            
            for _, row in df_coords.iterrows():
                db_name = get_clean_name(row['Team'])
                conn.execute(text("""
                    UPDATE teams 
                    SET latitude = :lat, longitude = :lon 
                    WHERE name LIKE :name OR name = :exact
                """), {
                    "lat": parse_coords(row['Latitude']), 
                    "lon": parse_coords(row['Longitude']), 
                    "name": f"%{db_name}%",
                    "exact": row['Team']
                })
        
        # 2. Update Transfer Data from the Master CSV
        print("\n--- Processing Transfer Data ---")
        transfer_file = 'data/leagues_transfer_financials_22_24.csv'
        if os.path.exists(transfer_file):
            df_transfers = pd.read_csv(transfer_file)
            db_teams = pd.read_sql("SELECT team_id, name FROM teams", engine)
            
            success_count = 0
            for _, row in df_transfers.iterrows():
                target_name = get_clean_name(row['Club'])
                
                # Match team name against DB teams
                match = db_teams[db_teams['name'].str.contains(target_name, case=False, na=False)]
                
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
                    print(f"⚠️ Warning: Team '{row['Club']}' not found in DB.")
            
            conn.commit()
            print(f"✅ Success! {success_count} financial records processed.")
        else:
            print(f"❌ Error: Master transfer file {transfer_file} not found.")

if __name__ == "__main__":
    enrich_database()