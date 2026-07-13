import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

"""
TRAINING SCRIPT

Uses MLB-style features to predict game outcomes.
"""

# Create dummy dataset (you can replace later)
data = {
    "home_win_pct": [0.6, 0.55, 0.7, 0.4],
    "away_win_pct": [0.5, 0.6, 0.65, 0.45],
    "home_ops": [0.78, 0.75, 0.80, 0.70],
    "away_ops": [0.72, 0.77, 0.78, 0.69],
    "home_era": [3.5, 4.0, 3.2, 4.5],
    "away_era": [4.2, 3.8, 3.9, 4.8],
    "home_team_won": [1, 0, 1, 0]
}

df = pd.DataFrame(data)

X = df[[
    "home_win_pct",
    "away_win_pct",
    "home_ops",
    "away_ops",
    "home_era",
    "away_era"
]]

y = df["home_team_won"]

model = DecisionTreeClassifier()
model.fit(X, y)

# Ensure models folder exists
os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/game_model.joblib")

print("Model trained and saved!")
