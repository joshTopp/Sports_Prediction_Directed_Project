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


def backfill_season(start_date_str, end_date_str):
    start_date = datetime.datetime.strptime(start_date_str, "%m/%d/%Y").date()
    end_date = datetime.datetime.strptime(end_date_str, "%m/%d/%Y").date()

    current_date = start_date
    delta = datetime.timedelta(days=1)


    while current_date <= end_date:
        date_str = current_date.strftime('%m/%d/%Y')
        try:
            schedule = statsapi.schedule(date=date_str)
        except Exception as e:
            print(f"Error fetching data for {date_str}: {e}")
            current_date += delta
            continue

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

            if home_pitcher:
                supabase.table("players").upsert(
                    {"player_id": home_pitcher, "full_name": game.get('home_probable_pitcher_name')}).execute()
            if away_pitcher:
                supabase.table("players").upsert(
                    {"player_id": away_pitcher, "full_name": game.get('away_probable_pitcher_name')}).execute()

            matchup_data = {
                "game_pk": game_pk,
                "game_date": str(current_date),
                "home_team_id": game['home_id'],
                "away_team_id": game['away_id'],
                "home_probable_pitcher_id": home_pitcher,
                "away_probable_pitcher_id": away_pitcher
            }
            supabase.table("daily_matchups").upsert(matchup_data).execute()

        current_date += delta

# This is just temporary
if __name__ == "__main__":
    backfill_season("06/28/2026", "07/11/2026")