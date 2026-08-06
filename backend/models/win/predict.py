import json
import joblib
import datetime
import pandas as pd
from pathlib import Path

from backend.database.data import get_table_as_df, get_matchups_between, upsert_rows
from backend.models.win.features import WinFeatureEngineer

WINDOWS = (15, 30, 50, 100, 200)
PREDICTION_TYPE = "win_probability"

DIR = Path(__file__).resolve().parent
MODEL_PATH = DIR / "win_model.joblib"
FEATURE_COLS_PATH = DIR / "win_model_feature_cols.json"


def confidence_and_risk(home_win_prob):
    distance_from_toss_up = abs(home_win_prob - 0.5) * 2
    confidence = int(round(distance_from_toss_up * 100))

    if confidence >= 60:
        risk = "Low"
    elif confidence >= 30:
        risk = "Medium"
    else:
        risk = "High"
    return confidence, risk


def predict_for_date(date_str):
    # default date is today if None
    if date_str is None:
        target_date = datetime.date.today()
    else:
        target_date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
    target_date = str(target_date)

    # load the saved weights from the train file
    model = joblib.load(MODEL_PATH)
    with open(FEATURE_COLS_PATH) as f:
        feature_cols = json.load(f)

    # get all the games from the range of dates
    matchups = get_matchups_between(target_date, target_date)
    if matchups.empty:
        return

    # get dataframe for stats
    team_stats_df = get_table_as_df("team_game_stats")
    pitcher_stats_df = get_table_as_df("pitcher_game_stats")
    fe = WinFeatureEngineer(team_stats_df, pitcher_stats_df, windows=WINDOWS)

    prediction_rows = []
    for _, game in matchups.iterrows():
        # build dictionary for the feature engineering
        feat_row = fe.build_matchup_features(
            home_team_id=game.home_team_id,
            away_team_id=game.away_team_id,
            home_pitcher_id=game.get("home_probable_pitcher_id"),
            away_pitcher_id=game.get("away_probable_pitcher_id"),
            as_of_date=target_date,
            windows=WINDOWS,
        )
        # make all the empty rows set to Na
        X_row = pd.DataFrame([feat_row])[feature_cols].fillna(-1)
        # predict a probability of winning like 54%-46%
        home_win_proba = float(model.predict_proba(X_row)[:, 1][0])
        away_win_proba = 1.0 - home_win_proba

        confidence, risk = confidence_and_risk(home_win_proba)

        # add the predicted
        prediction_rows.append({
            "game_date": target_date,
            "game_pk": int(game.game_pk),
            "team_id": int(game.home_team_id),
            "opponent_team_id": int(game.away_team_id),
            "prediction_type": PREDICTION_TYPE,
            "predicted_value": round(home_win_proba * 100, 2),
            "confidence_score": confidence,
            "risk_level": risk,
        })
        # just swapped the away team and the home team ids
        prediction_rows.append({
            "game_date": target_date,
            "game_pk": int(game.game_pk),
            "team_id": int(game.away_team_id),
            "opponent_team_id": int(game.home_team_id),
            "prediction_type": PREDICTION_TYPE,
            "predicted_value": round(away_win_proba * 100, 2),
            "confidence_score": confidence,
            "risk_level": risk,
        })

    # send it to data.py function to save it
    if prediction_rows:
        upsert_rows("daily_team_predictions", prediction_rows,  on_conflict="game_date,team_id,prediction_type")
    else:
        print("No predictions")
