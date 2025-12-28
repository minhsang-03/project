import os
import requests
import pandas as pd
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    return create_engine(url)

def fetch_and_save_matches():
    engine = get_db_engine()
    api_key = os.getenv("FOOTBALL_API_KEY")
    headers = {'x-apisports-key': api_key}
    
    # Seasons we are targeting
    seasons = [2021, 2022, 2023]
    league_id = 39

    # 1. Map years to our internal DB season_ids to maintain foreign key integrity
    season_map = {}
    with engine.connect() as conn:
        result = conn.execute(text("SELECT season_id, year FROM seasons WHERE league_id = 39"))
        for row in result:
            season_map[row.year] = row.season_id

    all_matches = []

    for year in seasons:
        print(f"Fetching matches for season {year}...")
        url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={year}"
        
        try:
            response = requests.get(url, headers=headers).json()
            
            if not response.get('response'):
                print(f"⚠️ No match data for {year}.")
                continue

            for item in response['response']:
                f = item['fixture']
                t = item['teams']
                g = item['goals']
                
                all_matches.append({
                    'match_id': f['id'],
                    'season_id': season_map[year], # Uses the internal DB ID
                    'date': f['date'].split('T')[0],
                    'home_team_id': t['home']['id'],
                    'away_team_id': t['away']['id'],
                    'home_goals': g['home'],
                    'away_goals': g['away'],
                    'match_status': f['status']['short']
                })
            
            # Rate limit safety
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Error in season {year}: {e}")

    if all_matches:
        df_matches = pd.DataFrame(all_matches)
        
        # 'match_id' is our primary key, so we use INSERT IGNORE logic
        with engine.connect() as conn:
            for _, row in df_matches.iterrows():
                conn.execute(text("""
                    INSERT IGNORE INTO matches 
                    (match_id, season_id, date, home_team_id, away_team_id, home_goals, away_goals, match_status)
                    VALUES (:mid, :sid, :dt, :ht, :at, :hg, :ag, :status)
                """), {
                    "mid": row['match_id'], "sid": row['season_id'], "dt": row['date'],
                    "ht": row['home_team_id'], "at": row['away_team_id'], 
                    "hg": row['home_goals'], "ag": row['away_goals'], "status": row['match_status']
                })
            conn.commit()
            
        print(f"✅ Successfully inserted {len(df_matches)} matches.")

if __name__ == "__main__":
    fetch_and_save_matches()