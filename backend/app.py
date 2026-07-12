import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv

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


@app.get("/api/teams")
def get_player_directory():
    """
    Returns all team's name, id, abbreviation
    """
    try:
        response = supabase.table("teams").select("team_id, team_name, abbreviation").execute()
        return {"count": len(response.data), "players": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))