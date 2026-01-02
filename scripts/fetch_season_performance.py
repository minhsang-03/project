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

def fetch_and_save_performance():
    """
    Fetches league standings for all Top 5 leagues and saves 
    performance metrics including the target variable (is_top_5).
    """
    engine = get_db_engine()
    api_key = os.getenv("FOOTBALL_API_KEY")
    headers = {'x-apisports-key': api_key}
    
    # League IDs: 39=PL, 78=Bundesliga, 140=La Liga, 135=Serie A, 61=Ligue 1
    league_ids = [39, 78, 140, 135, 61]
    seasons = [2022, 2023, 2024]

    for league_id in league_ids:
        for season in seasons:
            print(f"--- Fetching Standings: League {league_id} | Season {season} ---")
            url = f"https://v3.football.api-sports.io/standings?league={league_id}&season={season}"
            
            try:
                response = requests.get(url, headers=headers).json()
                
                # The API returns standings in a nested list structure
                if not response.get('response') or not response['response'][0]['league']['standings']:
                    print(f"⚠️ No standings found for League {league_id} in {season}.")
                    continue

                # European leagues have only one group/table [0]
                standings = response['response'][0]['league']['standings'][0]
                
                for entry in standings:
                    rank = entry['rank']
                    team_id = entry['team']['id']
                    
                    with engine.begin() as conn:
                        # We use INSERT ... ON DUPLICATE KEY UPDATE to allow script re-runs
                        # without creating duplicate records for the same team and season.
                        conn.execute(text("""
                            INSERT INTO team_season_performance 
                            (team_id, season_year, points, final_position, is_top_5, wins, draws, losses, goals_for, goals_against)
                            VALUES (:tid, :y, :pts, :rank, :top5, :w, :d, :l, :gf, :ga)
                            ON DUPLICATE KEY UPDATE 
                                points = VALUES(points),
                                final_position = VALUES(final_position),
                                is_top_5 = VALUES(is_top_5),
                                wins = VALUES(wins),
                                draws = VALUES(draws),
                                losses = VALUES(losses),
                                goals_for = VALUES(goals_for),
                                goals_against = VALUES(goals_against)
                        """), {
                            "tid": team_id,
                            "y": season,
                            "pts": entry['points'],
                            "rank": rank,
                            "top5": 1 if rank <= 5 else 0,
                            "w": entry['all']['win'],
                            "d": entry['all']['draw'],
                            "l": entry['all']['lose'],
                            "gf": entry['all']['goals']['for'],
                            "ga": entry['all']['goals']['against']
                        })
                
                print(f"✅ Successfully processed {len(standings)} teams for League {league_id}.")
                time.sleep(2) # Modest sleep to stay within API limits
                
            except Exception as e:
                print(f"❌ Error in League {league_id}, Season {season}: {e}")

if __name__ == "__main__":
    fetch_and_save_performance()