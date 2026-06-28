
CREATE TABLE teams (
    team_id INT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL
);

CREATE TABLE players (
    player_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    primary_position VARCHAR(10),
    bat_side CHAR(1),
    throw_hand CHAR(1)
);

CREATE TABLE daily_matchups (
    game_pk INT PRIMARY KEY,
    game_date DATE NOT NULL,
    home_team_id INT REFERENCES teams(team_id),
    away_team_id INT REFERENCES teams(team_id),
    home_probable_pitcher_id INT,
    away_probable_pitcher_id INT
);

CREATE TABLE daily_predictions (
    prediction_id SERIAL PRIMARY KEY,
    game_date DATE NOT NULL,
    player_id INT REFERENCES players(player_id),
    prediction_type VARCHAR(30),
    predicted_value NUMERIC(5, 2) NOT NULL,
    confidence_score INT NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    UNIQUE(game_date, player_id, prediction_type)
);