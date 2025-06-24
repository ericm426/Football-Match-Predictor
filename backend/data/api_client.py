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
    
    
    def get_matches(self, team_id, limit = 5):
        """Get matches based on team_id 

        Args:
            team_id (_type_): _description_
            limits (int, optional): _description_. Defaults to 10.
        """
        url = f"{self.base_url}/teams/{team_id}/matches"
        params= {
            'limit': limit,
            'status': 'FINISHED',
            'dateFrom': '2023-08-01',
            'dateTo': '2024-06-01'
        } #5 calls for recent form
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return (f"error: API Error Code: {response.status_code}")
    
    def get_id_by_name(self, team_name):
        """Gets the team id by finding using name

        Args:
            team_name (_type_): _description_
        """
        team_data = self.get_teams()

        if 'error' in team_data:
            return None
        
        for team in team_data['teams']:
            if team['name'] == team_name:
                return team['id']
        
        return None

    def get_recent_form(self, team_name, limit=5):
        """Get form from last matches"""
        team_id = self.get_id_by_name(team_name)
        matches_data = self.get_matches(team_id, limit=limit)
        
        if 'matches' not in matches_data or not matches_data['matches']:
            return 0
        
        total_points = 0
        matches_analyzed = 0

        for match in matches_data['matches']:
            winner = match['score']['winner']
            home_team_id = match['homeTeam']['id']
            
            if winner == "DRAW":
                total_points += 1
            elif winner == "HOME_TEAM":
                total_points += 3 if team_id == home_team_id else 0
            elif winner == "AWAY_TEAM":
                total_points += 3 if team_id != home_team_id else 0
            
            matches_analyzed += 1
        
        return total_points / matches_analyzed if matches_analyzed > 0 else 0
    
    def get_season_form(self, team_name, limit=5):
        """Get team form over season"""
        team_id = self.get_id_by_name(team_name)
        if not team_id:
            return 0
        
        url = f"{self.base_url}/teams/{team_id}/matches"
        params = {
            'limit': limit,
            'status': 'FINISHED',
            'dateFrom': '2023-08-01',
            'dateTo': '2024-06-01'
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            result_set = data.get('resultSet', {})
            
            # Extract wins, draws, losses
            wins = result_set.get('wins', 0)
            draws = result_set.get('draws', 0) 
            losses = result_set.get('losses', 0)
            played = result_set.get('played', 0)
            
            if played == 0:
                return 0
            
            # Calculate form score
            total_points = (wins * 3) + (draws * 1) + (losses * 0)
            form_score = total_points / played
            
            return form_score
        return 0
    
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
    
    # Test form calculation
    print("\n--- Testing Form Calculation ---")
    arsenal_form = api.form_calculation("Arsenal FC")
    print(f"Arsenal FC form score: {arsenal_form}")
    
    # Test another team
    chelsea_form = api.form_calculation("Chelsea FC")
    print(f"Chelsea FC form score: {chelsea_form}")

    return True



if __name__ == "__main__":
    test_api()



