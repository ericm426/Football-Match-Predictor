from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from data.api_client import FootballDataAPI

load_dotenv()

app = Flask(__name__)
CORS(app)

football_api = FootballDataAPI()

@app.route('/')
def hello():
    return jsonify({"message": "Tactical Matchup Predictor API"})

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Team List"""
    team_data = football_api.get_teams()

    if 'error' in team_data:
        return jsonify({"Error": "Unable to Fetch Data"}), 500
    
    teams = []
    # important team data
    for team in team_data['teams']:
        teams.append({
            'id': team['id'],
            'name': team['name'],
            'shortName': team['shortName'],
            'tla': team['tla'],
            'crest': team['crest']
        })

    return jsonify({"teams": teams})

@app.route('/api/predict', methods=['POST'])
def predict_match():
    """prediction algorithm

    Returns:
        _type_: _description_
    """
    data = request.json
    home_data = data.get('homeTeam')
    away_data = data.get('awayTeam')
    
    home_team = home_data['name']
    away_team = away_data['name']
    home_short = home_data['shortName']
    away_short = away_data['shortName']
    
    base_home_prob = 46.1 # calculated from my data calc in data folder
    base_away_prob = 32.4
    base_draw_prob = 21.6

    home_recent_form = football_api.get_recent_form(home_team, limit=5)
    away_recent_form = football_api.get_recent_form(away_team, limit=5)

    home_season_form = football_api.get_season_form(home_team)
    away_season_form = football_api.get_season_form(away_team)


    # basic logic, not in depth yet
    prediction = {
        "home_team": home_team,
        "away_team": away_team,
        "prediction": f"Loading analysis for {home_short} vs {away_short} . . .",
        "home_win_prob": 46.1,
        "draw_prob": 21.6,
        "away_win_prob": 32.4,
        "confidence": "Medium"
    }

    return jsonify(prediction)


if __name__ == '__main__':
    app.run(debug=True)