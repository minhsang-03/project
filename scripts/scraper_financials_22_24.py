import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def clean_value(val):
    """
    Converts Transfermarkt strings (e.g., '€150.00m', '€500k') into float numbers.
    """
    if not val or not isinstance(val, str) or val == '-' or '?' in val:
        return 0.0
    
    multiplier_sign = -1 if '-' in val else 1
    clean_str = val.replace('€', '').replace('-', '').replace('+', '').strip()
    
    if 'm' in clean_str:
        return float(clean_str.replace('m', '')) * 1_000_000 * multiplier_sign
    elif 'k' in clean_str:
        return float(clean_str.replace('k', '')) * 1_000 * multiplier_sign
    
    try:
        return float(clean_str) * multiplier_sign
    except ValueError:
        return 0.0

def scrape_transfer_financials(seasons):
    all_data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Dictionary of Top 5 Leagues and their Transfermarkt codes
    leagues = {
        'Premier League': 'GB1',
        'Bundesliga': 'L1',
        'La Liga': 'ES1',
        'Serie A': 'IT1',
        'Ligue 1': 'FR1'
    }

    for league_name, league_code in leagues.items():
        for season in seasons:
            print(f"Scraping {league_name} - Season {season}...")
            # The URL now uses the dynamic league_code
            url = f"https://www.transfermarkt.com/wettbewerb/einnahmenausgaben/wettbewerb/{league_code}/plus/1?saison_id={season}&saison_id_bis={season}"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"Failed to fetch {league_name} {season}")
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', class_='items')
                
                if not table:
                    print(f"No table found for {league_name} {season}")
                    continue
                    
                rows = table.find('tbody').find_all('tr')

                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 8: 
                        club_name = cols[2].text.strip()
                        raw_exp = cols[4].text.strip() 
                        raw_inc = cols[6].text.strip()      
                        raw_bal = cols[8].text.strip()     
                        
                        all_data.append({
                            'League': league_name,
                            'Season': season,
                            'Club': club_name,
                            'Expenditure': clean_value(raw_exp),
                            'Income': clean_value(raw_inc),
                            'Net Balance': clean_value(raw_bal)
                        })
                
                # Sleep to be respectful and avoid getting blocked
                time.sleep(3)
                
            except Exception as e:
                print(f"Error scraping {league_name} in {season}: {e}")

    return all_data

# --- Execution ---
seasons_to_scrape = ['2022', '2023', '2024']
results = scrape_transfer_financials(seasons_to_scrape)

df = pd.DataFrame(results)

# Save to the data folder
os.makedirs('data', exist_ok=True)
file_path = 'data/leagues_transfer_financials_22_24.csv'
df.to_csv(file_path, index=False)

print(f"\n✅ Successfully exported {len(df)} rows to {file_path}")