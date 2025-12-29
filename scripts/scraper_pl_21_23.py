import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def clean_value(val):
    """
    Handles conversion of strings like '€150.00m', '€500k', or '€-10.5m' 
    into float numbers.
    """
    if not val or not isinstance(val, str) or val == '-' or '?' in val:
        return 0.0
    
    # Identify if it's a negative value
    multiplier_sign = -1 if '-' in val else 1
    
    # Remove currency, signs, and spaces
    clean_str = val.replace('€', '').replace('-', '').replace('+', '').strip()
    
    # Apply multipliers
    if 'm' in clean_str:
        return float(clean_str.replace('m', '')) * 1_000_000 * multiplier_sign
    elif 'k' in clean_str:
        return float(clean_str.replace('k', '')) * 1_000 * multiplier_sign
    
    try:
        return float(clean_str) * multiplier_sign
    except ValueError:
        return 0.0

def scrape_transfer_spending(seasons):
    all_data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for season in seasons:
        print(f"Scraping season {season}...")
        url = f"https://www.transfermarkt.com/premier-league/einnahmenausgaben/wettbewerb/GB1/ids/a/sa//saison_id/{season}/saison_id_bis/{season}/nat/0/pos//w_s//intern/0/plus/1"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch season {season}")
            continue
            
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='items')
        
        if not table:
            continue
            
        rows = table.find('tbody').find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 8: # Ensure row has enough columns
                # Extracting raw text
                club_name = cols[2].text.strip()
                raw_exp = cols[4].text.strip() 
                raw_inc = cols[6].text.strip()      
                raw_bal = cols[8].text.strip()     
                
                all_data.append({
                    'Season': f"{season}",
                    'Club': club_name,
                    'Expenditure': clean_value(raw_exp),
                    'Income': clean_value(raw_inc),
                    'Net Balance': clean_value(raw_bal)
                })
        
        time.sleep(2)

    return all_data

# --- Execution ---
seasons_to_scrape = ['2021', '2022', '2023']
scraped_results = scrape_transfer_spending(seasons_to_scrape)

# Convert to DataFrame
df = pd.DataFrame(scraped_results)

# Create 'data' folder if it doesn't exist
folder_name = 'data'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Export to CSV
file_path = os.path.join(folder_name, 'pl_transfer_spending_21_23.csv')
df.to_csv(file_path, index=False)

print(f"Data exported successfully to {file_path}")