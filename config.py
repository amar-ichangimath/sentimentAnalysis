"""
config.py
---------
Centralised configuration for the sentiment dashboard.
All tuneable parameters live here — edit this file rather than the source modules.
"""

import os
from dotenv import load_dotenv

# Load variables from .env (ignored if not present, e.g. in CI/CD)
load_dotenv()

# ---------------------------------------------------------------------------
# Twitter API v2 credentials  (populated from .env — never hardcode here)
# ---------------------------------------------------------------------------
TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
TWITTER_CONSUMER_KEY: str = os.getenv("TWITTER_CONSUMER_KEY", "")
TWITTER_CONSUMER_SECRET: str = os.getenv("TWITTER_CONSUMER_SECRET", "")
TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# ---------------------------------------------------------------------------
# Search defaults
# ---------------------------------------------------------------------------
DEFAULT_SEARCH_TERM: str = "Python"
DEFAULT_TWEET_COUNT: int = 100
MAX_TWEETS_PER_REQUEST: int = 100   # Twitter API v2 hard limit per call

# ---------------------------------------------------------------------------
# Sentiment thresholds (VADER compound score range: -1.0 to +1.0)
# ---------------------------------------------------------------------------
POSITIVE_THRESHOLD: float = 0.05    # compound score above this -> positive
NEGATIVE_THRESHOLD: float = -0.05   # compound score below this -> negative

# ---------------------------------------------------------------------------
# Word cloud settings
# ---------------------------------------------------------------------------
WORDCLOUD_WIDTH: int = 1600
WORDCLOUD_HEIGHT: int = 800
WORDCLOUD_MAX_FONT: int = 200
WORDCLOUD_OUTPUT_DIR: str = "outputs"
WORDCLOUD_OUTPUT_PATH: str = "outputs/wordcloud.png"

# ---------------------------------------------------------------------------
# Dashboard settings
# ---------------------------------------------------------------------------
DASHBOARD_HOST: str = "127.0.0.1"
DASHBOARD_PORT: int = 8050
DASHBOARD_DEBUG: bool = False
DASHBOARD_TITLE: str = "Twitter Sentiment Dashboard"
