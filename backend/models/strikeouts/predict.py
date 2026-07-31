import sys
import json
import joblib
import datetime
import numpy as np
import pandas as pd
from pathlib import Path

from backend.database.data import get_table_as_df, get_matchups_between, upsert_rows
from backend.models.strikeouts.features import FeatureEngineer

WINDOWS = (15, 30, 50, 100)
PREDICTION_TYPE = "strikeouts"

DIR = Path(__file__).resolve().parent
MODEL_PATH = DIR / "k_model.joblib"
FEATURE_COLS_PATH = DIR / "k_model_feature_cols.json"


def confidence_and_risk(row, smallest_window):
    # get the smallest amount of games get the standard deviation
    n_games = row.get(f"L{smallest_window}_n_games", 0) or 0
    k_std = row.get(f"L{smallest_window}_k_std", np.nan)
    # if standard deviation is none set to 0
    k_std = 0.0 if pd.isna(k_std) else k_std

    data_score = min(n_games / smallest_window, 1.0) * 60
    stability_score = max(0.0, 40 - k_std * 10)
    # confidence needs to range from 0-100 so clip to that range convert to int and round
    confidence = int(round(np.clip(data_score + stability_score, 0, 100)))

    if confidence >= 70:
        risk = "Low"
    elif confidence >= 45:
        risk = "Medium"
    else:
        risk = "High"
    return confidence, risk

# basically the same as predict for win%, so im not going to put comments
def predict_for_date(date_str):

    if date_str is None:
        target_date = datetime.date.today()
    else:
        target_date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
    target_date = str(target_date)

    model = joblib.load(MODEL_PATH)
    with open(FEATURE_COLS_PATH) as f:
        feature_cols = json.load(f)

    matchups = get_matchups_between(target_date, target_date)
    if matchups.empty:
        return

    pitcher_stats_df = get_table_as_df("pitcher_game_stats")
    team_stats_df = get_table_as_df("team_game_stats")
    fe = FeatureEngineer(pitcher_stats_df, team_stats_df, windows=WINDOWS)
    smallest_window = min(WINDOWS)

    prediction_rows = []
    for _, game in matchups.iterrows():
        for pitcher_id, opp_team_id, is_home in [
            (game.home_probable_pitcher_id, game.away_team_id, True),
            (game.away_probable_pitcher_id, game.home_team_id, False),
        ]:
            if pd.isna(pitcher_id):
                continue
            pitcher_id = int(pitcher_id)

            feat_row = fe.build_feature_row(
                player_id=pitcher_id,
                opponent_team_id=int(opp_team_id),
                as_of_date=target_date,
                is_home=is_home,
                windows=WINDOWS,
            )
            X_row = pd.DataFrame([feat_row])[feature_cols].fillna(-1)
            predicted_k = float(model.predict(X_row)[0])
            confidence, risk = confidence_and_risk(feat_row, smallest_window)

            prediction_rows.append({
                "game_date": target_date,
                "player_id": pitcher_id,
                "prediction_type": PREDICTION_TYPE,
                "predicted_value": round(predicted_k, 2),
                "confidence_score": confidence,
                "risk_level": risk,
            })

    if prediction_rows:
        upsert_rows("daily_predictions", prediction_rows, on_conflict="game_date,player_id,prediction_type")
    else:
        print("Pitchers not listed yet")
