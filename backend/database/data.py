import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("DATABASE_URL")
key = os.getenv("DATABASE_KEY")
supabase = create_client(url, key)

PAGE_SIZE = 1000


def get_table_as_df(table_name, select="*", filters=None):
    """
    retrieves the entire table into a dataframe
    """
    all_rows = []
    start = 0
    while True:
        query = supabase.table(table_name).select(select)
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        resp = query.range(start, start + PAGE_SIZE - 1).execute()
        rows = resp.data
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        start += PAGE_SIZE
    return pd.DataFrame(all_rows)


def get_matchups_between(start_date, end_date):
    """start_date/end_date as 'YYYY-MM-DD'."""
    all_rows = []
    start = 0
    while True:
        resp = (
            supabase.table("daily_matchups")
            .select("*")
            .gte("game_date", start_date)
            .lte("game_date", end_date)
            .range(start, start + PAGE_SIZE - 1)
            .execute()
        )
        rows = resp.data
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        start += PAGE_SIZE
    return pd.DataFrame(all_rows)


def upsert_rows(table_name, rows, batch_size=200, on_conflict=None):
    """
    I've noticed that supabase is super slow, so I looked up ways to speed it up
    """
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        if batch:
            supabase.table(table_name).upsert(batch, on_conflict=on_conflict).execute()