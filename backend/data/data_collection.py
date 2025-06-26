import json
import time
import requests
from datetime import datetime
from api_client import FootballDataAPI

class HistoricalPLData:
    def __init__(self):
        self.api = FootballDataAPI()
        self.seasons = [
            ('2019-08-01', '2020-07-31', '2019-20'),
            ('2020-09-01', '2021-07-31', '2020-21'),  
            ('2021-08-01', '2022-07-31', '2021-22'),
            ('2022-08-01', '2023-07-31', '2022-23'),
            ('2023-08-01', '2024-07-31', '2023-24'),
        ]

    def collect_season(self, start_date, end_date, season_name):
        print(f"Collecting all season data for PL Season {season_name}")
        url = f"{self.api.base_url}/competitions/PL/matches"
        params = {
            'dateFrom': start_date,
            'dateTo': end_date,
            'status': 'FINISHED'
        }

        try:
            response = requests.get(url, headers=self.api.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data['matches'])} matches for {season_name}")
                return data['matches']
            else:
                print(f"Error collecting {season_name}: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception collecting {season_name}: {e}")
            return []
        
    def collect_all_data(self):
        """Collect data for all seasons"""
        all_matches = []
        
        for start_date, end_date, season_name in self.seasons:
            season_matches = self.collect_season(start_date, end_date, season_name)
            
            for match in season_matches:
                match['season'] = season_name
            
            all_matches.extend(season_matches)

            time.sleep(2)
        
        return all_matches
    
    def save_data(self, matches, filename="22-23_fixtures.json"):
        save_path = 'C:\Users\Eric_\OneDrive\Documents\GitHub\Football-Match-Predictor\backend\data'
        print(f"Saving {len(matches)} to {filename}")
        with open(filename, 'w') as file:
            json.dump(matches, file, indent=2)
        print("File Saved!")

def main():
    """Run the data collection"""
    collector = HistoricalPLData()
    
    print("Starting historical data collection...")
    print("This might take a few minutes...")
    
    # Collect all data
    #matches = collector.collect_all_data()
    season = input("Season: ")
    fixtures23 = collector.collect_season('2022-08-01', '2023-07-31', season)
    # Save to file
    collector.save_data(fixtures23)
    
    print(f"\nCollection complete!")
    print(f"Total matches collected: {len(fixtures23)}")
    print(f"Data saved to: 22-23_fixtures.json")

if __name__ == "__main__":
    main()    