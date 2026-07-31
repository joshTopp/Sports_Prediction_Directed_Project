import datetime
import traceback
from add_prior_seasons import backfill_season
from backend.models.strikeouts.predict import predict_for_date as predict_k_for_date
from backend.models.win.predict import predict_for_date as predict_win_for_date
from add_players import seed_active_mlb_players


def run():
    # get the next 3 days dates
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")
    today = datetime.date.today()
    future_date = (today + datetime.timedelta(days=2)).strftime("%m/%d/%Y")
    # update mlb player roster just in case
    seed_active_mlb_players()
    # retrieve the past game outcomes and future probable pitchers etc
    try:
        backfill_season(yesterday, future_date)
    except Exception:
        traceback.print_exc()
        raise

    # predict games
    for offset in range(3):
        target_date = (today + datetime.timedelta(days=offset)).strftime("%m/%d/%Y")
        try:
            predict_k_for_date(target_date)
        except Exception:
            traceback.print_exc()
        try:
            predict_win_for_date(target_date)
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    run()