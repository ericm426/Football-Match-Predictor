import React, { useState, useEffect } from 'react';
import './app.css';

function App() {
  const [teams, setTeams] = useState([]);
  const [error, setError] = useState(null);
  const [selectedHomeTeam, setSelectedHomeTeam] = useState('');
  const [selectedAwayTeam, setSelectedAwayTeam] = useState('');
  const [prediction, setPrediction] = useState(null);
  
  useEffect(() => {
  fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setError(null);
      const response = await fetch('http://localhost:5000/api/teams');
      if (!response.ok) {
        throw new Error(`HTTP error, status: ${response.status}`);
      }

      const data = await response.json();
      setTeams(data.teams);
    } catch (error) {
      console.error('Failed to fetch teams', error);
      setError('Unable to load teams. Please check your connection and try again.');
      setTeams([]);
    }
  }

  const predictMatch = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          homeTeam: {
            name: selectedHomeTeam,
            shortName: teams.find(t => t.name === selectedHomeTeam)?.shortName
          },
          awayTeam: {
            name: selectedAwayTeam,
            shortName: teams.find(t => t.name === selectedAwayTeam)?.shortName
          }
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
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="prediction-form">
          <select value={selectedHomeTeam} onChange={(e) => setSelectedHomeTeam(e.target.value)}>
            <option value="">Select Home Team</option>
            {teams.map(team => (
              <option key={team.id} value={team.name}> 
              {team.name}
              </option>
            ))}
          </select>
          
          <select value={selectedAwayTeam} onChange={(e) => setSelectedAwayTeam(e.target.value)}>
            <option value="">Select Away Team</option>
            {console.log("Selected Home Team:", selectedHomeTeam)}
            {teams
            .filter(team => {
              console.log("Checking team:", team.name, "vs", selectedHomeTeam);
              return team.name !== selectedHomeTeam})
            .map(team => (
              <option key={team.id} value={team.name}> 
              {team.name}
              </option>
            ))}
          </select>

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