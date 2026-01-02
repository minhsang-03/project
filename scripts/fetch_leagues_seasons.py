import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

def get_db_engine():
    """Creates a SQLAlchemy engine using credentials from .env"""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    
    # Connection string for MySQL
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    return create_engine(url)

def initialize_static_data():
    engine = get_db_engine()
    
    try:
        with engine.connect() as conn:
            # 1. Insert Premier League (using text() for safety)
            # We use INSERT IGNORE to avoid errors if the script is run twice
            conn.execute(
                text("INSERT IGNORE INTO leagues (league_id, name, country) VALUES (:id, :name, :country)"),
                {"id": 39, "name": "Premier League", "country": "England"}
            )
            
            # 2. Prepare Seasons Data
            # Note: 2020 represents the 2020/21 season; the three seasons are the only available seasons in the API data source.
            seasons_to_add = [2021, 2022, 2023]
            
            for year in seasons_to_add:
                # Check if season already exists to avoid duplicates
                result = conn.execute(
                    text("SELECT season_id FROM seasons WHERE league_id = 39 AND year = :year"),
                    {"year": year}
                ).fetchone()
                
                if not result:
                    conn.execute(
                        text("INSERT INTO seasons (league_id, year) VALUES (:lib, :year)"),
                        {"lib": 39, "year": year}
                    )
            
            conn.commit()
            print("✅ Successfully initialized Leagues and Seasons.")
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")

if __name__ == "__main__":
    initialize_static_data()