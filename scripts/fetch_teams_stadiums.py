import os
import requests
import pandas as pd
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_db_engine():
    user, pw, host, db = os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"), os.getenv("DB_NAME")
    # Using 'pool_pre_ping' helps manage stale connections
    return create_engine(f"mysql+pymysql://{user}:{pw}@{host}/{db}", pool_pre_ping=True)

def fetch_and_save_teams_multi_league():
    engine = get_db_engine()
    api_key = os.getenv("FOOTBALL_API_KEY")
    headers = {'x-apisports-key': api_key}
    
    league_ids = [39, 61, 78, 135, 140]
    seasons = [2022, 2023, 2024]

    for league_id in league_ids:
        for season in seasons:
            print(f"--- Processing League ID {league_id} | Season {season} ---")
            url = f"https://v3.football.api-sports.io/teams?league={league_id}&season={season}"
            
            try:
                response = requests.get(url, headers=headers).json()
                if not response.get('response'):
                    print(f"⚠️ No data found for League {league_id} in {season}.")
                    continue

                for item in response['response']:
                    t = item['team']
                    v = item['venue']
                    
                    # Using a context manager (with engine.begin()) ensures 
                    # that the transaction is committed automatically 
                    # and closed even if an error occurs.
                    with engine.begin() as conn:
                        # 1. Static team data
                        conn.execute(text("""
                            INSERT IGNORE INTO teams (team_id, name, city)
                            VALUES (:id, :name, :city)
                        """), {"id": t['id'], "name": t['name'], "city": v['city']})
                        
                        # 2. Historical stadium data
                        conn.execute(text("""
                            INSERT INTO team_stadium_history (team_id, season_year, stadium_name, stadium_capacity)
                            VALUES (:tid, :y, :sn, :cap)
                            ON DUPLICATE KEY UPDATE stadium_capacity = VALUES(stadium_capacity)
                        """), {
                            "tid": t['id'], 
                            "y": season, 
                            "sn": v['name'], 
                            "cap": v['capacity'] if v['capacity'] else 0
                        })

                print(f"✅ Success: Processed teams for League {league_id} in {season}.")
                time.sleep(2) # Modest sleep to respect API limits
                
            except Exception as e:
                print(f"❌ Error encountered for League {league_id}, Season {season}: {e}")

if __name__ == "__main__":
    fetch_and_save_teams_multi_league()