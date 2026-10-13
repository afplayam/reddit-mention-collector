# reddit-mention-collector
A personal, non-commercial Python tool that reads public posts through Reddit's authenticated Data API and stores locally extracted ticker mentions in DuckDB for personal research.

It extracts simple uppercase ticker mentions from post titles and self-text,
then stores the posts and ticker mentions locally in DuckDB for personal
market research.

## Scope

- Read-only access to public posts
- No posting, commenting, voting, or messaging
- No redistribution or publication of Reddit content
- No commercial use
- No AI training use
- Data is stored locally in DuckDB

## Files

- `collect_reddit.py`: authenticated collector using PRAW
- `test_reddit.py`: minimal authentication/listing test
- `.env.example`: required environment variables

## API usage

The application uses OAuth credentials supplied through environment
variables and accesses only public subreddit listings.
