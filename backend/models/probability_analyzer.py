import json
from collections import defaultdict
from cached_form_calculator import CachedFormCalculator

class ProbabilityAnalyzer:
    def __init__(self):
        self.cache_calc = CachedFormCalculator()
        self.matches = self.load_historical_data()
    
    def load_historical_data(self):
        """Load match data"""
        with open('24-25_fixtures.json', 'r') as f:
            return json.load(f)
    
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
        
        for match in self.matches:
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            winner = match['score']['winner']

            home_form = self.cache_calc.get_team_form(home_team)
            away_form = self.cache_calc.get_team_form(away_team)
            
            if home_form > 0 and away_form > 0:
                form_diff = home_form - away_form
                form_diff_rounded = round(2 * form_diff) / 2

                if winner == 'HOME_TEAM':
                    outcome = 'HOME_WIN'
                elif winner == 'AWAY_TEAM':
                    outcome = 'AWAY_WIN'
                else:
                    outcome = 'DRAW'
                
                form_outcomes[form_diff_rounded].append(outcome)
        
        # Calculate probabilities for each form difference
        form_probabilities = {}
        for form_diff, outcomes in form_outcomes.items():
            total = len(outcomes)
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
        print("Analyzing 2024-25 Premier League data...")
        
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
                'season': '2024-25',
                'total_matches': basic_probs['total_matches']
            }
        }
        
        with open('prediction_model_24-25.json', 'w') as f:
            json.dump(model, f, indent=2)
        
        print(f"\nPrediction model saved to prediction_model_24-25")
        return model

if __name__ == "__main__":
    analyzer = ProbabilityAnalyzer()
    model = analyzer.generate_prediction_model()