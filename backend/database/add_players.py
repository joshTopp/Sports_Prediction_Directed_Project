import os
import statsapi
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_KEY = os.getenv("DATABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def seed_active_mlb_players():
    try:
        teams = statsapi.get('teams', {'sportIds': 1, 'activeStatus': 'Yes'})['teams']
    except Exception as e:
        print(f"Failed 1: {e}")
        return

    all_players_payload = []

    for team in teams:
        team_id = team['id']
        team_name = team['name']
        print(f"Fetching {team_name}...")

        try:
            # Grab the active roster
            roster = statsapi.get('team_roster', {'teamId': team_id})['roster']

            for member in roster:
                person = member['person']
                player_id = person['id']
                position = member['position']

                player_detail = statsapi.lookup_player(player_id)

                bat_side = "R"  # Default fallback
                throw_hand = "R"

                if player_detail and len(player_detail) > 0:
                    p_info = player_detail[0]
                    bat_side = p_info.get('batSide', {}).get('code', 'R')
                    throw_hand = p_info.get('pitchHand', {}).get('code', 'R')
                player_row = {
                    "player_id": player_id,
                    "full_name": person['fullName'],
                    "primary_position": position.get('abbreviation', 'N/A'),
                    "team_id": team_id,
                    "bat_side": bat_side,
                    "throw_hand": throw_hand
                }
                all_players_payload.append(player_row)

        except Exception as e:
            print(f"Error {team_id}: {e}")

    if all_players_payload:
        try:
            try:
                supabase.rpc("dummy_cache_refresh", {}).execute()
            except:
                pass

            supabase.table("players").upsert(all_players_payload).execute()
            print("Players have been added to the table")
        except Exception as e:
            print(f"Failed 2: {e}")
    else:
        print("No players")


if __name__ == "__main__":
    seed_active_mlb_players()