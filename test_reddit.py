import os
import praw
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

print("Read-only:", reddit.read_only)

for post in reddit.subreddit("wallstreetbets").new(limit=3):
    print(post.id, post.title[:80])
