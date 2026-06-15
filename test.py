import json
import statsapi

player_id = 592450

print("Fetching stats...")
raw_stats = statsapi.player_stat_data(player_id, group="hitting", type="season")

stats_list = raw_stats.get("stats", [])

if stats_list:
    print("--- ALL AVAILABLE COLUMNS IN THE FIRST ROW ---")
    print(json.dumps(stats_list[0], indent=4))