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

    def get_risk_level(self, confidence):
        confidence_percent = confidence * 100

        if confidence_percent >= 80:
            return "Low"
        elif confidence_percent >= 60:
            return "Medium"
        else:
            return "High"

    def predict_game(self, data):
        df = pd.DataFrame([data])

        prediction = self.model.predict(df)[0]
        probabilities = self.model.predict_proba(df)[0]

        confidence = max(probabilities)
        confidence_score = round(confidence * 100, 2)
        risk_level = self.get_risk_level(confidence)

        return {
            "winner": "home" if prediction == 1 else "away",
            "confidence_score": confidence_score,
            "risk_level": risk_level
        }


model_service = ModelService()
