import statsapi
from backend.database.data import supabase, get_table_as_df


# function name represents it
def build_name_to_id_cache():
    players_df = get_table_as_df("players")
    if players_df.empty:
        return {}
    # dictionary for lookups by player's name
    return {
        row["full_name"].strip().lower(): row["player_id"]
        for _, row in players_df.iterrows()
        if row.get("full_name")
    }

def resolve_pitcher_id(name, cache):
    if not name:
        return None

    key = name.strip().lower()
    if key in cache:
        return cache[key]

    try:
        # if not in the cache look it up
        results = statsapi.lookup_player(name)
    except Exception as e:
        print(f"Error 1 in k_model.py")
        return None

    # name isnt in the database
    if not results:
        return None

    # get the
    match = results[0]
    player_id = match["id"]
    full_name = match["fullName"]

    supabase.table("players").upsert({"player_id": player_id, "full_name": full_name}).execute()
    cache[key] = player_id
    cache[full_name.strip().lower()] = player_id
    return player_id
