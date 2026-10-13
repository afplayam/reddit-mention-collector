import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import praw
from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(os.getenv("DUCKDB_PATH", "data/wsb.duckdb"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

TICKER_PATTERN = re.compile(r"\b([A-Z]{1,5})\b")

# Avoid treating common WSB words as tickers
BLACKLIST = {
    "DD", "YOLO", "WSB", "APE", "MOON", "ROPE", "TENDIE", "TENDIES",
    "ETF", "IPO", "CEO", "CFO", "SEC", "FOMO", "ATH", "ATL", "EPS",
    "GDP", "FED", "USA", "US", "UK", "IT", "AI", "OTC", "PDT",
}


def init_db(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS reddit_posts (
            post_id VARCHAR PRIMARY KEY,
            subreddit VARCHAR,
            title VARCHAR,
            selftext VARCHAR,
            author VARCHAR,
            created_utc TIMESTAMP,
            score BIGINT,
            num_comments BIGINT,
            url VARCHAR,
            collected_at TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS ticker_mentions (
            post_id VARCHAR,
            ticker VARCHAR,
            source VARCHAR,
            created_utc TIMESTAMP,
            collected_at TIMESTAMP,
            PRIMARY KEY (post_id, ticker, source)
        )
    """)


def extract_tickers(text):
    if not text:
        return set()

    candidates = TICKER_PATTERN.findall(text.upper())
    return {
        ticker for ticker in candidates
        if ticker not in BLACKLIST and 1 <= len(ticker) <= 5
    }


def store_post(con, submission):
    created_utc = datetime.fromtimestamp(
        submission.created_utc,
        tz=timezone.utc,
    ).replace(tzinfo=None)

    con.execute("""
        INSERT OR IGNORE INTO reddit_posts
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        submission.id,
        submission.subreddit.display_name,
        submission.title,
        submission.selftext or "",
        str(submission.author) if submission.author else "[deleted]",
        created_utc,
        submission.score,
        submission.num_comments,
        submission.url,
        datetime.utcnow(),
    ])

    text = f"{submission.title} {submission.selftext or ''}"
    tickers = extract_tickers(text)

    for ticker in tickers:
        con.execute("""
            INSERT OR IGNORE INTO ticker_mentions
            VALUES (?, ?, ?, ?, ?)
        """, [
            submission.id,
            ticker,
            "post",
            created_utc,
            datetime.utcnow(),
        ])


def main():
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    con = duckdb.connect(str(DB_PATH))
    init_db(con)

    subreddit = reddit.subreddit("wallstreetbets")

    for submission in subreddit.new(limit=100):
        store_post(con, submission)
        time.sleep(0.7)

    print(f"Stored posts in {DB_PATH}")


if __name__ == "__main__":
    main()
