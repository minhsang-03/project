import os
import requests
import pandas as pd
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_engine():
    """Initializes the connection to the MySQL database."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    return create_engine(url)

def fetch_and_save_matches_multi_league():
    """
    Fetches all match fixtures for the Top 5 leagues and 
    stores them with links to the internal season_id.
    """
    engine = get_db_engine()
    api_key = os.getenv("FOOTBALL_API_KEY")
    headers = {'x-apisports-key': api_key}
    
    # Target Configuration
    league_ids = [39, 78, 140, 135, 61]
    seasons = [2022, 2023, 2024]

    for league_id in league_ids:
        # 1. Map years to internal DB season_ids for THIS league
        # This ensures the Foreign Key constraints are respected.
        season_map = {}
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT season_id, year FROM seasons WHERE league_id = :lid"),
                {"lid": league_id}
            )
            for row in result:
                season_map[row.year] = row.season_id

        for year in seasons:
            if year not in season_map:
                print(f"⚠️ Skipping League {league_id} Year {year}: Season record not found in DB.")
                continue

            print(f"--- Fetching Matches: League {league_id} | Season {year} ---")
            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={year}"
            
            try:
                response = requests.get(url, headers=headers).json()
                
                if not response.get('response'):
                    print(f"⚠️ No match data found for League {league_id} in {year}.")
                    continue

                matches_batch = []
                for item in response['response']:
                    f = item['fixture']
                    t = item['teams']
                    g = item['goals']
                    
                    matches_batch.append({
                        'match_id': f['id'],
                        'season_id': season_map[year],
                        'date': f['date'].split('T')[0],
                        'home_team_id': t['home']['id'],
                        'away_team_id': t['away']['id'],
                        'home_goals': g['home'] if g['home'] is not None else 0,
                        'away_goals': g['away'] if g['away'] is not None else 0,
                        'match_status': f['status']['short']
                    })
                
                # 2. Bulk Insert using INSERT IGNORE
                if matches_batch:
                    df_matches = pd.DataFrame(matches_batch)
                    with engine.begin() as conn:
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
                    print(f"✅ Inserted {len(matches_batch)} matches.")
                
                # Sleep to prevent API rate limiting
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Error in League {league_id}, Season {year}: {e}")

if __name__ == "__main__":
    fetch_and_save_matches_multi_league()