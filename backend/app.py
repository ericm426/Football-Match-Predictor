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
    # basic logic, not in depth yet
    prediction = {
        "home_team": home_team,
        "away_team": away_team,
        "prediction": f"Loading Analysis for {home_team} vs {away_team}",
        "home_win_prob": 45,
        "draw_prob": 25,
        "away_win_prob": 30,
        "confidence": "Medium"
    }

    return jsonify(prediction)


if __name__ == '__main__':
    app.run(debug=True)