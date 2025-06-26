import json
from collections import defaultdict
from cached_form_calculator import CachedFormCalculator

class ProbabilityAnalyzer:
    def __init__(self):
        self.cache_calc = CachedFormCalculator()
        self.matches = self.load_historical_data()
    
    def load_historical_data(self):
        """Load match data"""
        with open('premier_league_historical.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['matches']  # Access the 'matches' key instead of returning the whole object
    
    def calculate_team_form(self, team_name, match_date, num_games=5):
        """Calculate team form based on last N games before the given date"""
        team_matches = []
        
        # Get all matches for this team before the current match date
        for match in self.matches:
            if match['date'] < match_date:  # Only look at previous matches
                if match['homeTeam']['name'] == team_name or match['awayTeam']['name'] == team_name:
                    team_matches.append(match)
        
        # Sort by date (most recent first) and take last N games
        team_matches.sort(key=lambda x: x['date'], reverse=True)
        recent_matches = team_matches[:num_games]
        
        if len(recent_matches) < 3:  # Need minimum matches for reliable form
            return None
            
        # Calculate points from recent matches (3 for win, 1 for draw, 0 for loss)
        points = 0
        for match in recent_matches:
            winner = match['score']['winner']
            if winner == 'DRAW':
                points += 1
            elif (winner == 'HOME_TEAM' and match['homeTeam']['name'] == team_name) or \
                 (winner == 'AWAY_TEAM' and match['awayTeam']['name'] == team_name):
                points += 3
            # Loss = 0 points
        
        # Return form as points per game
        return points / len(recent_matches)
    
    def calculate_basic_probabilities(self):
        """Calculate base home/away/draw rates"""
        total_matches = len(self.matches)
        home_wins = sum(1 for m in self.matches if m['score']['winner'] == 'HOME_TEAM')
        away_wins = sum(1 for m in self.matches if m['score']['winner'] == 'AWAY_TEAM') 
        draws = sum(1 for m in self.matches if m['score']['winner'] == 'DRAW')
        
        return {
            'home_win_rate': home_wins / total_matches,
            'away_win_rate': away_wins / total_matches,
            'draw_rate': draws / total_matches,
            'total_matches': total_matches
        }
    
    def analyze_form_impact(self):
        """Analyze how form difference affects results"""
        form_outcomes = defaultdict(list)
        processed_matches = 0
        
        # Sort matches by date to ensure chronological order
        sorted_matches = sorted(self.matches, key=lambda x: x['date'])
        
        for i, match in enumerate(sorted_matches):
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            winner = match['score']['winner']
            match_date = match['date']

            # Calculate form based on historical data up to this match
            home_form = self.calculate_team_form(home_team, match_date)
            away_form = self.calculate_team_form(away_team, match_date)
            
            if home_form is not None and away_form is not None:
                form_diff = home_form - away_form
                form_diff_rounded = round(4 * form_diff) / 4  # Round to nearest 0.25

                if winner == 'HOME_TEAM':
                    outcome = 'HOME_WIN'
                elif winner == 'AWAY_TEAM':
                    outcome = 'AWAY_WIN'
                else:
                    outcome = 'DRAW'
                
                form_outcomes[form_diff_rounded].append(outcome)
                processed_matches += 1
        
        print(f"Processed {processed_matches} matches with form data")
        
        # Calculate probabilities for each form difference
        form_probabilities = {}
        for form_diff, outcomes in form_outcomes.items():
            total = len(outcomes)
            if total >= 5:  # Only include form differences with enough samples
                home_wins = outcomes.count('HOME_WIN')
                away_wins = outcomes.count('AWAY_WIN')
                draws = outcomes.count('DRAW')
                
                form_probabilities[form_diff] = {
                    'home_win_prob': home_wins / total,
                    'away_win_prob': away_wins / total,
                    'draw_prob': draws / total,
                    'sample_size': total
                }
        
        return form_probabilities
    
    def generate_prediction_model(self):
        """Create the complete prediction model"""
        print("Analyzing 4 season Premier League data...")
        
        basic_probs = self.calculate_basic_probabilities()
        print(f"\nBasic probabilities from {basic_probs['total_matches']} matches:")
        print(f"Home wins: {basic_probs['home_win_rate']:.1%}")
        print(f"Away wins: {basic_probs['away_win_rate']:.1%}")
        print(f"Draws: {basic_probs['draw_rate']:.1%}")
        
        form_analysis = self.analyze_form_impact()
        print(f"\nForm impact analysis:")

        sorted_form = sorted(form_analysis.items())
        print("Form Diff | Home% | Away% | Draw% | Samples")
        print("-" * 45)
        for form_diff, probs in sorted_form:
            if probs['sample_size'] >= 5: 
                print(f"{form_diff:8.1f} | {probs['home_win_prob']:4.1%} | "
                      f"{probs['away_win_prob']:4.1%} | {probs['draw_prob']:4.1%} | "
                      f"{probs['sample_size']:7}")

        model = {
            'basic_probabilities': basic_probs,
            'form_probabilities': form_analysis,
            'metadata': {
                'season': '2028-2023',
                'total_matches': basic_probs['total_matches']
            }
        }
        
        with open('prediction_model_18-23.json', 'w') as f:
            json.dump(model, f, indent=2)
        
        print(f"\nPrediction model saved to prediction_model_18-23")
        return model

if __name__ == "__main__":
    analyzer = ProbabilityAnalyzer()
    model = analyzer.generate_prediction_model()