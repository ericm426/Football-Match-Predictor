import json
### TODO Fix Form Calculator Later down the line bcs its fucked rn and calcs the form of team on last 5 matches of the season
class CachedFormCalculator:
    def __init__(self, cache_file='form_cache.json'):
        self.cache = self.load_cache(cache_file)
    
    def load_cache(self, filename):
        """Load pre-built form cache"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Cache file {filename} not found! Build cache first.")
            return {}
    
    def get_team_form(self, team_name):
        """Get team's representative form score"""
        if team_name in self.cache.get('teams', {}):
            return self.cache['teams'][team_name]['representative_form']['score']
        return 0.0
    
    def get_team_season_stats(self, team_name):
        """Get full season statistics"""
        if team_name in self.cache.get('teams', {}):
            return self.cache['teams'][team_name]['season_stats']
        return None
    
    def compare_teams(self, team1, team2):
        """Quick comparison of two teams"""
        team1_form = self.get_team_form(team1)
        team2_form = self.get_team_form(team2)
        
        return {
            'team1': {'name': team1, 'form': team1_form},
            'team2': {'name': team2, 'form': team2_form},
            'form_advantage': team1_form - team2_form
        }


if __name__ == "__main__":
    calc = CachedFormCalculator()

    arsenal_form = calc.get_team_form("Arsenal FC")
    chelsea_form = calc.get_team_form("Chelsea FC")
    
    print(f"Arsenal form: {arsenal_form:.2f}")
    print(f"Chelsea form: {chelsea_form:.2f}")
    
    comparison = calc.compare_teams("Arsenal FC", "Chelsea FC")
    print(f"Form comparison: {comparison}")