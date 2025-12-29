import os
import requests
import pandas as pd
import time
from sqlalchemy import create_engine
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

def fetch_and_save_performance():
    engine = get_db_engine()
    api_key = os.getenv("FOOTBALL_API_KEY")
    headers = {'x-apisports-key': api_key}
    
    # Focus on the seasons you selected
    seasons = [2021, 2022, 2023]
    league_id = 39 

    all_records = []

    for season in seasons:
        print(f"Fetching standings for {season}...")
        url = f"https://v3.football.api-sports.io/standings?league={league_id}&season={season}"
        
        try:
            response = requests.get(url, headers=headers).json()
            # Navigate API structure: response -> [0] -> league -> standings -> [0]
            standings = response['response'][0]['league']['standings'][0]
            
            for entry in standings:
                rank = entry['rank']
                all_records.append({
                    'team_id': entry['team']['id'],
                    'season_year': season,
                    'points': entry['points'],
                    'final_position': rank,
                    'is_top_5': 1 if rank <= 5 else 0, # Our target variable
                    'wins': entry['all']['win'],
                    'draws': entry['all']['draw'],
                    'losses': entry['all']['lose'],
                    'goals_for': entry['all']['goals']['for'],
                    'goals_against': entry['all']['goals']['against']
                })
            time.sleep(2) # Respect rate limits
        except Exception as e:
            print(f"Error in season {season}: {e}")

    if all_records:
        df = pd.DataFrame(all_records)
        df.to_sql('team_season_performance', con=engine, if_exists='append', index=False)
        print(f"Successfully loaded {len(df)} performance records.")

if __name__ == "__main__":
    fetch_and_save_performance()