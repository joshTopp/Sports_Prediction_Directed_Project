import './App.css'

function App() {
  const samplePlayer = {
    name: 'Aaron Judge',
    team: 'New York Yankees',
    position: 'RF',
    opponent: 'Boston Red Sox',
    pitcherMatchup: 'vs. Left-Handed Pitcher',
    hitChance: '64%',
    homeRunChance: '18%',
    strikeoutRisk: 'Medium',
    confidenceScore: '72%',
    riskLevel: 'Moderate',
    explanation:
      'This prediction is based on recent hitting trends, pitcher matchup, and overall player performance. The confidence score is moderate because the player has strong power numbers, but the strikeout risk is still a factor.',
  }

  return (
    <main className="dashboard">
      <header className="header">
        <div>
          <h1>MLB Performance Prediction</h1>
          <p>
            MVP dashboard mockup using placeholder data for player predictions,
            confidence score, and risk level.
          </p>
        </div>
      </header>

      <section className="search-section">
        <label htmlFor="player-search">Search Player</label>
        <input
          id="player-search"
          type="text"
          placeholder="Search MLB player..."
        />
      </section>

      <section className="player-card">
        <div>
          <h2>{samplePlayer.name}</h2>
          <p>
            {samplePlayer.team} • {samplePlayer.position}
          </p>
        </div>
        <div>
          <p className="small-label">Matchup</p>
          <p>{samplePlayer.opponent}</p>
          <p>{samplePlayer.pitcherMatchup}</p>
        </div>
      </section>

      <section className="prediction-grid">
        <div className="prediction-card">
          <p className="small-label">Hit Chance</p>
          <h3>{samplePlayer.hitChance}</h3>
        </div>

        <div className="prediction-card">
          <p className="small-label">Home Run Chance</p>
          <h3>{samplePlayer.homeRunChance}</h3>
        </div>

        <div className="prediction-card">
          <p className="small-label">Strikeout Risk</p>
          <h3>{samplePlayer.strikeoutRisk}</h3>
        </div>

        <div className="prediction-card">
          <p className="small-label">Confidence Score</p>
          <h3>{samplePlayer.confidenceScore}</h3>
        </div>

        <div className="prediction-card">
          <p className="small-label">Risk Level</p>
          <h3>{samplePlayer.riskLevel}</h3>
        </div>
      </section>

      <section className="info-grid">
        <div className="explanation-box">
          <h2>Why this prediction?</h2>
          <p>{samplePlayer.explanation}</p>
        </div>

        <div className="chart-placeholder">
          <h2>Recent Performance Trend</h2>
          <div className="chart-box">
            <span>Chart placeholder</span>
          </div>
        </div>
      </section>
    </main>
  )
}

export default App