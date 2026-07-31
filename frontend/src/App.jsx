import { useEffect, useState } from "react";
import "./App.css";

const PLAYER_API_URL = "http://127.0.0.1:8000/api/players";
const DASHBOARD_API_URL =
  "http://127.0.0.1:8000/api/dashboard/2026-07-31";

const teamIdMap = {
  108: { teamCode: "LAA", team: "Los Angeles Angels" },
  109: { teamCode: "ARI", team: "Arizona Diamondbacks" },
  110: { teamCode: "BAL", team: "Baltimore Orioles" },
  111: { teamCode: "BOS", team: "Boston Red Sox" },
  112: { teamCode: "CHC", team: "Chicago Cubs" },
  113: { teamCode: "CIN", team: "Cincinnati Reds" },
  114: { teamCode: "CLE", team: "Cleveland Guardians" },
  115: { teamCode: "COL", team: "Colorado Rockies" },
  116: { teamCode: "DET", team: "Detroit Tigers" },
  117: { teamCode: "HOU", team: "Houston Astros" },
  118: { teamCode: "KC", team: "Kansas City Royals" },
  119: { teamCode: "LAD", team: "Los Angeles Dodgers" },
  120: { teamCode: "WSH", team: "Washington Nationals" },
  121: { teamCode: "NYM", team: "New York Mets" },
  133: { teamCode: "ATH", team: "Athletics" },
  134: { teamCode: "PIT", team: "Pittsburgh Pirates" },
  135: { teamCode: "SD", team: "San Diego Padres" },
  136: { teamCode: "SEA", team: "Seattle Mariners" },
  137: { teamCode: "SF", team: "San Francisco Giants" },
  138: { teamCode: "STL", team: "St. Louis Cardinals" },
  139: { teamCode: "TB", team: "Tampa Bay Rays" },
  140: { teamCode: "TEX", team: "Texas Rangers" },
  141: { teamCode: "TOR", team: "Toronto Blue Jays" },
  142: { teamCode: "MIN", team: "Minnesota Twins" },
  143: { teamCode: "PHI", team: "Philadelphia Phillies" },
  144: { teamCode: "ATL", team: "Atlanta Braves" },
  145: { teamCode: "CWS", team: "Chicago White Sox" },
  146: { teamCode: "MIA", team: "Miami Marlins" },
  147: { teamCode: "NYY", team: "New York Yankees" },
  158: { teamCode: "MIL", team: "Milwaukee Brewers" },
};

/*
  These local players remain available if the backend is offline
  or returns an empty player list.

  Prediction numbers are still stored in the frontend until the
  prediction endpoints are connected.
*/

const fallbackPlayers = [
  {
    id: 1,
    name: "Aaron Judge",
    initials: "AJ",
    team: "New York Yankees",
    teamCode: "NYY",
    position: "RF",
    number: "99",
    bats: "R",
    throws: "R",
    matchup: "vs Boston",
    gameTime: "7:10 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 72,
    homeRunChance: 28,
    strikeoutRisk: 20,
    confidence: 72,
    risk: "Moderate",
    edge: "+8%",
    recentForm: "Strong",
    matchupStrength: "Favorable",
    trend: [52, 61, 58, 69, 63, 76, 71, 82, 78, 88],
    insights: [
      "Strong recent contact rate over the last ten games.",
      "Favorable matchup against the opposing pitcher.",
      "Power production has improved during the recent trend window.",
      "Strikeout risk remains moderate.",
    ],
  },
  {
    id: 2,
    name: "Shohei Ohtani",
    initials: "SO",
    team: "Los Angeles Dodgers",
    teamCode: "LAD",
    position: "TWP",
    number: "17",
    bats: "L",
    throws: "R",
    matchup: "vs San Diego",
    gameTime: "10:10 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 68,
    homeRunChance: 25,
    strikeoutRisk: 24,
    confidence: 68,
    risk: "Moderate",
    edge: "+7%",
    recentForm: "Strong",
    matchupStrength: "Favorable",
    trend: [48, 55, 67, 61, 72, 68, 79, 73, 84, 80],
    insights: [
      "Recent power production is trending upward.",
      "The matchup provides a positive handedness advantage.",
      "Home run probability is above the current player-board average.",
      "Moderate strikeout risk slightly lowers confidence.",
    ],
  },
  {
    id: 3,
    name: "Juan Soto",
    initials: "JS",
    team: "New York Mets",
    teamCode: "NYM",
    position: "RF",
    number: "22",
    bats: "L",
    throws: "L",
    matchup: "vs Atlanta",
    gameTime: "7:20 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 66,
    homeRunChance: 22,
    strikeoutRisk: 18,
    confidence: 65,
    risk: "Low",
    edge: "+6%",
    recentForm: "Strong",
    matchupStrength: "Favorable",
    trend: [56, 62, 59, 70, 66, 74, 69, 77, 81, 79],
    insights: [
      "Strong plate discipline improves the overall outlook.",
      "Recent performance has remained consistent.",
      "The matchup is favorable for left-handed contact.",
      "Lower strikeout risk supports a positive prediction.",
    ],
  },
  {
    id: 4,
    name: "Mookie Betts",
    initials: "MB",
    team: "Los Angeles Dodgers",
    teamCode: "LAD",
    position: "RF",
    number: "50",
    bats: "R",
    throws: "R",
    matchup: "vs San Diego",
    gameTime: "10:10 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 64,
    homeRunChance: 17,
    strikeoutRisk: 16,
    confidence: 63,
    risk: "Low",
    edge: "+5%",
    recentForm: "Steady",
    matchupStrength: "Balanced",
    trend: [63, 58, 66, 70, 64, 72, 68, 74, 71, 77],
    insights: [
      "Recent contact numbers have remained steady.",
      "Low strikeout risk improves the overall outlook.",
      "The matchup is balanced rather than strongly favorable.",
      "Power probability remains moderate.",
    ],
  },
  {
    id: 5,
    name: "Bobby Witt Jr.",
    initials: "BW",
    team: "Kansas City Royals",
    teamCode: "KC",
    position: "SS",
    number: "7",
    bats: "R",
    throws: "R",
    matchup: "vs Minnesota",
    gameTime: "8:10 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 67,
    homeRunChance: 19,
    strikeoutRisk: 21,
    confidence: 66,
    risk: "Moderate",
    edge: "+6%",
    recentForm: "Trending",
    matchupStrength: "Favorable",
    trend: [45, 53, 60, 57, 66, 64, 72, 78, 75, 84],
    insights: [
      "Recent performance is trending in a positive direction.",
      "Speed and contact ability support the hit prediction.",
      "The opposing matchup is considered favorable.",
      "Strikeout risk remains manageable.",
    ],
  },
  {
    id: 6,
    name: "Yordan Alvarez",
    initials: "YA",
    team: "Houston Astros",
    teamCode: "HOU",
    position: "DH",
    number: "44",
    bats: "L",
    throws: "R",
    matchup: "vs Texas",
    gameTime: "8:05 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 62,
    homeRunChance: 26,
    strikeoutRisk: 27,
    confidence: 61,
    risk: "Moderate",
    edge: "+4%",
    recentForm: "Power Up",
    matchupStrength: "Balanced",
    trend: [50, 57, 54, 63, 60, 69, 65, 73, 70, 76],
    insights: [
      "Power production has improved in the recent trend window.",
      "The matchup is balanced rather than clearly favorable.",
      "Home run probability remains one of the strongest metrics.",
      "Strikeout risk reduces the total confidence score.",
    ],
  },
  {
    id: 7,
    name: "Freddie Freeman",
    initials: "FF",
    team: "Los Angeles Dodgers",
    teamCode: "LAD",
    position: "1B",
    number: "5",
    bats: "L",
    throws: "R",
    matchup: "vs San Diego",
    gameTime: "10:10 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 65,
    homeRunChance: 16,
    strikeoutRisk: 15,
    confidence: 64,
    risk: "Low",
    edge: "+5%",
    recentForm: "Steady",
    matchupStrength: "Favorable",
    trend: [58, 64, 61, 69, 72, 68, 75, 73, 79, 82],
    insights: [
      "Consistent contact supports the hit prediction.",
      "Strikeout risk is lower than the other featured players.",
      "The matchup is considered favorable.",
      "Recent form has remained steady.",
    ],
  },
  {
    id: 8,
    name: "Gunnar Henderson",
    initials: "GH",
    team: "Baltimore Orioles",
    teamCode: "BAL",
    position: "SS",
    number: "2",
    bats: "L",
    throws: "R",
    matchup: "vs Toronto",
    gameTime: "7:07 PM",
    opposingPitcher: "Projected Starting Pitcher",
    hitChance: 59,
    homeRunChance: 21,
    strikeoutRisk: 31,
    confidence: 58,
    risk: "High",
    edge: "+3%",
    recentForm: "Mixed",
    matchupStrength: "Difficult",
    trend: [62, 55, 67, 51, 64, 58, 70, 60, 68, 63],
    insights: [
      "Recent performance has been inconsistent.",
      "The opposing matchup is considered difficult.",
      "Power potential remains positive.",
      "Higher strikeout risk lowers the confidence score.",
    ],
  },
];

function createInitials(fullName) {
  if (!fullName) {
    return "MLB";
  }

  const nameParts = fullName.trim().split(/\s+/).filter(Boolean);

  return (
    nameParts
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join("") || "MLB"
  );
}

function isPitcherPosition(position) {
  const pitcherPositions = ["P", "SP", "RP", "TWP"];

  return pitcherPositions.includes(
    String(position || "").toUpperCase(),
  );
}

function normalizePredictionRisk(riskLevel, fallbackRisk) {
  const normalizedRisk = String(riskLevel || "")
    .trim()
    .toLowerCase();

  if (normalizedRisk === "low") {
    return "Low";
  }

  if (
    normalizedRisk === "medium" ||
    normalizedRisk === "moderate"
  ) {
    return "Moderate";
  }

  if (normalizedRisk === "high") {
    return "High";
  }

  return fallbackRisk;
}

function normalizePredictionConfidence(
  confidenceScore,
  fallbackConfidence,
) {
  const numericConfidence = Number(confidenceScore);

  if (!Number.isFinite(numericConfidence)) {
    return fallbackConfidence;
  }

  if (numericConfidence >= 0 && numericConfidence <= 1) {
    return Math.round(numericConfidence * 100);
  }

  return Math.round(numericConfidence);
}

function formatStrikeoutProjection(value) {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return numericValue.toFixed(2).replace(/\.?0+$/, "");
}

function convertBackendPlayer(
  player,
  index,
  loadedMatchups,
  loadedPredictions,
  backendPlayerLookup,
) {
  const playerId = player.player_id ?? `backend-player-${index}`;

  const predictionProfileIndex =
    Math.abs(Number(player.player_id) || index) % fallbackPlayers.length;

  const predictionProfile = fallbackPlayers[predictionProfileIndex];

  const teamId =
    player.team_id === null || player.team_id === undefined
      ? "N/A"
      : player.team_id;

  const mappedTeam = teamIdMap[player.team_id];
  const playerName = player.full_name || `MLB Player ${index + 1}`;

  let playerMatchup = "Matchup TBD";
  let opposingPitcher = "Projected Starting Pitcher";
  const numericTeamId = Number(player.team_id);

  const matchingGame = Array.isArray(loadedMatchups)
    ? loadedMatchups.find((game) => {
        return (
          Number(game.home_team_id) === numericTeamId ||
          Number(game.away_team_id) === numericTeamId
        );
      })
    : null;

  if (matchingGame) {
    const playerIsHomeTeam =
      Number(matchingGame.home_team_id) === numericTeamId;

    const opponentTeamId = playerIsHomeTeam
      ? matchingGame.away_team_id
      : matchingGame.home_team_id;

    const opponentTeam = teamIdMap[Number(opponentTeamId)];

    const opponentTeamCode = opponentTeam
    ? opponentTeam.teamCode
    : `T${opponentTeamId}`;
  
  playerMatchup = playerIsHomeTeam
    ? `vs ${opponentTeamCode}`
    : `@ ${opponentTeamCode}`;
  
  const opposingPitcherId = playerIsHomeTeam
    ? matchingGame.away_probable_pitcher_id
    : matchingGame.home_probable_pitcher_id;
  
  if (
    opposingPitcherId !== null &&
    opposingPitcherId !== undefined
  ) {
    const pitcherPlayer = backendPlayerLookup.get(
      Number(opposingPitcherId),
    );
  
    if (pitcherPlayer?.full_name) {
      opposingPitcher = pitcherPlayer.full_name;
    }
  }
  }

  const playerPosition = player.primary_position || "N/A";

  const playerIsPitcher = isPitcherPosition(playerPosition);
  
  const strikeoutPrediction =
    playerIsPitcher && Array.isArray(loadedPredictions)
      ? loadedPredictions.find((prediction) => {
          return Number(prediction.player_id) === Number(playerId);
        })
      : null;
  
  const predictedStrikeouts = Number(
    strikeoutPrediction?.predicted_value,
  );
  
  const hasStrikeoutPrediction =
    Boolean(strikeoutPrediction) &&
    Number.isFinite(predictedStrikeouts);
  
  const strikeoutRisk = hasStrikeoutPrediction
    ? predictedStrikeouts
    : predictionProfile.strikeoutRisk;
  
  const confidence = hasStrikeoutPrediction
    ? normalizePredictionConfidence(
        strikeoutPrediction.confidence_score,
        predictionProfile.confidence,
      )
    : predictionProfile.confidence;
  
  const risk = hasStrikeoutPrediction
    ? normalizePredictionRisk(
        strikeoutPrediction.risk_level,
        predictionProfile.risk,
      )
    : predictionProfile.risk;

  return {
    ...predictionProfile,

    id: playerId,
    name: playerName,
    initials: createInitials(playerName),

    team: mappedTeam ? mappedTeam.team : `Team ${teamId}`,
    teamCode: mappedTeam ? mappedTeam.teamCode : `T${teamId}`,

    position: playerPosition,
    number: "--",
    bats: player.bat_side || "N/A",
    throws: player.throw_hand || "N/A",
    
    matchup: playerMatchup,
    gameTime: "TBD",
    opposingPitcher,
    
    strikeoutRisk,
    confidence,
    risk,
    hasStrikeoutPrediction,

    insights: [
      "Recent performance trends support the current player outlook.",
      "Matchup strength is included when the next game is available.",
      "Strikeout risk contributes to the overall confidence score.",
      "Recent form and player trends are included in the analysis.",
    ],
  };
}

function getRiskClass(risk) {
  return `risk-${risk.toLowerCase()}`;
}

function TopNavigation({ activePage, setActivePage }) {
  const highlightedPage = activePage === "detail" ? "search" : activePage;

  const navigationItems = [
    { id: "dashboard", label: "Dashboard", icon: "⌂" },
    { id: "search", label: "Player Search", icon: "⌕" },
    { id: "predictions", label: "Prediction Board", icon: "▦" },
    { id: "model", label: "Model Lab", icon: "◉" },
    { id: "premium", label: "Premium", icon: "♔" },
  ];

  return (
    <header className="top-navigation">
      <button
        type="button"
        className="brand"
        onClick={() => setActivePage("dashboard")}
      >
        <span className="brand-logo">T6</span>

        <span className="brand-text">
          <strong>TEAM 6</strong>
          <small>MLB PREDICTION APP</small>
        </span>
      </button>

      <nav className="navigation-links" aria-label="Main navigation">
        {navigationItems.map((item) => (
          <button
            type="button"
            key={item.id}
            className={
              highlightedPage === item.id
                ? "navigation-button active"
                : "navigation-button"
            }
            onClick={() => setActivePage(item.id)}
          >
            <span className="navigation-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="navigation-actions">
        <span className="demo-status-dot" title="Dashboard active" />

        <button type="button" className="notification-button">
          ♧
        </button>

        <span className="profile-circle">T6</span>
      </div>
    </header>
  );
}

function PlayerAvatar({ player, large = false }) {
  return (
    <div className={large ? "player-avatar large" : "player-avatar"}>
      <span>{player.initials}</span>
      <small>{player.teamCode}</small>
    </div>
  );
}

function PlayerResultRow({
  player,
  selectedPlayer,
  setSelectedPlayer,
  openDetail,
}) {
  const isSelected = selectedPlayer.id === player.id;

  return (
    <article
      className={isSelected ? "player-result selected" : "player-result"}
      onClick={() => setSelectedPlayer(player)}
    >
      <div className="player-result-main">
        <PlayerAvatar player={player} />

        <div>
          <h3>{player.name}</h3>
          <p>
            {player.teamCode} · {player.position}
          </p>
        </div>
      </div>

      <div className="player-result-info">
        <span className="player-hand">
          Bats {player.bats} · Throws {player.throws}
        </span>

        <span className="confidence-value">{player.confidence}%</span>

        <span className={`risk-badge ${getRiskClass(player.risk)}`}>
          {player.risk}
        </span>

        <button
          type="button"
          className="small-action-button"
          onClick={(event) => {
            event.stopPropagation();
            openDetail(player);
          }}
        >
          View
        </button>
      </div>
    </article>
  );
}

function MetricCard({ label, value, caption, accent = "orange" }) {
  return (
    <article className={`metric-card accent-${accent}`}>
      <span className="metric-label">{label}</span>
      <strong>{value}</strong>

      <div className="metric-progress">
        <span
          className="metric-progress-fill"
          style={{
            width:
              typeof value === "string" && value.includes("%") ? value : "65%",
          }}
        />
      </div>

      <small>{caption}</small>
    </article>
  );
}

function PlayerPreview({ player, openDetail }) {
  return (
    <section className="panel player-preview-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">MATCHUP PREVIEW</span>
          <h2>Player Preview</h2>
        </div>

        <span className={`risk-badge ${getRiskClass(player.risk)}`}>
          {player.risk} Risk
        </span>
      </div>

      <div className="player-preview-header">
        <PlayerAvatar player={player} large />

        <div className="player-preview-identity">
          <span className="team-code-label">{player.teamCode}</span>
          <h2>{player.name}</h2>

          <p>
            {player.team} · #{player.number} · {player.position}
          </p>

          <div className="player-small-details">
            <span>Bats: {player.bats}</span>
            <span>Throws: {player.throws}</span>
          </div>
        </div>
      </div>

      <div className="next-matchup-card">
        <div>
          <span>Next Matchup</span>
          <strong>{player.matchup}</strong>
        </div>

        <div>
          <span>Game Time</span>
          <strong>{player.gameTime}</strong>
        </div>
      </div>

      <div className="preview-metrics">
        <MetricCard
          label="Hit Chance"
          value={`${player.hitChance}%`}
          caption="Player prediction"
          accent="green"
        />

        <MetricCard
          label="Home Run Chance"
          value={`${player.homeRunChance}%`}
          caption="Power outlook"
          accent="orange"
        />

        <MetricCard
          label="Confidence"
          value={`${player.confidence}%`}
          caption="Confidence score"
          accent="purple"
        />
      </div>

      <div className="preview-summary-row">
        <div>
          <span>Model Edge</span>
          <strong className="positive-text">{player.edge}</strong>
        </div>

        <div>
          <span>Recent Form</span>
          <strong>{player.recentForm}</strong>
        </div>

        <div>
          <span>Matchup</span>
          <strong>{player.matchupStrength}</strong>
        </div>
      </div>

      <button
        type="button"
        className="primary-button full-width-button"
        onClick={() => openDetail(player)}
      >
        View Full Player Analysis
        <span>→</span>
      </button>
    </section>
  );
}

function SummaryCard({ icon, label, value, description, status }) {
  const statusLabels = {
    ready: "Active",
    pending: "Live",
    waiting: "Tracked",
    planned: "Saved",
  };

  return (
    <article className="summary-card">
      <div className="summary-card-top">
        <span className="summary-icon">{icon}</span>

        <span className={`status-chip ${status}`}>
          {statusLabels[status]}
        </span>
      </div>

      <span>{label}</span>
      <strong>{value}</strong>
      <small>{description}</small>
    </article>
  );
}

function DashboardPage({
  players,
  filteredPlayers,
  selectedPlayer,
  setSelectedPlayer,
  searchText,
  setSearchText,
  openDetail,
  setActivePage,
  playerLoadLabel,
}) {
  const topPredictions = [...players]
    .sort((firstPlayer, secondPlayer) => {
      return secondPlayer.confidence - firstPlayer.confidence;
    })
    .slice(0, 4);

  const dashboardResults = searchText
    ? filteredPlayers
    : filteredPlayers.slice(0, 5);

  return (
    <>
      <section className="page-heading">
        <div>
          <span className="eyebrow">DASHBOARD</span>
          <h1>MLB Prediction Dashboard</h1>
          <p>
            Search players, compare matchup trends, and review confidence and
            risk levels.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={() => setActivePage("search")}
        >
          Open Player Search
        </button>
      </section>

      <section className="dashboard-main-grid">
        <div className="dashboard-left-column">
          <section className="panel dashboard-search-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">PLAYER SEARCH</span>
                <h2>Search MLB Players</h2>
              </div>

              <span className="result-count">{playerLoadLabel}</span>
            </div>

            <label className="search-input-wrapper">
              <span>⌕</span>

              <input
                type="text"
                value={searchText}
                onChange={(event) => setSearchText(event.target.value)}
                placeholder="Search by player name, team, or position..."
              />

              {searchText && (
                <button
                  type="button"
                  className="clear-search-button"
                  onClick={() => setSearchText("")}
                  aria-label="Clear search"
                >
                  ×
                </button>
              )}
            </label>

            <div className="player-results-list">
              {dashboardResults.length > 0 ? (
                dashboardResults.map((player) => (
                  <PlayerResultRow
                    key={player.id}
                    player={player}
                    selectedPlayer={selectedPlayer}
                    setSelectedPlayer={setSelectedPlayer}
                    openDetail={openDetail}
                  />
                ))
              ) : (
                <div className="empty-state">
                  <strong>No players found</strong>
                  <p>Try searching for another player, team, or position.</p>
                </div>
              )}
            </div>

            <button
              type="button"
              className="text-button"
              onClick={() => setActivePage("search")}
            >
              View all players →
            </button>
          </section>

          <section className="panel demo-predictions-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">TODAY'S MLB BOARD</span>
                <h2>Top Predictions</h2>
              </div>

              <span className="sample-label">MODEL INFO</span>
            </div>

            <div className="prediction-list">
              {topPredictions.map((player, index) => (
                <button
                  type="button"
                  className="prediction-row"
                  key={player.id}
                  onClick={() => {
                    setSelectedPlayer(player);
                    openDetail(player);
                  }}
                >
                  <span className="prediction-rank">0{index + 1}</span>

                  <PlayerAvatar player={player} />

                  <span className="prediction-player">
                    <strong>{player.name}</strong>
                    <small>
                      {player.teamCode} · {player.matchup}
                    </small>
                  </span>

                  <span className="prediction-type">Hit Chance</span>

                  <span className="prediction-confidence">
                    {player.confidence}%
                  </span>

                  <span
                    className={`risk-badge ${getRiskClass(player.risk)}`}
                  >
                    {player.risk}
                  </span>
                </button>
              ))}
            </div>
          </section>
        </div>

        <PlayerPreview player={selectedPlayer} openDetail={openDetail} />
      </section>

      <section className="summary-card-grid">
        <SummaryCard
          icon="✓"
          label="Highest Confidence"
          value={topPredictions[0]?.name || "Player"}
          description={`${topPredictions[0]?.confidence || 0}% confidence score`}
          status="ready"
        />

        <SummaryCard
          icon="⌁"
          label="Lowest Risk"
          value={
            players.find((player) => player.risk === "Low")?.name ||
            players[0]?.name ||
            "Player"
          }
          description="Low risk player profile"
          status="pending"
        />

        <SummaryCard
          icon="◉"
          label="Trends"
          value="10 Games"
          description="Recent player performance window"
          status="waiting"
        />

        <SummaryCard
          icon="☆"
          label="Watchlist"
          value={`${Math.min(players.length, 4)} Players`}
          description="Featured players currently tracked"
          status="planned"
        />
      </section>

      <section className="dashboard-secondary-grid">
        <section className="panel compact-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">DATA SYNC</span>
              <h2>Dashboard Coverage</h2>
            </div>
          </div>

          <div className="status-list">
            <div>
              <span className="status-indicator ready" />
              <p>
                <strong>Player Board</strong>
                <small>{playerLoadLabel}</small>
              </p>
            </div>

            <div>
              <span className="status-indicator pending" />
              <p>
                <strong>Matchup Trends</strong>
                <small>Current matchup view available</small>
              </p>
            </div>

            <div>
              <span className="status-indicator pending" />
              <p>
                <strong>Confidence Scores</strong>
                <small>Player-level confidence ratings</small>
              </p>
            </div>

            <div>
              <span className="status-indicator waiting" />
              <p>
                <strong>Risk Levels</strong>
                <small>Low, moderate, and high ratings</small>
              </p>
            </div>

            <div>
              <span className="status-indicator planned" />
              <p>
                <strong>Trends</strong>
                <small>Recent ten-game performance view</small>
              </p>
            </div>
          </div>
        </section>

        <section className="panel compact-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">WATCHLIST</span>
              <h2>Player Watchlist</h2>
            </div>

            <span className="coming-soon-label">WATCHLIST</span>
          </div>

          <div className="watchlist">
            {players.slice(0, 4).map((player) => (
              <button
                type="button"
                key={player.id}
                onClick={() => setSelectedPlayer(player)}
              >
                <PlayerAvatar player={player} />

                <span>
                  <strong>{player.name}</strong>
                  <small>
                    {player.teamCode} · {player.position}
                  </small>
                </span>

                <span className="watchlist-star">☆</span>
              </button>
            ))}
          </div>

          <button type="button" className="disabled-feature-button" disabled>
            Watchlist Management
          </button>
        </section>

        <section className="panel compact-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">MODEL INFO</span>
              <h2>Analysis Overview</h2>
            </div>
          </div>

          <div className="model-preview-grid">
            <div>
              <span>Model Type</span>
              <strong>Random Forest / Decision Tree</strong>
            </div>

            <div>
              <span>Confidence</span>
              <strong>Player-Level Score</strong>
            </div>

            <div>
              <span>Risk Rating</span>
              <strong>Low to High</strong>
            </div>

            <div>
              <span>Trend Window</span>
              <strong>Last 10 Games</strong>
            </div>

            <div className="model-status-message">
              Matchup strength, recent form, confidence, and player trends are
              included in each analysis.
            </div>
          </div>

          <button
            type="button"
            className="secondary-button full-width-button"
            onClick={() => setActivePage("model")}
          >
            View Model Info
          </button>
        </section>
      </section>
    </>
  );
}

function PlayerSearchPage({
  filteredPlayers,
  selectedPlayer,
  setSelectedPlayer,
  searchText,
  setSearchText,
  openDetail,
  playerLoadLabel,
}) {
  return (
    <>
      <section className="page-heading">
        <div>
          <span className="eyebrow">PLAYER SEARCH</span>
          <h1>Player Search</h1>
          <p>
            Search players, compare confidence scores, and open detailed
            matchup analysis.
          </p>
        </div>

        <span className="result-count">{playerLoadLabel}</span>
      </section>

      <section className="search-page-grid">
        <section className="panel search-results-panel">
          <label className="search-input-wrapper large-search-input">
            <span>⌕</span>

            <input
              type="text"
              value={searchText}
              onChange={(event) => setSearchText(event.target.value)}
              placeholder="Search players, teams, or positions..."
              autoFocus
            />

            {searchText && (
              <button
                type="button"
                className="clear-search-button"
                onClick={() => setSearchText("")}
                aria-label="Clear search"
              >
                ×
              </button>
            )}
          </label>

          <div className="fake-filter-row">
            <button type="button" className="fake-filter active">
              All Players
            </button>

            <button type="button" className="fake-filter">
              Batters
            </button>

            <button type="button" className="fake-filter">
              Pitchers
            </button>

            <button type="button" className="fake-filter">
              All Teams
            </button>

            <button type="button" className="fake-filter">
              Handedness
            </button>
          </div>

          <div className="search-results-heading">
            <strong>Player Results</strong>
            <span>{filteredPlayers.length} players found</span>
          </div>

          <div className="player-results-list search-results-list">
            {filteredPlayers.length > 0 ? (
              filteredPlayers.map((player) => (
                <PlayerResultRow
                  key={player.id}
                  player={player}
                  selectedPlayer={selectedPlayer}
                  setSelectedPlayer={setSelectedPlayer}
                  openDetail={openDetail}
                />
              ))
            ) : (
              <div className="empty-state">
                <strong>No matching player</strong>
                <p>Try a different player name, team, or position.</p>
              </div>
            )}
          </div>
        </section>

        <PlayerPreview player={selectedPlayer} openDetail={openDetail} />
      </section>
    </>
  );
}

function MatchupStrengthMeter({ player }) {
  const strengthRows = [
    {
      label: "Pitcher Matchup",
      value: player.matchupStrength,
      percentage:
        player.matchupStrength === "Favorable"
          ? 82
          : player.matchupStrength === "Balanced"
            ? 60
            : 38,
      className: "green",
    },
    {
      label: "Recent Form",
      value: player.recentForm,
      percentage:
        player.recentForm === "Strong" || player.recentForm === "Trending"
          ? 78
          : player.recentForm === "Mixed"
            ? 48
            : 65,
      className: "blue",
    },
    {
      label: player.hasStrikeoutPrediction
        ? "Projected Strikeouts"
        : "Strikeout Risk",
      value: player.hasStrikeoutPrediction
        ? `${formatStrikeoutProjection(player.strikeoutRisk)} K`
        : `${player.strikeoutRisk}%`,
      percentage: player.hasStrikeoutPrediction
        ? Math.min(
            Math.max(Number(player.strikeoutRisk) * 10, 0),
            100,
          )
        : player.strikeoutRisk,
      className: "yellow",
    },
    {
      label: "Overall Risk",
      value: player.risk,
      percentage:
        player.risk === "Low" ? 30 : player.risk === "Moderate" ? 58 : 82,
      className: player.risk === "High" ? "red" : "orange",
    },
  ];

  return (
    <section className="panel matchup-strength-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">MATCHUP PREVIEW</span>
          <h2>Matchup Strength</h2>
        </div>
      </div>

      <div className="strength-meter-list">
        {strengthRows.map((row) => (
          <div className="strength-meter-row" key={row.label}>
            <div>
              <span>{row.label}</span>
              <strong>{row.value}</strong>
            </div>

            <div className="strength-meter">
              <span
                className={`strength-meter-fill ${row.className}`}
                style={{ width: `${row.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function TrendChart({ player }) {
  return (
    <section className="panel performance-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">TRENDS</span>
          <h2>Recent Performance</h2>
        </div>

        <span className="trend-status">
          Current Form: {player.recentForm}
        </span>
      </div>

      <div className="trend-chart">
        {player.trend.map((value, index) => (
          <div className="trend-column" key={`${player.id}-${index}`}>
            <div className="trend-bar-track">
              <span
                className="trend-bar-fill"
                style={{ height: `${value}%` }}
                title={`Game ${index + 1}: ${value}`}
              />
            </div>

            <small>G{index + 1}</small>
          </div>
        ))}
      </div>

      <div className="trend-footer">
        <span>Earlier Games</span>
        <span>Most Recent</span>
      </div>
    </section>
  );
}

function WhyPrediction({ player }) {
  return (
    <section className="panel explanation-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">MODEL INFO</span>
          <h2>Why This Prediction?</h2>
        </div>
      </div>

      <p className="explanation-introduction">
        This analysis reviews recent player trends, matchup difficulty,
        strikeout risk, and overall confidence.
      </p>

      <div className="insight-list">
        {player.insights.map((insight, index) => (
          <div className="insight-row" key={`${player.id}-${index}`}>
            <span className={`insight-icon insight-${index + 1}`}>✓</span>
            <p>{insight}</p>
          </div>
        ))}
      </div>

      <div className="confidence-note">
        <span>Confidence Score</span>
        <strong>{player.confidence}%</strong>
      </div>
    </section>
  );
}

function PremiumToolsPreview() {
  const tools = [
    "Custom stat windows",
    "Saved player watchlist",
    "Advanced matchup breakdown",
    "Deeper trend charts",
    "Player comparison tool",
  ];

  return (
    <section className="panel premium-preview-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow purple-text">PREMIUM TOOLS</span>
          <h2>Advanced Tools</h2>
        </div>

        <span className="locked-label">Premium</span>
      </div>

      <div className="premium-tool-list">
        {tools.map((tool) => (
          <div key={tool}>
            <span className="premium-lock">⌑</span>

            <p>
              <strong>{tool}</strong>
              <small>Included with premium access</small>
            </p>
          </div>
        ))}
      </div>

      <button type="button" className="premium-button">
        View Premium Tools
      </button>
    </section>
  );
}

function PlayerDetailPage({ player, setActivePage }) {
  return (
    <>
      <div className="detail-navigation">
        <button
          type="button"
          className="back-button"
          onClick={() => setActivePage("search")}
        >
          ← Back to Player Search
        </button>

        <button
          type="button"
          className="close-detail-button"
          onClick={() => setActivePage("search")}
          aria-label="Close player detail"
        >
          ×
        </button>
      </div>

      <section className="panel detail-player-hero">
        <div className="detail-player-main">
          <PlayerAvatar player={player} large />

          <div>
            <span className="team-code-label">{player.teamCode}</span>

            <h1>{player.name}</h1>

            <p>
              {player.team} · #{player.number} · {player.position}
            </p>

            <div className="player-detail-tags">
              <span>Bats: {player.bats}</span>
              <span>Throws: {player.throws}</span>
              <span>MLB Dashboard</span>
            </div>
          </div>
        </div>

        <div className="detail-matchup-card">
          <span>Next Game</span>
          <strong>{player.matchup}</strong>
          <p>{player.gameTime}</p>
          <small>Pitcher: {player.opposingPitcher}</small>
        </div>
      </section>

      <section className="detail-metric-grid">
        <MetricCard
          label="Hit Chance"
          value={`${player.hitChance}%`}
          caption="Player prediction"
          accent="green"
        />

        <MetricCard
          label="Home Run Chance"
          value={`${player.homeRunChance}%`}
          caption="Power outlook"
          accent="orange"
        />

        <MetricCard
          label={
            player.hasStrikeoutPrediction
              ? "Projected Strikeouts"
              : "Strikeout Risk"
          }
          value={
            player.hasStrikeoutPrediction
              ? `${formatStrikeoutProjection(player.strikeoutRisk)} K`
              : `${player.strikeoutRisk}%`
          }
          caption={
            player.hasStrikeoutPrediction
              ? "Pitcher projection"
              : "Lower is stronger"
          }
          accent="red"
        />

        <MetricCard
          label="Confidence Score"
          value={`${player.confidence}%`}
          caption="Model confidence"
          accent="purple"
        />

        <article className="metric-card risk-level-card">
          <span className="metric-label">Risk Level</span>
          <strong className={getRiskClass(player.risk)}>{player.risk}</strong>

          <div className="risk-gauge">
            <span
              style={{
                width:
                  player.risk === "Low"
                    ? "30%"
                    : player.risk === "Moderate"
                      ? "60%"
                      : "85%",
              }}
            />
          </div>

          <small>Overall risk rating</small>
        </article>

        <article className="metric-card model-edge-card">
          <span className="metric-label">Model Edge</span>
          <strong className="positive-text">{player.edge}</strong>

          <div className="metric-progress">
            <span
              className="metric-progress-fill"
              style={{ width: "68%" }}
            />
          </div>

          <small>Matchup advantage</small>
        </article>
      </section>

      <section className="detail-content-grid">
        <div className="detail-left-column">
          <TrendChart player={player} />

          <section className="panel model-info-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">MODEL INFO</span>
                <h2>Analysis Overview</h2>
              </div>
            </div>

            <div className="model-information-grid">
              <div>
                <span>Analysis Type</span>
                <strong>Player Matchup</strong>
              </div>

              <div>
                <span>Trend Window</span>
                <strong>Last 10 Games</strong>
              </div>

              <div>
                <span>Confidence Score</span>
                <strong>{player.confidence}%</strong>
              </div>

              <div>
                <span>Risk Level</span>
                <strong>{player.risk}</strong>
              </div>

              <div>
                <span>Matchup Rating</span>
                <strong>{player.matchupStrength}</strong>
              </div>

              <div>
                <span>Model Status</span>
                <strong>Active</strong>
              </div>
            </div>

            <p className="model-information-note">
              Matchup strength, recent form, strikeout risk, confidence, and
              trends are included in the analysis.
            </p>
          </section>
        </div>

        <div className="detail-right-column">
          <MatchupStrengthMeter player={player} />
          <WhyPrediction player={player} />
          <PremiumToolsPreview />
        </div>
      </section>
    </>
  );
}

function PredictionBoardPage({ players, setSelectedPlayer, openDetail }) {
  return (
    <>
      <section className="page-heading">
        <div>
          <span className="eyebrow">TODAY'S MLB BOARD</span>
          <h1>Prediction Board</h1>
          <p>
            Review player predictions, confidence scores, matchup information,
            and risk levels.
          </p>
        </div>
      </section>

      <section className="panel prediction-board-panel">
        <div className="board-heading-row">
          <span>Player</span>
          <span>Matchup</span>
          <span>Prediction</span>
          <span>Confidence</span>
          <span>Risk</span>
          <span>Status</span>
        </div>

        {players.map((player) => (
          <button
            type="button"
            className="board-player-row"
            key={player.id}
            onClick={() => {
              setSelectedPlayer(player);
              openDetail(player);
            }}
          >
            <span className="board-player-cell">
              <PlayerAvatar player={player} />

              <span>
                <strong>{player.name}</strong>
                <small>
                  {player.teamCode} · {player.position}
                </small>
              </span>
            </span>

            <span>{player.matchup}</span>
            <span>Hit Chance: {player.hitChance}%</span>
            <strong>{player.confidence}%</strong>

            <span className={`risk-badge ${getRiskClass(player.risk)}`}>
              {player.risk}
            </span>

            <span className="board-status">Active</span>
          </button>
        ))}
      </section>
    </>
  );
}

function ModelLabPage() {
  return (
    <>
      <section className="page-heading">
        <div>
          <span className="eyebrow">MODEL INFO</span>
          <h1>Model Lab</h1>
          <p>
            View the player trends, matchup strength, confidence, and risk
            factors used in each prediction.
          </p>
        </div>
      </section>

      <section className="model-lab-grid">
        <section className="panel model-lab-main-card">
          <div className="model-lab-icon">ML</div>

          <div>
            <span className="eyebrow">MODEL TYPE</span>
            <h2>Random Forest / Decision Tree</h2>
            <p>
              The model reviews player trends, matchup conditions, confidence
              scores, and risk factors.
            </p>
          </div>

          <span className="waiting-badge">MODEL ACTIVE</span>
        </section>

        <SummaryCard
          icon="C"
          label="Confidence"
          value="Player Level"
          description="Confidence score for each prediction"
          status="ready"
        />

        <SummaryCard
          icon="R"
          label="Risk Levels"
          value="Three Levels"
          description="Low, moderate, and high ratings"
          status="pending"
        />

        <SummaryCard
          icon="T"
          label="Trend Window"
          value="10 Games"
          description="Recent performance analysis"
          status="waiting"
        />
      </section>

      <section className="panel model-checklist-panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">PREDICTION FACTORS</span>
            <h2>Model Overview</h2>
          </div>
        </div>

        <div className="integration-checklist">
          <div className="complete">
            <span>✓</span>
            <p>
              <strong>Player Trends</strong>
              <small>Recent performance direction</small>
            </p>
          </div>

          <div className="complete">
            <span>✓</span>
            <p>
              <strong>Matchup Strength</strong>
              <small>Pitcher and handedness outlook</small>
            </p>
          </div>

          <div className="complete">
            <span>✓</span>
            <p>
              <strong>Confidence Score</strong>
              <small>Overall prediction confidence</small>
            </p>
          </div>

          <div className="complete">
            <span>✓</span>
            <p>
              <strong>Risk Level</strong>
              <small>Low, moderate, or high risk</small>
            </p>
          </div>

          <div className="complete">
            <span>✓</span>
            <p>
              <strong>Trends</strong>
              <small>Recent ten-game performance window</small>
            </p>
          </div>
        </div>
      </section>
    </>
  );
}

function PremiumPage() {
  return (
    <>
      <section className="page-heading centered-page-heading">
        <div>
          <span className="eyebrow purple-text">PREMIUM TOOLS</span>
          <h1>Premium Tools</h1>
          <p>
            Compare the standard dashboard with advanced matchup and trend
            features.
          </p>
        </div>
      </section>

      <section className="plan-grid">
        <article className="panel plan-card">
          <span className="plan-label">FREE</span>
          <h2>Standard Dashboard</h2>
          <p>Core player prediction tools.</p>

          <div className="plan-price">
            <strong>Included</strong>
            <span>Standard access</span>
          </div>

          <ul>
            <li>Player search</li>
            <li>Confidence scores</li>
            <li>Risk levels</li>
            <li>Recent performance trends</li>
            <li>Daily player predictions</li>
          </ul>

          <button type="button" className="secondary-button full-width-button">
            Current Access
          </button>
        </article>

        <article className="panel plan-card premium-plan-card">
          <span className="plan-label premium">PREMIUM</span>
          <h2>Premium Tools</h2>
          <p>Advanced matchup and performance features.</p>

          <div className="plan-price">
            <strong>Coming Soon</strong>
            <span>Premium access</span>
          </div>

          <ul>
            <li>Custom stat windows</li>
            <li>Saved player watchlist</li>
            <li>Advanced matchup breakdown</li>
            <li>Deeper trend charts</li>
            <li>Player comparison tools</li>
          </ul>

          <button type="button" className="premium-button full-width-button">
            Premium Tools Coming Soon
          </button>
        </article>
      </section>
    </>
  );
}

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [availablePlayers, setAvailablePlayers] = useState(fallbackPlayers);
  const [selectedPlayer, setSelectedPlayer] = useState(fallbackPlayers[0]);
  const [searchText, setSearchText] = useState("");
  const [backendPlayerCount, setBackendPlayerCount] = useState(0);
  const [isLoadingPlayers, setIsLoadingPlayers] = useState(true);
  
  const [dailyMatchups, setDailyMatchups] = useState([]);
  const [dailyPredictions, setDailyPredictions] = useState([]);

  useEffect(() => {
    let requestCancelled = false;
  
    async function loadApplicationData() {
      try {
        const playerResponse = await fetch(PLAYER_API_URL);
  
        if (!playerResponse.ok) {
          throw new Error(
            `Player request failed with status ${playerResponse.status}`,
          );
        }
  
        const playerData = await playerResponse.json();
  
        const backendPlayers = Array.isArray(playerData.players)
          ? playerData.players
          : [];
  
        if (backendPlayers.length === 0) {
          throw new Error("The backend returned an empty player list.");
        }
  
        let loadedMatchups = [];
        let loadedPredictions = [];
  
        try {
          const dashboardResponse = await fetch(DASHBOARD_API_URL);
  
          if (!dashboardResponse.ok) {
            throw new Error(
              `Dashboard request failed with status ${dashboardResponse.status}`,
            );
          }
  
          const dashboardData = await dashboardResponse.json();
  
          loadedMatchups = Array.isArray(dashboardData.matchups)
            ? dashboardData.matchups
            : [];
  
          loadedPredictions = Array.isArray(dashboardData.predictions)
            ? dashboardData.predictions
            : [];
        } catch (dashboardError) {
          console.error(
            "Could not load daily matchup data.",
            dashboardError,
          );
        }
  
        const backendPlayerLookup = new Map(
          backendPlayers.map((backendPlayer) => [
            Number(backendPlayer.player_id),
            backendPlayer,
          ]),
        );
        
        const convertedPlayers = backendPlayers.map((player, index) =>
          convertBackendPlayer(
            player,
            index,
            loadedMatchups,
            loadedPredictions,
            backendPlayerLookup,
          ),
        );

        if (requestCancelled) {
          return;
        }
  
        const returnedCount = Number(playerData.count);
  
        setAvailablePlayers(convertedPlayers);
        setBackendPlayerCount(
          Number.isFinite(returnedCount)
            ? returnedCount
            : convertedPlayers.length,
        );
        setSelectedPlayer(convertedPlayers[0]);
  
        setDailyMatchups(loadedMatchups);
        setDailyPredictions(loadedPredictions);
      } catch (error) {
        console.error(
          "Could not load backend players. Using local players instead.",
          error,
        );
  
        if (!requestCancelled) {
          setAvailablePlayers(fallbackPlayers);
          setBackendPlayerCount(0);
          setSelectedPlayer(fallbackPlayers[0]);
  
          setDailyMatchups([]);
          setDailyPredictions([]);
        }
      } finally {
        if (!requestCancelled) {
          setIsLoadingPlayers(false);
        }
      }
    }
  
    loadApplicationData();
  
    return () => {
      requestCancelled = true;
    };
  }, []);

  const normalizedSearch = searchText.toLowerCase().trim();

  const filteredPlayers = availablePlayers.filter((player) => {
    const searchableText = [
      player.name,
      player.team,
      player.teamCode,
      player.position,
      player.bats,
      player.throws,
    ]
      .join(" ")
      .toLowerCase();

    return searchableText.includes(normalizedSearch);
  });

  const playerLoadLabel = isLoadingPlayers
    ? "Loading players..."
    : backendPlayerCount > 0
      ? `${backendPlayerCount} players loaded`
      : `${availablePlayers.length} players available`;

  function openDetail(player) {
    setSelectedPlayer(player);
    setActivePage("detail");
  }

  function renderPage() {
    if (activePage === "search") {
      return (
        <PlayerSearchPage
          filteredPlayers={filteredPlayers}
          selectedPlayer={selectedPlayer}
          setSelectedPlayer={setSelectedPlayer}
          searchText={searchText}
          setSearchText={setSearchText}
          openDetail={openDetail}
          playerLoadLabel={playerLoadLabel}
        />
      );
    }

    if (activePage === "detail") {
      return (
        <PlayerDetailPage
          player={selectedPlayer}
          setActivePage={setActivePage}
        />
      );
    }

    if (activePage === "predictions") {
      return (
        <PredictionBoardPage
          players={availablePlayers}
          setSelectedPlayer={setSelectedPlayer}
          openDetail={openDetail}
        />
      );
    }

    if (activePage === "model") {
      return <ModelLabPage />;
    }

    if (activePage === "premium") {
      return <PremiumPage />;
    }

    return (
      <DashboardPage
        players={availablePlayers}
        filteredPlayers={filteredPlayers}
        selectedPlayer={selectedPlayer}
        setSelectedPlayer={setSelectedPlayer}
        searchText={searchText}
        setSearchText={setSearchText}
        openDetail={openDetail}
        setActivePage={setActivePage}
        playerLoadLabel={playerLoadLabel}
      />
    );
  }

  return (
    <div className="app-shell">
      <TopNavigation
        activePage={activePage}
        setActivePage={setActivePage}
      />

      <main className="main-content">{renderPage()}</main>

      <footer className="app-footer">
        <span>Team 6 MLB Prediction App | IT 391 | MLB Dashboard</span>
      </footer>
    </div>
  );
}

export default App;