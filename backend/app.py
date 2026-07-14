import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
from model_service import model_service

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="MLB Sports Analytics Engine API")
# CORSMiddleware is for security
# change all the * when we publish this online. This is for local
# * means accept from every website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "MLB Predictive Engine API is live"}

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



@app.get("/api/players")
def get_player_directory():
    """
    Returns all player's id, name, position, bat side, throw hand, team's id
    """
    try:
        response = supabase.table("players").select("player_id, full_name, primary_position, bat_side, throw_hand, team_id").execute()
        return {"count": len(response.data), "players": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# PLAYER SEARCH ENDPOINT

@app.get("/api/players/search")
def search_players(
    name: Optional[str] = Query(None, description="Partial, case-insensitive match on player full name, e.g. 'judge'"),
    team_id: Optional[int] = Query(None, description="Exact match on team id, e.g. 147"),
    position: Optional[str] = Query(None, description="Exact match on position abbreviation, e.g. 'SS', 'P', 'OF'"),
):
    """
    Searches the player directory by any combination of name, team, and position.
    All filters are optional and combine with AND logic. Calling with no filters
    behaves like /api/players (returns the full roster).
    """
    try:
        query = supabase.table("players").select(
            "player_id, full_name, primary_position, bat_side, throw_hand, team_id"
        )

        if name:
            query = query.ilike("full_name", f"%{name}%")
        if team_id is not None:
            query = query.eq("team_id", team_id)
        if position:
            query = query.eq("primary_position", position.upper())

        response = query.execute()
        return {"count": len(response.data), "players": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/teams")
def get_teams_directory():
    """
    Returns all team's name, id, abbreviation
    """
    try:
        response = supabase.table("teams").select("team_id, team_name, abbreviation").execute()
        return {"count": len(response.data), "players": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/{game_date}")
def get_daily_dashboard(game_date: str):
    """
    Gets the match up for the day and predicts all the prediction
    for the day format it is this: YYYY-MM-DD
    """
    try:
        matchups_res = supabase.table("daily_matchups").select("*").eq("game_date", game_date).execute()

        predictions_res = supabase.table("daily_predictions").select("*").eq("game_date", game_date).execute()

        return {
            "date": game_date,
            "matchups": matchups_res.data,
            "predictions": predictions_res.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database fetch failed: {str(e)}")

