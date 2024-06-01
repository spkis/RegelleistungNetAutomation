# fcr_results/fcr_results.py

import requests
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
from io import BytesIO

def download_data():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://www.regelleistung.net/apps/cpp-publisher/api/v1/download/tenders/resultsoverview?date={today}&exportFormat=xlsx&market=CAPACITY&productTypes=FCR"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the download failed
    print(f"Data downloaded for {today}")
    return BytesIO(response.content)

def process_data(file_content, hourly=True):
    # Lesen Sie die Excel-Daten aus dem im Speicher befindlichen Inhalt
    df = pd.read_excel(file_content)
    
    # Sicherstellen, dass alle relevanten Felder float sind
    for col in df.columns:
        if "MW" in col or "EUR" in col:
            df[col] = df[col].astype(float, errors='ignore')
    
    # Konvertieren Sie die DATE_FROM-Spalte in einen String
    df['DATE_FROM'] = df['DATE_FROM'].astype(str)

    countries = ['AUSTRIA', 'BELGIUM', 'DENMARK', 'FRANCE', 'GERMANY', 'NETHERLANDS', 'SLOVENIA', 'SWITZERLAND', 'CZECH_REPUBLIC']
    country_data = []

    # Hinzufügen der neuen Logik für das Zeitfeld und Umstrukturierung der Daten für jedes Land
    for index, row in df.iterrows():
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
            if hourly:
                for hour in time_ranges[product_name]:
                    for country in countries:
                        new_row = {
                            'timestamp': (date_from + timedelta(hours=hour)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                            'measurement': 'fcr_results',
                            'country': country.lower(),
                            'demand': row[f'{country}_DEMAND_[MW]'],
                            'price': row[f'{country}_SETTLEMENTCAPACITY_PRICE_[EUR/MW]'],
                            'deficit_surplus': row[f'{country}_DEFICIT(-)_SURPLUS(+)_[MW]']
                        }
                        country_data.append(new_row)
            else:
                start_hour = time_ranges[product_name].start
                end_hour = time_ranges[product_name].stop
                for country in countries:
                    new_row = {
                        'timestamp': (date_from + timedelta(hours=start_hour)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        'measurement': 'fcr_results',
                        'country': country.lower(),
                        'demand': row[f'{country}_DEMAND_[MW]'],
                        'price': row[f'{country}_SETTLEMENTCAPACITY_PRICE_[EUR/MW]'],
                        'deficit_surplus': row[f'{country}_DEFICIT(-)_SURPLUS(+)_[MW]']
                    }
                    country_data.append(new_row)
    
    new_df = pd.DataFrame(country_data)
    print("Data processed and transformed")
    
    return new_df

def save_data(df):
    today = datetime.today().strftime('%Y%m%d')
    file_name = f"fcr_results_{today}.csv"
    df.to_csv(file_name, index=False)
    print(f"Final data saved to {file_name}")

def main():
    file_content = download_data()
    df = process_data(file_content, hourly=True)  # Setzen Sie hourly=False, um vierstündliche Daten zu verwenden
    save_data(df)
    return df

def schedule_daily_run():
    schedule.every().day.at("10:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
