from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return jsonify({"message": "Tactical Matchup Predictor API"})

@app.route('/api/predict', methods=['POST'])
def predict_match():
    data = request.json
    # TODO: Implement prediction logic
    return jsonify({
        "home_team": data.get('homeTeam'),
        "away_team": data.get('awayTeam'),
        "prediction": "Coming soon!"
    })

if __name__ == '__main__':
    app.run(debug=True)