import numpy as np
import pandas as pd


class WinFeatureEngineer:
    # same initialize func as the other features file except instead of team its pitcher
    def __init__(self, team_stats_df, pitcher_stats_df, windows=(15, 30)):
        self.windows = windows

        self.team_stats = team_stats_df.copy()
        if not self.team_stats.empty:
            self.team_stats["game_date"] = pd.to_datetime(self.team_stats["game_date"])
            self.team_stats = self.team_stats.sort_values(["team_id", "game_date"]).reset_index(drop=True)

        self.pitcher_stats = pitcher_stats_df.copy()
        if not self.pitcher_stats.empty:
            self.pitcher_stats["game_date"] = pd.to_datetime(self.pitcher_stats["game_date"])
            self.pitcher_stats = self.pitcher_stats.sort_values(["player_id", "game_date"]).reset_index(drop=True)

    def team_window_features(self, team_id, as_of_date, window, prefix):
        p = f"{prefix}_L{window}"
        if self.team_stats.empty:
            hist = pd.DataFrame()
        else:
            hist = self.team_stats[
                (self.team_stats.team_id == team_id) &
                (self.team_stats.game_date < pd.Timestamp(as_of_date))
                ].tail(window)

        n = len(hist)
        if n == 0:
            return {
                f"{p}_n_games": 0,
                f"{p}_win_pct": np.nan,
                f"{p}_run_diff_avg": np.nan,
                f"{p}_runs_scored_avg": np.nan,
                f"{p}_runs_allowed_avg": np.nan,
            }

        return {
            f"{p}_n_games": n,
            f"{p}_win_pct": hist["is_win"].mean(),
            f"{p}_run_diff_avg": (hist["runs_scored"] - hist["runs_allowed"]).mean(),
            f"{p}_runs_scored_avg": hist["runs_scored"].mean(),
            f"{p}_runs_allowed_avg": hist["runs_allowed"].mean(),
        }

    def days_rest(self, team_id, as_of_date):
        if self.team_stats.empty:
            return np.nan
        hist = self.team_stats[(self.team_stats.team_id == team_id) &(self.team_stats.game_date < pd.Timestamp(as_of_date))]
        if hist.empty:
            return np.nan
        return (pd.Timestamp(as_of_date) - hist["game_date"].max()).days

    def starter_window_features(self, player_id, as_of_date, window, prefix):
        p = f"{prefix}_L{window}"
        if player_id is None or pd.isna(player_id) or self.pitcher_stats.empty:
            hist = pd.DataFrame()
        else:
            hist = self.pitcher_stats[
                (self.pitcher_stats.player_id == player_id) &
                (self.pitcher_stats.is_starter == True) &
                (self.pitcher_stats.game_date < pd.Timestamp(as_of_date))
                ].tail(window)

        n = len(hist)
        if n == 0:
            return {
                f"{p}_n_games": 0,
                f"{p}_k9": np.nan,
                f"{p}_bb_pct": np.nan,
                f"{p}_ip_per_game": np.nan,
            }

        total_ip = hist["innings_pitched"].sum()
        total_bf = hist["batters_faced"].sum()
        return {
            f"{p}_n_games": n,
            f"{p}_k9": (hist["strikeouts"].sum() / total_ip * 9) if total_ip > 0 else np.nan,
            f"{p}_bb_pct": (hist["walks"].sum() / total_bf) if total_bf > 0 else np.nan,
            f"{p}_ip_per_game": hist["innings_pitched"].mean(),
        }

    def build_matchup_features(self, home_team_id, away_team_id, home_pitcher_id, away_pitcher_id, as_of_date, windows=None):
        windows = windows or self.windows
        row = {
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_days_rest": self.days_rest(home_team_id, as_of_date),
            "away_days_rest": self.days_rest(away_team_id, as_of_date),
        }
        for w in windows:
            row.update(self.team_window_features(home_team_id, as_of_date, w, "home"))
            row.update(self.team_window_features(away_team_id, as_of_date, w, "away"))
            row.update(self.starter_window_features(home_pitcher_id, as_of_date, w, "home_sp"))
            row.update(self.starter_window_features(away_pitcher_id, as_of_date, w, "away_sp"))
        return row


def build_win_training_dataset(matchups_df, team_stats_df, pitcher_stats_df, windows=(15, 30)):
    fe = WinFeatureEngineer(team_stats_df, pitcher_stats_df, windows=windows)

    completed = matchups_df[matchups_df["winner_team_id"].notna()].copy()
    completed["game_date"] = pd.to_datetime(completed["game_date"])
    completed = completed.sort_values("game_date").reset_index(drop=True)

    rows = []
    for _, g in completed.iterrows():
        feats = fe.build_matchup_features(
            home_team_id=g.home_team_id,
            away_team_id=g.away_team_id,
            home_pitcher_id=g.get("home_probable_pitcher_id"),
            away_pitcher_id=g.get("away_probable_pitcher_id"),
            as_of_date=g.game_date,
            windows=windows,
        )
        feats["target_home_win"] = int(g.winner_team_id == g.home_team_id)
        feats["game_pk"] = g.game_pk
        feats["game_date"] = g.game_date
        rows.append(feats)

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    min_window = min(windows)
    df = df[
        (df[f"home_L{min_window}_n_games"] > 0) &
        (df[f"away_L{min_window}_n_games"] > 0)
        ].reset_index(drop=True)
    return df