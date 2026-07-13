from fastapi import FastAPI
from model_service import model_service


# GAME PREDICTION ENDPOINT

@app.post("/predict/game")
def predict_game(data: dict):
    result = model_service.predict_game(data)
    return result



# EXPLANATION FEATURE (KEY DIFFERENTIATOR)

@app.post("/predict/game/explain")
def explain_prediction(data: dict):
    result = model_service.predict_game(data)

    explanation = []

    if data["home_ops"] > data["away_ops"]:
        explanation.append("Home team has stronger offense (higher OPS).")

    if data["home_era"] < data["away_era"]:
        explanation.append("Home team has better pitching (lower ERA).")

    return {
        "prediction": result,
        "explanation": explanation,
        "sources": [
            "https://www.mlb.com/stats/",
            "https://www.ballparkpal.com/"
        ]
    }



# REFERENCES ENDPOINT (FOR PROJECT REQUIREMENTS)

@app.get("/references")
def references():
    return {
        "MLB Stats": "https://www.mlb.com/stats/",
        "MLB API": "https://github.com/toddrob99/MLB-StatsAPI/wiki",
        "Ballpark Pal": "https://www.ballparkpal.com/",
        "BAT X": "https://rotogrinders.com/the-bat",
        "Chart.js": "https://www.chartjs.org/",
        "Tailwind CSS": "https://tailwindcss.com/",
        "PostgreSQL": "https://www.postgresql.org/"
    }
