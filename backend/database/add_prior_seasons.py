import datetime
import statsapi
import requests
import time
from data import supabase, upsert_rows
from backend.models.strikeouts.k_model import build_name_to_id_cache, resolve_pitcher_id

# official MLB Stats API endpoints
BASE_URL = "https://statsapi.mlb.com/api/v1"

# Innings Pitched
def outs_to_ip(outs):
    # 1 full inning for one side equals to 3 outs
    return round(outs / 3.0, 1) if outs else 0.0


#retrieves the boxscore of the specific games using the mlbstats endpoint
def get_boxscore(game_pk):
    response = requests.get(f"{BASE_URL}/game/{game_pk}/boxscore", timeout=15)
    response.raise_for_status()
    time.sleep(0.25)
    return response.json()


def extract_pitcher_and_team_rows(game_pk, game_date, box):
    pitcher_rows = []
    team_rows = []
    sides = {"home": "away", "away": "home"}

    # retrieve runs scored by each side
    home_runs = box["teams"]["home"].get("teamStats", {}).get("batting", {}).get("runs", 0)
    away_runs = box["teams"]["away"].get("teamStats", {}).get("batting", {}).get("runs", 0)

    # go both sides and retrieve home and away stats
    for side, opp_side in sides.items():
        team_block = box["teams"][side]
        team_id = team_block["team"]["id"]
        opp_team_id = box["teams"][opp_side]["team"]["id"]

        runs_scored = home_runs if side == "home" else away_runs
        runs_allowed = away_runs if side == "home" else home_runs

        # batting stats for teams
        batting = team_block.get("teamStats", {}).get("batting", {})
        team_rows.append({
            "game_pk": game_pk,
            "team_id": team_id,
            "game_date": game_date,
            "team_strikeouts": batting.get("strikeOuts", 0),
            "team_plate_appearances": batting.get("plateAppearances", batting.get("atBats", 0)),
            "runs_scored": runs_scored,
            "runs_allowed": runs_allowed,
            "is_win": runs_scored > runs_allowed
        })

        # retrieves each pitcher stats on the team
        players = team_block.get("players", {})
        pitcher_order = team_block.get("pitchers", [])
        for idx, pid in enumerate(pitcher_order):
            pdata = players.get(f"ID{pid}", {})
            stats = pdata.get("stats", {}).get("pitching", {})
            # ignore players with no pitching stats
            if not stats:
                continue
            # get the statline for the pitchers that I think is useful for my feature engineering
            pitcher_rows.append({
                "game_pk": game_pk,
                "player_id": pid,
                "team_id": team_id,
                "opponent_team_id": opp_team_id,
                "game_date": game_date,
                "is_home": side == "home",
                "is_starter": idx == 0,
                "innings_pitched": outs_to_ip(stats.get("outs", 0)),
                "strikeouts": stats.get("strikeOuts", 0),
                "walks": stats.get("baseOnBalls", 0),
                "batters_faced": stats.get("battersFaced", 0),
                "hits_allowed": stats.get("hits", 0),
                "pitches_thrown": stats.get("numberOfPitches", 0),
                "strikes_thrown": stats.get("strikes", 0),
            })

    return pitcher_rows, team_rows


def extract_matchup_result(box):
    # get team ids and retrieve the results of the matches of both
    home_id = box["teams"]["home"]["team"]["id"]
    away_id = box["teams"]["away"]["team"]["id"]
    home_runs = box["teams"]["home"].get("teamStats", {}).get("batting", {}).get("runs", 0)
    away_runs = box["teams"]["away"].get("teamStats", {}).get("batting", {}).get("runs", 0)

    return {
        "home_score": home_runs,
        "away_score": away_runs,
        # faster way of wins
        "winner_team_id": home_id if home_runs > away_runs else away_id,
    }

# makes sure the pitchers are in the database if not add them with unknown
def ensure_players_exist(pitcher_rows):
    seen = {r["player_id"] for r in pitcher_rows}
    if not seen:
        return
    existing = supabase.table("players").select("player_id").in_("player_id", list(seen)).execute()
    existing_ids = {r["player_id"] for r in existing.data}
    missing = seen - existing_ids
    for pid in missing:
        supabase.table("players").upsert({"player_id": pid, "full_name": f"Unknown ({pid})"}).execute()


def upsert_matchup(game, current_date, name_cache):
    game_pk = game['game_id']

    # get the probable pitchers and get retrieve its id using cache
    home_pitcher = game.get('home_probable_pitcher')
    home_pitcher = resolve_pitcher_id(home_pitcher, name_cache)

    away_pitcher = game.get('away_probable_pitcher')
    away_pitcher = resolve_pitcher_id(away_pitcher, name_cache)

    try:
        # insert home team
        supabase.table("teams").upsert({
            "team_id": game['home_id'],
            "team_name": game['home_name'],
            "abbreviation": game['home_name'][:3].upper(),
        }).execute()
        # insert away team
        supabase.table("teams").upsert({
            "team_id": game['away_id'],
            "team_name": game['away_name'],
            "abbreviation": game['away_name'][:3].upper(),
        }).execute()
        # insert the daily matchup
        supabase.table("daily_matchups").upsert({
            "game_pk": game_pk,
            "game_date": str(current_date),
            "home_team_id": game['home_id'],
            "away_team_id": game['away_id'],
            "home_probable_pitcher_id": home_pitcher,
            "away_probable_pitcher_id": away_pitcher,
        }).execute()
        return True

    except Exception as e:
        print(f"  Error 1 add_prior_seasons.py: {e}")
        return False

def backfill_season(start_date_string, end_date_string):
    # convert the strings to the time format accepted
    start_date = datetime.datetime.strptime(start_date_string, "%m/%d/%Y").date()
    end_date = datetime.datetime.strptime(end_date_string, "%m/%d/%Y").date()

    current_date = start_date
    time_delta = datetime.timedelta(days=1)
    # used for strikeouts in k_model.py func
    name_cache = build_name_to_id_cache()

    # keep going through days till you reach the end date
    while current_date <= end_date:
        date_string = current_date.strftime('%m/%d/%Y')
        try:
            # retrieve the schedule of the day
            schedule = statsapi.schedule(date=date_string)
        except Exception as e:
            print(f"Error 2 add_prior_seasons.py: {e}")
            current_date += time_delta
            continue

        # initialize variables
        all_pitcher_rows, all_team_rows = [], []
        matchups_written, stats_written = 0, 0

        # retrieve and only add games from the regular season and post season
        for game in schedule:
            if game.get('game_type') not in ['R', 'W']:
                continue

            game_pk = game['game_id']

            # send to database continues if it goes wrong
            if not upsert_matchup(game, current_date, name_cache):
                continue
            matchups_written += 1

            # games have to be final to be added to stats
            if game.get("status") != "Final":
                continue

            try:
                box = get_boxscore(game_pk)
            except Exception as e:
                print(f"Error 3 add_prior_seasons.py: {e}")
                continue

            # retrieves pitcher and team rows
            pitcher_rows, team_rows = extract_pitcher_and_team_rows(game_pk, str(current_date), box)
            all_pitcher_rows.extend(pitcher_rows)
            all_team_rows.extend(team_rows)

            try:
                # Update the table of daily_matchups
                result = extract_matchup_result(box)
                supabase.table("daily_matchups").upsert({
                    "game_pk": game_pk,
                    "game_date": str(current_date),
                    "home_team_id": game['home_id'],
                    "away_team_id": game['away_id'],
                    **result,
                }).execute()
            except Exception as e:
                print(f"Error 4 add_prior_seasons.py: {e}")

            stats_written += 1

        # send all the infor to the database
        if all_pitcher_rows:
            ensure_players_exist(all_pitcher_rows)
            upsert_rows("pitcher_game_stats", all_pitcher_rows)
        if all_team_rows:
            upsert_rows("team_game_stats", all_team_rows)

        current_date += time_delta

# This is just temporary to fill past games update_data_script will be ran for now on daily
if __name__ == "__main__":
    backfill_season("07/30/2026", "7/31/2026")