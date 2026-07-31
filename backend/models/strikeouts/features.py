import numpy as np
import pandas as pd


class FeatureEngineer:
    def __init__(self, pitcher_stats_df, team_stats_df, windows=(15, 30)):
        self.windows = windows

        self.pitcher_stats = pitcher_stats_df.copy()
        if not self.pitcher_stats.empty:
            self.pitcher_stats["game_date"] = pd.to_datetime(self.pitcher_stats["game_date"])
            self.pitcher_stats = self.pitcher_stats.sort_values(["player_id", "game_date"]).reset_index(drop=True)

        self.team_stats = team_stats_df.copy()
        if not self.team_stats.empty:
            self.team_stats["game_date"] = pd.to_datetime(self.team_stats["game_date"])
            self.team_stats["team_k_pct"] = (self.team_stats["team_strikeouts"]/ self.team_stats["team_plate_appearances"].replace(0, np.nan))
            self.team_stats = self.team_stats.sort_values(
                ["team_id", "game_date"]
            ).reset_index(drop=True)

    def pitcher_window_features(self, player_id, as_of_date, window):
        prefix = f"L{window}"
        if self.pitcher_stats.empty:
            hist = pd.DataFrame()
        else:
            hist = self.pitcher_stats[
                (self.pitcher_stats.player_id == player_id) &
                (self.pitcher_stats.game_date < pd.Timestamp(as_of_date))
                ].tail(window)

        n = len(hist)
        if n == 0:
            return {
                f"{prefix}_n_games": 0,
                f"{prefix}_k_per_game": np.nan,
                f"{prefix}_k9": np.nan,
                f"{prefix}_k_pct": np.nan,
                f"{prefix}_bb_pct": np.nan,
                f"{prefix}_ip_per_game": np.nan,
                f"{prefix}_pitches_per_game": np.nan,
                f"{prefix}_strike_pct": np.nan,
                f"{prefix}_k_std": np.nan,
            }

        total_ip = hist["innings_pitched"].sum()
        total_bf = hist["batters_faced"].sum()
        total_pitches = hist["pitches_thrown"].sum()
        return {
            f"{prefix}_n_games": n,
            f"{prefix}_k_per_game": hist["strikeouts"].mean(),
            f"{prefix}_k9": (hist["strikeouts"].sum() / total_ip * 9) if total_ip > 0 else np.nan,
            f"{prefix}_k_pct": (hist["strikeouts"].sum() / total_bf) if total_bf > 0 else np.nan,
            f"{prefix}_bb_pct": (hist["walks"].sum() / total_bf) if total_bf > 0 else np.nan,
            f"{prefix}_ip_per_game": hist["innings_pitched"].mean(),
            f"{prefix}_pitches_per_game": hist["pitches_thrown"].mean(),
            f"{prefix}_strike_pct": (hist["strikes_thrown"].sum() / total_pitches)
            if total_pitches > 0 else np.nan,
            f"{prefix}_k_std": hist["strikeouts"].std() if n > 1 else 0.0,
        }

    def days_rest(self, player_id, as_of_date):
        if self.pitcher_stats.empty:
            return np.nan
        hist = self.pitcher_stats[(self.pitcher_stats.player_id == player_id) & (self.pitcher_stats.game_date < pd.Timestamp(as_of_date))]
        if hist.empty:
            return np.nan
        return (pd.Timestamp(as_of_date) - hist["game_date"].max()).days

    def opponent_window_features(self, opponent_team_id, as_of_date, window):
        prefix = f"opp_L{window}"
        if self.team_stats.empty:
            return {f"{prefix}_k_pct": np.nan}
        hist = self.team_stats[
            (self.team_stats.team_id == opponent_team_id) &
            (self.team_stats.game_date < pd.Timestamp(as_of_date))
            ].tail(window)
        if hist.empty:
            return {f"{prefix}_k_pct": np.nan}
        return {f"{prefix}_k_pct": hist["team_k_pct"].mean()}

    def build_feature_row(self, player_id, opponent_team_id, as_of_date, is_home, windows=None):
        windows = windows or self.windows
        row = {
            "player_id": player_id,
            "opponent_team_id": opponent_team_id,
            "is_home": int(is_home),
            "days_rest": self.days_rest(player_id, as_of_date),
        }
        for w in windows:
            row.update(self.pitcher_window_features(player_id, as_of_date, w))
            row.update(self.opponent_window_features(opponent_team_id, as_of_date, w))
        return row


def build_training_dataset(pitcher_stats_df, team_stats_df, windows=(15, 30)):
    fe = FeatureEngineer(pitcher_stats_df, team_stats_df, windows=windows)

    rows = []
    for _, game in fe.pitcher_stats.iterrows():
        feats = fe.build_feature_row(
            player_id=game.player_id,
            opponent_team_id=game.opponent_team_id,
            as_of_date=game.game_date,
            is_home=game.is_home,
            windows=windows,
        )
        feats["target_K"] = game.strikeouts
        feats["game_pk"] = game.game_pk
        feats["game_date"] = game.game_date
        rows.append(feats)

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    min_window = min(windows)
    df = df[df[f"L{min_window}_n_games"] > 0].reset_index(drop=True)
    return df