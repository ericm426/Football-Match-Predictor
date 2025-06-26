import json
import os
import glob
from datetime import datetime
from pathlib import Path

class ESPNJSONParser:
    def __init__(self):
        self.parsed_matches = []
        self.stats = {
            'total_files': 0,
            'total_matches': 0,
            'completed_matches': 0,
            'seasons_found': set(),
            'date_range': {'earliest': None, 'latest': None}
        }
    
    def parse_espn_match(self, event):
        """Parse a single ESPN event into our format"""
        try:
            # Get basic match info
            match_data = {
                'id': event.get('id'),
                'date': event.get('date'),
                'name': event.get('name'),
                'shortName': event.get('shortName')
            }
            
            # Get competition data (first competition in the event)
            competition = event.get('competitions', [{}])[0]
            
            # Check if match is completed
            status = competition.get('status', {})
            if not status.get('type', {}).get('completed', False):
                return None  # Skip incomplete matches
            
            # Get teams
            competitors = competition.get('competitors', [])
            if len(competitors) != 2:
                return None  # Skip if we don't have exactly 2 teams
            
            # Identify home and away teams
            home_team = None
            away_team = None
            
            for competitor in competitors:
                if competitor.get('homeAway') == 'home':
                    home_team = competitor
                elif competitor.get('homeAway') == 'away':
                    away_team = competitor
            
            if not home_team or not away_team:
                return None
            
            # Extract team names and scores
            home_team_name = home_team.get('team', {}).get('displayName', '')
            away_team_name = away_team.get('team', {}).get('displayName', '')
            home_score = int(home_team.get('score', 0))
            away_score = int(away_team.get('score', 0))
            
            # Determine winner
            if home_score > away_score:
                winner = 'HOME_TEAM'
            elif away_score > home_score:
                winner = 'AWAY_TEAM'
            else:
                winner = 'DRAW'
            
            # Build match in format expected by ProbabilityAnalyzer
            parsed_match = {
                'homeTeam': {
                    'name': home_team_name,
                    'id': home_team.get('id'),
                    'abbreviation': home_team.get('team', {}).get('abbreviation', '')
                },
                'awayTeam': {
                    'name': away_team_name,
                    'id': away_team.get('id'),
                    'abbreviation': away_team.get('team', {}).get('abbreviation', '')
                },
                'score': {
                    'winner': winner,
                    'homeScore': home_score,
                    'awayScore': away_score
                },
                'date': match_data['date'],
                'venue': competition.get('venue', {}).get('displayName', ''),
                'attendance': competition.get('attendance'),
                'season': event.get('season', {}).get('year'),
                
                # Optional: Include additional data that might be useful
                'statistics': {
                    'home': self._extract_team_stats(home_team),
                    'away': self._extract_team_stats(away_team)
                },
                'match_events': self._extract_match_events(competition),
                
                # Original ESPN data for reference
                '_original_id': event.get('id'),
                '_original_name': event.get('name')
            }
            
            return parsed_match
            
        except Exception as e:
            print(f"Error parsing match: {e}")
            return None
    
    def _extract_team_stats(self, team_data):
        """Extract team statistics from ESPN format"""
        stats = {}
        team_stats = team_data.get('statistics', [])
        
        for stat in team_stats:
            stat_name = stat.get('name', '')
            stat_value = stat.get('displayValue', '')
            stats[stat_name] = stat_value
        
        return stats
    
    def _extract_match_events(self, competition):
        """Extract match events (goals, cards, etc.)"""
        events = []
        details = competition.get('details', [])
        
        for detail in details:
            event = {
                'type': detail.get('type', {}).get('text', ''),
                'clock': detail.get('clock', {}).get('displayValue', ''),
                'team_id': detail.get('team', {}).get('id'),
                'scoring_play': detail.get('scoringPlay', False),
                'red_card': detail.get('redCard', False),
                'yellow_card': detail.get('yellowCard', False),
                'penalty': detail.get('penaltyKick', False),
                'players': [athlete.get('displayName', '') 
                           for athlete in detail.get('athletesInvolved', [])]
            }
            events.append(event)
        
        return events
    
    def parse_json_file(self, file_path):
        """Parse a single ESPN JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stats['total_files'] += 1
            file_matches = 0
            
            # Parse each event in the file
            events = data.get('events', [])
            for event in events:
                parsed_match = self.parse_espn_match(event)
                if parsed_match:
                    self.parsed_matches.append(parsed_match)
                    file_matches += 1
                    self.stats['completed_matches'] += 1
                    
                    # Update statistics
                    if parsed_match.get('season'):
                        self.stats['seasons_found'].add(parsed_match['season'])
                    
                    # Track date range
                    match_date = parsed_match.get('date')
                    if match_date:
                        if not self.stats['date_range']['earliest'] or match_date < self.stats['date_range']['earliest']:
                            self.stats['date_range']['earliest'] = match_date
                        if not self.stats['date_range']['latest'] or match_date > self.stats['date_range']['latest']:
                            self.stats['date_range']['latest'] = match_date
            
            self.stats['total_matches'] += len(events)
            print(f"✓ {os.path.basename(file_path)}: {file_matches} completed matches")
            return file_matches
            
        except Exception as e:
            print(f"✗ Error parsing {file_path}: {e}")
            return 0
    
    def parse_directory(self, directory_path, pattern="*.json"):
        """Parse all ESPN JSON files in a directory"""
        input_dir = Path(directory_path)
        json_files = list(input_dir.glob(pattern))
        
        if not json_files:
            print(f"No JSON files found matching pattern '{pattern}' in {directory_path}")
            return
        
        print(f"Found {len(json_files)} JSON files to parse")
        print("=" * 50)
        
        for json_file in sorted(json_files):
            self.parse_json_file(str(json_file))
        
        self._print_summary()
    
    def _print_summary(self):
        """Print parsing summary"""
        print("\n" + "=" * 50)
        print("PARSING SUMMARY")
        print("=" * 50)
        print(f"Files processed: {self.stats['total_files']}")
        print(f"Total matches found: {self.stats['total_matches']}")
        print(f"Completed matches: {self.stats['completed_matches']}")
        print(f"Seasons found: {sorted(list(self.stats['seasons_found']))}")
        
        if self.stats['date_range']['earliest'] and self.stats['date_range']['latest']:
            print(f"Date range: {self.stats['date_range']['earliest'][:10]} to {self.stats['date_range']['latest'][:10]}")
        
        # Basic outcome statistics
        if self.parsed_matches:
            home_wins = sum(1 for m in self.parsed_matches if m['score']['winner'] == 'HOME_TEAM')
            away_wins = sum(1 for m in self.parsed_matches if m['score']['winner'] == 'AWAY_TEAM')
            draws = sum(1 for m in self.parsed_matches if m['score']['winner'] == 'DRAW')
            total = len(self.parsed_matches)
            
            print(f"\nOutcome Distribution:")
            print(f"Home wins: {home_wins} ({home_wins/total:.1%})")
            print(f"Away wins: {away_wins} ({away_wins/total:.1%})")
            print(f"Draws: {draws} ({draws/total:.1%})")
    
    def save_parsed_data(self, output_file="historical_fixtures.json"):
        """Save parsed matches in format expected by ProbabilityAnalyzer"""
        output_data = {
            'matches': self.parsed_matches,
            'metadata': {
                'total_matches': len(self.parsed_matches),
                'seasons': sorted(list(self.stats['seasons_found'])),
                'date_range': self.stats['date_range'],
                'parsing_stats': self.stats
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Parsed data saved to {output_file}")
        print(f"Format compatible with ProbabilityAnalyzer")
        return output_file
    
    def get_matches_for_analyzer(self):
        """Return matches in the exact format expected by ProbabilityAnalyzer"""
        return self.parsed_matches

# Usage example and integration with ProbabilityAnalyzer
def create_historical_dataset(espn_json_directory, output_file="historical_fixtures.json"):
    """Complete pipeline to create historical dataset from ESPN JSON files"""
    print("ESPN JSON Parser - Creating Historical Dataset")
    print("=" * 60)
    
    # Parse all ESPN JSON files
    parser = ESPNJSONParser()
    parser.parse_directory(espn_json_directory)
    
    # Save in ProbabilityAnalyzer format
    parser.save_parsed_data(output_file)
    
    return parser.get_matches_for_analyzer()

# Modified ProbabilityAnalyzer to work with historical data
class HistoricalProbabilityAnalyzer:
    def __init__(self, historical_data_file="historical_fixtures.json"):
        self.cache_calc = None  # You'd need to adapt this for historical data
        self.matches = self.load_historical_data(historical_data_file)
    
    def load_historical_data(self, data_file):
        """Load historical match data"""
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            # Return just the matches array
            return data.get('matches', data) if isinstance(data, dict) else data
        except FileNotFoundError:
            print(f"Historical data file {data_file} not found. Run the parser first.")
            return []
    
    def calculate_basic_probabilities(self):
        """Calculate base home/away/draw rates from historical data"""
        if not self.matches:
            return None
            
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
    
    def analyze_by_season(self):
        """Analyze trends by season"""
        season_stats = {}
        
        for match in self.matches:
            season = match.get('season')
            if not season:
                continue
                
            if season not in season_stats:
                season_stats[season] = {'HOME_TEAM': 0, 'AWAY_TEAM': 0, 'DRAW': 0, 'total': 0}
            
            winner = match['score']['winner']
            season_stats[season][winner] += 1
            season_stats[season]['total'] += 1
        
        # Calculate percentages
        for season, stats in season_stats.items():
            total = stats['total']
            if total > 0:
                stats['home_win_rate'] = stats['HOME_TEAM'] / total
                stats['away_win_rate'] = stats['AWAY_TEAM'] / total
                stats['draw_rate'] = stats['DRAW'] / total
        
        return season_stats

if __name__ == "__main__":
    import sys
    
    # Get directory from command line or use current directory
    if len(sys.argv) > 1:
        json_directory = sys.argv[1]
    else:
        json_directory = "."  # Current directory
    
    # Check if directory exists and has JSON files
    input_dir = Path(json_directory)
    if not input_dir.exists():
        print(f"Error: Directory '{json_directory}' does not exist")
        print("Usage: python espn_json_parser.py [directory_path]")
        sys.exit(1)
    
    # Look for JSON files
    json_files = list(input_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in '{json_directory}'")
        print("Available files:")
        all_files = list(input_dir.glob("*"))[:10]  # Show first 10 files
        for file in all_files:
            print(f"  {file.name}")
        if len(all_files) >= 10:
            print("  ...")
        sys.exit(1)
    
    print(f"Found {len(json_files)} JSON files in '{json_directory}'")
    
    # Step 1: Parse ESPN JSON files
    print("Step 1: Parsing ESPN JSON files...")
    matches = create_historical_dataset(json_directory, "premier_league_historical.json")
    
    # Only proceed if we found matches
    if not matches:
        print("No matches found. Check your JSON file format.")
        sys.exit(1)
    
    # Step 2: Run probability analysis
    print("\nStep 2: Running probability analysis...")
    analyzer = HistoricalProbabilityAnalyzer("premier_league_historical.json")
    
    basic_probs = analyzer.calculate_basic_probabilities()
    if basic_probs:
        print(f"\nHistorical Analysis Results:")
        print(f"Total matches: {basic_probs['total_matches']}")
        print(f"Home wins: {basic_probs['home_win_rate']:.1%}")
        print(f"Away wins: {basic_probs['away_win_rate']:.1%}")
        print(f"Draws: {basic_probs['draw_rate']:.1%}")
    
        # Season-by-season analysis
        season_analysis = analyzer.analyze_by_season()
        if season_analysis:
            print(f"\nSeason-by-season breakdown:")
            for season, stats in sorted(season_analysis.items()):
                print(f"{season}: {stats['total']} matches - "
                      f"H:{stats['home_win_rate']:.1%} A:{stats['away_win_rate']:.1%} D:{stats['draw_rate']:.1%}")
    else:
        print("No probability analysis possible - no valid matches found.")