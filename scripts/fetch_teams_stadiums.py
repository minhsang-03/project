import os
import requests
import pandas as pd
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load credentials
load_dotenv()

def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    return create_engine(url)

def fetch_and_save_teams_with_history():
    engine = get_db_engine()
    api_key = os.getenv("FOOTBALL_API_KEY")
    headers = {'x-apisports-key': api_key}
    
    # Using your 3 confirmed seasons
    seasons = [2021, 2022, 2023]
    league_id = 39

    for season in seasons:
        print(f"--- Processing Season {season} ---")
        url = f"https://v3.football.api-sports.io/teams?league={league_id}&season={season}"
        
        try:
            response = requests.get(url, headers=headers).json()
            
            if not response.get('response'):
                print(f"⚠️ No data for {season}. Skipping...")
                continue

            teams_batch = []
            history_batch = []

            for item in response['response']:
                t = item['team']
                v = item['venue']
                
                # 1. Prepare data for 'teams' table (Static)
                teams_batch.append({
                    'team_id': t['id'],
                    'name': t['name'],
                    'city': v['city'],
                    'latitude': None, # To be enriched later
                    'longitude': None
                })

                # 2. Prepare data for 'team_stadium_history' (Historical)
                history_batch.append({
                    'team_id': t['id'],
                    'season_year': season,
                    'stadium_name': v['name'],
                    'stadium_capacity': v['capacity']
                })

            # Convert to DataFrames
            df_teams = pd.DataFrame(teams_batch).drop_duplicates(subset=['team_id'])
            df_history = pd.DataFrame(history_batch)

            # Insert Teams (Using INSERT IGNORE logic via SQL to avoid duplicates across seasons)
            with engine.connect() as conn:
                for _, row in df_teams.iterrows():
                    conn.execute(text("""
                        INSERT IGNORE INTO teams (team_id, name, city, latitude, longitude)
                        VALUES (:id, :name, :city, :lat, :lon)
                    """), {"id": row['team_id'], "name": row['name'], "city": row['city'], "lat": None, "lon": None})
                
                # Insert Stadium History
                df_history.to_sql('team_stadium_history', con=engine, if_exists='append', index=False, method='multi')
                conn.commit()

            print(f"✅ Season {season}: Added {len(df_teams)} teams and their stadium info.")
            
            # Rate limiting for Free Tier (10 requests per minute)
            time.sleep(6) 
            
        except Exception as e:
            print(f"❌ Error in {season}: {e}")

if __name__ == "__main__":
    fetch_and_save_teams_with_history()