import os
import json
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import log_loss, accuracy_score, brier_score_loss

from backend.database.data import get_table_as_df, get_matchups_between
from backend.models.win.features import build_win_training_dataset

WINDOWS = (15, 30, 50, 100)

MODEL_PATH = "win_model.joblib"
FEATURE_COLS_PATH = "win_model_feature_cols.json"

EXCLUDE_COLS = {"target_home_win", "game_pk", "game_date", "home_team_id", "away_team_id"}


def main():

    # retrieve all the matches from the database
    matchups_df = get_matchups_between("0001-01-01", "2100-01-01")
    # retrieve from the function I made in data.py
    team_stats_df = get_table_as_df("team_game_stats")
    pitcher_stats_df = get_table_as_df("pitcher_game_stats")

    if matchups_df.empty or "winner_team_id" not in matchups_df.columns:
        return

    # windows means the amount of games that it should read just builds the dataframe of the last window
    training_df = build_win_training_dataset(matchups_df, team_stats_df, pitcher_stats_df, windows=WINDOWS)

    if training_df.empty:
        return

    training_df = training_df.sort_values("game_date").reset_index(drop=True)
    feature_cols = [c for c in training_df.columns if c not in EXCLUDE_COLS]

    X = training_df[feature_cols].fillna(-1)
    y = training_df["target_home_win"]

    split_index = int(len(training_df) * 0.8)
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    # Tested Classifiers such as randomforest, gradientboosting, logisticregression and more
    # It seems like the same reason for the one before a lot of tuning
    # Random forest was best in this case, I do want to say win rates in baseball is extremely
    # difficult predicted probabilities are ranged from 40-60% which means each side have solid chances to win
    model = RandomForestClassifier(random_state=42, n_jobs=-1)
    param_grid = {
            "n_estimators": [100, 200],
            "max_depth": [4, 6, 8, None],
            "min_samples_leaf": [5, 10, 20],
    }
    # same as strikeout predictions
    split = TimeSeriesSplit(n_splits=5)
    grid = GridSearchCV(model, param_grid, cv=split)

    # basics results testing fitting weights
    grid.fit(X_train, y_train)
    best_model = grid.best_estimator_
    print(f"Best params: {grid.best_params_}")

    proba = best_model.predict_proba(X_test)[:, 1]
    predictions = (proba >= 0.5).astype(int)

    logloss = log_loss(y_test, proba)
    accuracy = accuracy_score(y_test, predictions)
    brier = brier_score_loss(y_test, proba)
    print(f"Test log loss: {logloss:.4f}")
    print(f"Test accuracy: {accuracy:.4f}")
    print(f"Test Brier score: {brier:.4f}")

    # Write onto the weights onto model to use for the app
    joblib.dump(best_model, MODEL_PATH)
    with open(FEATURE_COLS_PATH, "w") as f:
        json.dump(feature_cols, f)


if __name__ == "__main__":
    main()