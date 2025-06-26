import json
from collections import defaultdict
from api_client import FootballDataAPI

class FormCacheBuilder:
    def __init__(self):
        self.api = FootballDataAPI()
        self.matches = self.load_historical_data()
        self.teams = self.get_all_teams()
    
    def load_historical_data(self):
        """Load your collected match data"""
        try:
            with open('23-24_PLData.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Historical data not found! Run data_collector.py first.")
            return []
    
    def get_all_teams(self):
        """Get unique teams from historical data"""
        teams = set()
        for match in self.matches:
            teams.add(match['homeTeam']['name'])
            teams.add(match['awayTeam']['name'])
        return sorted(list(teams))
    
    def get_team_matches_chronological(self, team_name):
        """Get all matches for a team in chronological order"""
        team_matches = []
        
        for match in self.matches:
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            
            if team_name == home_team or team_name == away_team:
                team_matches.append({
                    'date': match['utcDate'],
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_goals': match['score']['fullTime']['home'],
                    'away_goals': match['score']['fullTime']['away'],
                    'winner': match['score']['winner'],
                    'is_home': team_name == home_team
                })

        team_matches.sort(key=lambda x: x['date'])
        return team_matches
    
    def calculate_rolling_form(self, team_name, window=5):
        """Calculate form at different points in the season - FIXED VERSION"""
        matches = self.get_team_matches_chronological(team_name)
        form_timeline = []
        
        for i in range(len(matches)):
            # Calculate form BEFORE this match (using previous matches only)
            if i < window:
                # Not enough previous matches, use what we have
                recent_matches = matches[:i]
            else:
                # Use last 'window' matches before this one
                recent_matches = matches[i-window:i]
            
            if not recent_matches:
                form_score = 0.0
            else:
                points = 0
                for match in recent_matches:
                    result = self.get_match_result(match, team_name)
                    if result == 'WIN':
                        points += 3
                    elif result == 'DRAW':
                        points += 1
                
                form_score = points / len(recent_matches)
            
            form_timeline.append({
                'after_match': i + 1,
                'date': matches[i]['date'],
                'form_score': form_score,
                'matches_used': len(recent_matches)
            })
        
        return form_timeline
    
    def get_match_result(self, match, team_name):
        """Determine if team won, drew, or lost"""
        winner = match['winner']
        is_home = match['is_home']
        
        if winner == 'DRAW':
            return 'DRAW'
        elif winner == 'HOME_TEAM':
            return 'WIN' if is_home else 'LOSS'
        elif winner == 'AWAY_TEAM':
            return 'WIN' if not is_home else 'LOSS'
        
        return 'UNKNOWN'
    
    def build_complete_cache(self):
        """Build form cache for all teams"""
        print("Building form cache for all teams...")
        
        cache = {
            'metadata': {
                'created_date': '2024-12-31',  # Update this
                'season': '2023-24',
                'total_teams': len(self.teams),
                'total_matches': len(self.matches)
            },
            'teams': {}
        }
        
        for i, team in enumerate(self.teams):
            print(f"Processing {team} ({i+1}/{len(self.teams)})...")

            team_matches = self.get_team_matches_chronological(team)

            total_matches = len(team_matches)
            wins = sum(1 for m in team_matches if self.get_match_result(m, team) == 'WIN')
            draws = sum(1 for m in team_matches if self.get_match_result(m, team) == 'DRAW')
            losses = sum(1 for m in team_matches if self.get_match_result(m, team) == 'LOSS')
            
            timeline = self.calculate_rolling_form(team)
            if timeline:
                # Use form from matches 10-30 (mid-season, when form is stable)
                mid_season_forms = [t['form_score'] for t in timeline[10:30] if t['matches_used'] >= 5]
                representative_form = sum(mid_season_forms) / len(mid_season_forms) if mid_season_forms else 0
            else:
                representative_form = 0

            cache['teams'][team] = {
                'season_stats': {
                    'matches': total_matches,
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'win_rate': wins / total_matches if total_matches > 0 else 0,
                    'points_per_game': (wins * 3 + draws) / total_matches if total_matches > 0 else 0
                },
                'representative_form': {
                    'score': representative_form,
                    'description': 'Average form from mid-season period'
                },
                'form_timeline': timeline
                }
        
        return cache
    
    def save_cache(self, cache, filename='form_cache.json'):
        """Save cache to file"""
        print(f"Saving cache to {filename}...")
        with open(filename, 'w') as f:
            json.dump(cache, f, indent=2)
        print("Cache saved successfully!")

def main():
    """Build the form cache"""
    builder = FormCacheBuilder()
    
    print("Starting form cache build...")
    cache = builder.build_complete_cache()
    builder.save_cache(cache)

    print(f"\nCache built successfully!")
    print(f"Teams cached: {len(cache['teams'])}")
    print(f"Season: {cache['metadata']['season']}")

if __name__ == "__main__":
    main()