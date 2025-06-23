import React, { useState } from 'react';
import './app.css';

function App() {
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [prediction, setPrediction] = useState(null);

  const predictMatch = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          homeTeam,
          awayTeam,
        }),
      });
      
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Tactical Matchup Predictor</h1>
        
        <div className="prediction-form">
          <input
            type="text"
            placeholder="Home Team"
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
          />
          
          <input
            type="text"
            placeholder="Away Team"
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
          />
          
          <button onClick={predictMatch}>
            Predict Match
          </button>
        </div>

        {prediction && (
          <div className="prediction-result">
            <h3>Prediction Result:</h3>
            <p>{prediction.home_team} vs {prediction.away_team}</p>
            <p>{prediction.prediction}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;