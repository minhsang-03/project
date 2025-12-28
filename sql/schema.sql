CREATE DATABASE IF NOT EXISTS football_project;
USE football_project;

-- 1. Leagues Table
CREATE TABLE leagues (
    league_id INT PRIMARY KEY,
    name VARCHAR(100),
    country VARCHAR(100)
);

-- 2. Seasons Table
CREATE TABLE seasons (
    season_id INT AUTO_INCREMENT PRIMARY KEY,
    league_id INT,
    year INT,
    FOREIGN KEY (league_id) REFERENCES leagues(league_id)
);

-- 3. Teams Table (Updated with Stadium Info)
CREATE TABLE teams (
    team_id INT PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(100),
    stadium_name VARCHAR(100),
    stadium_capacity INT,
    latitude DECIMAL(10, 8), 
    longitude DECIMAL(11, 8)
);

-- 4. Matches Table (Updated with Season Foreign Key)
CREATE TABLE matches (
    match_id INT PRIMARY KEY,
    season_id INT,
    date DATE,
    home_team_id INT,
    away_team_id INT,
    home_goals INT,
    away_goals INT,
    match_status VARCHAR(50),
    FOREIGN KEY (season_id) REFERENCES seasons(season_id),
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);

-- 5. Team Season Performance (Target Variable)
CREATE TABLE team_season_performance (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT,
    season_year INT,
    points INT,
    final_position INT,
    is_top_5 BOOLEAN,
    wins INT,
    draws INT,
    losses INT,
    goals_for INT,
    goals_against INT,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- 6. Team Enrichment Data (Simplified: Removed squad size)
CREATE TABLE team_enrichment_data (
    enrichment_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT,
    season_year INT,
    transfer_spend_euro DECIMAL(15, 2),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- 7. League Season Stats
CREATE TABLE league_season_stats (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    league_id INT,
    season_year INT,
    avg_goals_per_game DECIMAL(5, 2),
    home_win_percentage DECIMAL(5, 2),
    FOREIGN KEY (league_id) REFERENCES leagues(league_id)
);