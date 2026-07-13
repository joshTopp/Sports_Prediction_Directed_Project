import joblib
import pandas as pd

"""
ML MODEL SERVICE

References:
- Ballpark Pal: https://www.ballparkpal.com/
- BAT X: https://rotogrinders.com/the-bat
"""

class ModelService:

    def __init__(self):
        self.model = joblib.load("models/game_model.joblib")

    def predict_game(self, data):

        df = pd.DataFrame([data])

        prediction = self.model.predict(df)[0]
        probabilities = self.model.predict_proba(df)[0]

        return {
            "winner": "home" if prediction == 1 else "away",
            "confidence": max(probabilities)
        }


model_service = ModelService()
