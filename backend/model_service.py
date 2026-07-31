import logging
from pathlib import Path

import joblib
import pandas as pd


"""
ML MODEL SERVICE

References:
- Ballpark Pal: https://www.ballparkpal.com/
- BAT X: https://rotogrinders.com/the-bat
"""


logger = logging.getLogger(__name__)


class ModelService:

    def __init__(self):
        self.model = None
        self.model_ready = False
        self.model_error = None

        backend_folder = Path(__file__).resolve().parent
        self.model_path = backend_folder / "models" / "game_model.joblib"

        self.load_model()

    def load_model(self):
        """
        Attempts to load the ML model.

        The FastAPI server is allowed to continue starting when the model
        file is missing or cannot be loaded.
        """
        try:
            self.model = joblib.load(self.model_path)
            self.model_ready = True
            self.model_error = None

            logger.info("ML model loaded from %s", self.model_path)

        except FileNotFoundError:
            self.model = None
            self.model_ready = False
            self.model_error = (
                f"Model file was not found at {self.model_path}"
            )

            logger.warning(self.model_error)

        except Exception as error:
            self.model = None
            self.model_ready = False
            self.model_error = (
                f"Model could not be loaded: {error}"
            )

            logger.exception(self.model_error)

  def predict_game(self, data):

    if self.model is None:
        return {"error": "Model not loaded yet"}

    df = pd.DataFrame([data])

    prediction = self.model.predict(df)[0]
    probabilities = self.model.predict_proba(df)[0]

    home_prob = float(probabilities[1])
    away_prob = float(probabilities[0])

    return {
        "winner": "home" if prediction == 1 else "away",
        "home_win_probability": round(home_prob, 3),
        "away_win_probability": round(away_prob, 3),
        "confidence": round(max(home_prob, away_prob), 3)
    }


model_service = ModelService()
