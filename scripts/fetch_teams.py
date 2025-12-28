import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    return create_engine(url)

def fetch_and_save_teams():
    engine = get_db_engine()
    api_key = os.getenv("FOOTBALL_API_KEY")
    
    # API Endpoint for Premier League (39) Teams in 2023
    url = "https://v3.football.api-sports.io/teams?league=39&season=2023"
    headers = {'x-apisports-key': api_key}
    
    try:
        print("Fetching team data from API...")
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if not data.get('response'):
            print("❌ No data received from API. Check your API key or limits.")
            return

        teams_list = []
        for item in data['response']:
            t = item['team']
            v = item['venue']
            
            teams_list.append({
                'team_id': t['id'],
                'name': t['name'],
                'city': v['city'],
                'stadium_name': v['name'],
                'stadium_capacity': v['capacity'],
                'latitude': None,  # We will fill these in later for geographic viz
                'longitude': None
            })
        
        df_teams = pd.DataFrame(teams_list)
        
        # Use 'multi' method for faster insertion
        # 'if_exists=append' combined with 'team_id' as Primary Key 
        # means you might need to handle duplicates if you run this for multiple seasons.
        # For now, we fetch 2023 to get the 20 teams.
        
        df_teams.to_sql('teams', con=engine, if_exists='append', index=False, method='multi')
        print(f"✅ Successfully inserted {len(df_teams)} teams into the database.")
        
    except Exception as e:
        print(f"❌ Error during team ingestion: {e}")

if __name__ == "__main__":
    fetch_and_save_teams()