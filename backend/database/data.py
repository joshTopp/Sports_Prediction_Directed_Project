import datetime
import os
import statsapi
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("DATABASE_URL")
key = os.getenv("DATABASE_KEY")

supabase = create_client(url, key)


def ensure_team_and_player_exists(cursor, team_id, team_name, pitcher_id, pitcher_name):
    """Ensures parent records exist before inserting matchups to prevent FK constraints."""
    if team_id:
        cursor.execute("""
            INSERT INTO teams (team_id, team_name, abbreviation)
            VALUES (%s, %s, %s)
            ON CONFLICT (team_id) DO NOTHING;
        """, (team_id, team_name, team_name[:3].upper()))

    if pitcher_id and pitcher_name:
        cursor.execute("""
            INSERT INTO players (player_id, full_name)
            VALUES (%s, %s)
            ON CONFLICT (player_id) DO NOTHING;
        """, (pitcher_id, pitcher_name))


def fetch_daily_schedule():
    # Today's date for the API request
    today_str = datetime.date.today().strftime('%m/%d/%Y')
    print(f"Fetching MLB schedule for {today_str}...")

    # 1. Removed dict_keys=True to prevent the unexpected keyword argument error
    schedule = statsapi.schedule(date=today_str)

    matchups = []
    for game in schedule:
        if game.get('game_type') not in ['R', 'W']:
            continue

        game_pk = game['game_id']

        home_pitcher = game.get('home_probable_pitcher_id')
        home_pitcher = int(home_pitcher) if home_pitcher and str(home_pitcher).isdigit() else None

        away_pitcher = game.get('away_probable_pitcher_id')
        away_pitcher = int(away_pitcher) if away_pitcher and str(away_pitcher).isdigit() else None

        supabase.table("teams").upsert({"team_id": game['home_id'], "team_name": game['home_name'],
                                        "abbreviation": game['home_name'][:3].upper()}).execute()
        supabase.table("teams").upsert({"team_id": game['away_id'], "team_name": game['away_name'],
                                        "abbreviation": game['away_name'][:3].upper()}).execute()

        if home_pitcher and game.get('home_probable_pitcher_name'):
            supabase.table("players").upsert(
                {"player_id": home_pitcher, "full_name": game.get('home_probable_pitcher_name')}).execute()
        if away_pitcher and game.get('away_probable_pitcher_name'):
            supabase.table("players").upsert(
                {"player_id": away_pitcher, "full_name": game.get('away_probable_pitcher_name')}).execute()

        matchup_data = {
            "game_pk": game_pk,
            "game_date": str(datetime.date.today()),  # Format as 'YYYY-MM-DD' string for Postgres DATE types
            "home_team_id": game['home_id'],
            "away_team_id": game['away_id'],
            "home_probable_pitcher_id": home_pitcher,
            "away_probable_pitcher_id": away_pitcher
        }
        supabase.table("daily_matchups").upsert(matchup_data).execute()

        matchups.append(game)

    return matchups


def generate_and_save_predictions(matchups):
    today = datetime.date.today()

    for game in matchups:
        # Process starting pitchers for daily K predictions
        home_pitcher_id = game.get('home_probable_pitcher_id')
        away_pitcher_id = game.get('away_probable_pitcher_id')

        # Normalize pitcher values to valid integers
        pitchers_to_predict = [pid for pid in [home_pitcher_id, away_pitcher_id] if pid and str(pid).isdigit()]

        for pitcher_id in pitchers_to_predict:
            pitcher_id = int(pitcher_id)

            # this for an example ML model specifically strikeout predictions
            # features = gather_features_for_pitcher(pitcher_id)
            # predicted_value = ml_model.predict(features)
            # predicted_so = 5.8
            # confidence = 82
            # risk = "Medium"


# This is just temporary
if __name__ == "__main__":
    today_games = fetch_daily_schedule()