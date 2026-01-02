import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_engine():
    """Creates a SQLAlchemy engine using credentials from .env"""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    
    # Connection string for MySQL using the pymysql driver
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    return create_engine(url)

def initialize_static_data():
    """Populates the database with the top 5 European leagues and the target seasons."""
    engine = get_db_engine()
    
    # Configuration for the Top 5 European Leagues (API-Football IDs)
    leagues_data = [
        {"id": 39, "name": "Premier League", "country": "England"},
        {"id": 78, "name": "Bundesliga", "country": "Germany"},
        {"id": 140, "name": "La Liga", "country": "Spain"},
        {"id": 135, "name": "Serie A", "country": "Italy"},
        {"id": 61, "name": "Ligue 1", "country": "France"}
    ]
    
    # Seasons targeted for the study (2021/22, 2022/23, 2023/24)
    seasons_to_add = [2021, 2022, 2023]
    
    try:
        with engine.connect() as conn:
            # 1. Insert Leagues
            print("Processing leagues...")
            for league in leagues_data:
                # INSERT IGNORE prevents errors if the league already exists in the table
                conn.execute(
                    text("INSERT IGNORE INTO leagues (league_id, name, country) VALUES (:id, :name, :country)"),
                    {"id": league["id"], "name": league["name"], "country": league["country"]}
                )
            
            # 2. Insert Seasons for each league
            print("Processing seasons...")
            for league in leagues_data:
                for year in seasons_to_add:
                    # Check if the specific league/year combination already exists to avoid duplicates
                    # This is necessary because season_id is an auto-increment primary key
                    check_query = text("SELECT season_id FROM seasons WHERE league_id = :lid AND year = :year")
                    result = conn.execute(check_query, {"lid": league["id"], "year": year}).fetchone()
                    
                    if not result:
                        conn.execute(
                            text("INSERT INTO seasons (league_id, year) VALUES (:lid, :year)"),
                            {"lid": league["id"], "year": year}
                        )
            
            conn.commit()
            print("✅ Successfully initialized all 5 leagues and their seasons.")
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")

if __name__ == "__main__":
    initialize_static_data()