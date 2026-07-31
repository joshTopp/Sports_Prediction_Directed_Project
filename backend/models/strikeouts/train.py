import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from lightgbm import LGBMRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error

from backend.database.data import get_table_as_df
from features import build_training_dataset

WINDOWS = (15, 30, 50)

MODEL_PATH = "k_model.joblib"
FEATURE_COLS_PATH = "k_model_feature_cols.json"

EXCLUDE_COLS = {"target_K", "game_pk", "game_date", "player_id", "opponent_team_id"}


def main():
    # retrieve from the function I made in data.py
    pitcher_stats_df = get_table_as_df("pitcher_game_stats")
    team_stats_df = get_table_as_df("team_game_stats")

    if pitcher_stats_df.empty:
        return

    # windows means the amount of games that it should read just builds the dataframe of the last window
    training_df = build_training_dataset(pitcher_stats_df, team_stats_df, windows=WINDOWS)
    training_df = training_df.sort_values("game_date").reset_index(drop=True)
    feature_cols = [c for c in training_df.columns if c not in EXCLUDE_COLS]

    # testing different models so fillna is predicted wrong by some models just incase I want to test different models
    # X = training_df[feature_cols].fillna(training_df[feature_cols].median())
    X = training_df[feature_cols]
    y = training_df["target_K"]

    # get training and test splits
    split_idx = int(len(training_df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # using gridsearchcv to test multiple depths and leaves
    param_grid = {
        "max_depth": [4, 5, 8, 10],
        "min_samples_leaf": [5, 10, 20, 40],
    }
    # Tested A lot of regressors gradient descents like LightGBM, CatBoost, xgBoost, randomforest, decision trees.
    # It seems like all of them required a lot of tuning with optuna.
    # lightbgm suits this well in my opinion
    model = LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leave=31, random_state=42)
    split = TimeSeriesSplit(n_splits=5)
    grid = GridSearchCV(model, param_grid, cv=split, scoring="neg_mean_absolute_error")

    # basics results testing fitting weights
    grid.fit(X_train, y_train)
    model = grid.best_estimator_
    print("Best params:", grid.best_params_)

    predictions = model.predict(X_test)
    print("\nMean Absolute Error:", mean_absolute_error(y_test, predictions))
    print("Mean Squared error:", mean_squared_error(y_test, predictions) ** 0.5)

    importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print("\nFeature weights:")
    print(importances.head(10))

    # Write onto the weights onto model to use for the app
    joblib.dump(model, MODEL_PATH)
    with open(FEATURE_COLS_PATH, "w") as f:
        json.dump(feature_cols, f)


if __name__ == "__main__":
    main()