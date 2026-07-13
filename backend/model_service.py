import joblib
import pandas as pd

"""
ML MODEL SERVICE

References:
- MLB Stats: https://www.mlb.com/stats/
- Ballpark Pal: https://www.ballparkpal.com/
- BAT X: https://rotogrinders.com/the-bat
"""

class ModelService:

    def __init__(self):
        try:
            self.model = joblib.load("models/game_model.joblib")
        except:
            self.model = None

    def predict_game(self, data):

        if self.model is None:
            return {"error": "Model not loaded yet"}

        df = pd.DataFrame([data])

        prediction = self.model.predict(df)[0]
        probabilities = self.model.predict_proba(df)[0]

        return {
            "winner": "home" if prediction == 1 else "away",
            "confidence": float(max(probabilities))
        }


model_service = ModelService()
