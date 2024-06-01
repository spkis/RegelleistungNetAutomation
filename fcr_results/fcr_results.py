# fcr_results/fcr_results.py

import requests
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time

def download_data():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://www.regelleistung.net/apps/cpp-publisher/api/v1/download/tenders/resultsoverview?date={today}&exportFormat=xlsx&market=CAPACITY&productTypes=FCR"
    response = requests.get(url)
    with open('data.xlsx', 'wb') as f:
        f.write(response.content)
    print(f"Data downloaded for {today}")

def convert_xlsx_to_csv():
    df = pd.read_excel('data.xlsx')
    df.to_csv('data.csv', index=False)
    print("Data converted to CSV")

def process_data():
    df = pd.read_csv('data.csv')
    
    # Sicherstellen, dass alle Zahlen als float behandelt werden
    df = df.astype(float, errors='ignore')
    
    # Hinzufügen der neuen Logik für das Zeitfeld
    new_rows = []
    for index, row in df.iterrows():
        # Fehler abfangen, wenn das Datumsformat nicht stimmt
        try:
            date_from = datetime.strptime(row['DATE_FROM'], '%Y-%m-%d')
        except ValueError as e:
            print(f"Error parsing DATE_FROM: {row['DATE_FROM']} - {e}")
            continue
        
        time_ranges = {
            "NEGPOS_00_04": range(0, 4),
            "NEGPOS_04_08": range(4, 8),
            "NEGPOS_08_12": range(8, 12),
            "NEGPOS_12_16": range(12, 16),
            "NEGPOS_16_20": range(16, 20),
            "NEGPOS_20_24": range(20, 24),
        }
        product_name = row['PRODUCTNAME']
        if product_name in time_ranges:
            for hour in time_ranges[product_name]:
                new_row = row.copy()
                new_row['timestamp'] = (date_from + timedelta(hours=hour)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                new_row['measurement'] = 'fcr_results'
                new_rows.append(new_row)
    
    new_df = pd.DataFrame(new_rows)
    print("Data processed and transformed")
    
    return new_df

def save_data(df):
    today = datetime.today().strftime('%Y%m%d')
    file_name = f"Fcr_results_{today}.csv"
    df.to_csv(file_name, index=False)
    print(df)
    print(f"Final data saved to {file_name}")

def main():
    download_data()
    convert_xlsx_to_csv()
    df = process_data()
    save_data(df)
    return df

def schedule_daily_run():
    schedule.every().day.at("00:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
