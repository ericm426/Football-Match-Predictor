import requests
import json
import os 
from dotenv import load_dotenv

load_dotenv()

class FootballDataAPI:
    """Class for Data API
    """
    def __init__(self):
        """init with url, api key and headers
        """
        self.base_url = 'https://api.football-data.org/v4'
        self.API_key = os.getenv('FOOTBALL_DATA_API_KEY')
        self.headers = {'X-Auth-Token': self.API_key}
    
    def get_comps(self):
        """Get football competitions"""
        url = f"{self.base_url}/competitions"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {f"error: API Error Code: {response.status_code}"} 
        
    def get_teams(self, competition_id=2021): #2021 is PL check documentation for all codes: https://docs.football-data.org/general/v4/lookup_tables.html#_league_codes
        """Get football teams from comps

        Args:
            competition_id (_type_): _description_
        """
        url = f"{self.base_url}/competitions/{competition_id}/teams"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            return (f"error: API Error Code: {response.status_code}")
    
    
    def get_matches(self, team_id, limit = 10):
        """Get matches based on team_id 

        Args:
            team_id (_type_): _description_
            limits (int, optional): _description_. Defaults to 10.
        """
        url = f"{self.base_url}/teams/{team_id}/matches"
        params= {'limit': limit} #10 calls/min limit for free version
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return (f"error: API Error Code: {response.status_code}")
        
def test_api():
    """api test
    """
    api = FootballDataAPI()
    teams = api.get_teams()

    if 'error' in teams:
        print(f"Error: {teams['error']}")
        return False
    
    print("API working: Success")
    for team in teams['teams'][:5]:
        print(f"Team Name: {team['name']}")
    
    return True

if __name__ == "__main__":
    test_api()


