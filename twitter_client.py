"""
twitter_client.py
-----------------
Handles Twitter API v2 authentication and tweet fetching via Tweepy.
"""

import logging
import tweepy
import config

logger = logging.getLogger(__name__)


def create_client() -> tweepy.Client:
    """
    Authenticate with the Twitter API v2 using credentials from config.

    Returns:
        tweepy.Client: An authenticated Tweepy v2 client.

    Raises:
        ValueError: If required credentials are missing from the environment.
    """
    creds = {
        "TWITTER_BEARER_TOKEN": config.TWITTER_BEARER_TOKEN,
        "TWITTER_CONSUMER_KEY": config.TWITTER_CONSUMER_KEY,
        "TWITTER_CONSUMER_SECRET": config.TWITTER_CONSUMER_SECRET,
        "TWITTER_ACCESS_TOKEN": config.TWITTER_ACCESS_TOKEN,
        "TWITTER_ACCESS_TOKEN_SECRET": config.TWITTER_ACCESS_TOKEN_SECRET,
    }
    missing = [name for name, val in creds.items() if not val]
    if missing:
        raise ValueError(
            f"Missing Twitter API credentials: {', '.join(missing)}.\n"
            "Copy .env.example to .env and fill in your credentials."
        )

    return tweepy.Client(
        bearer_token=config.TWITTER_BEARER_TOKEN,
        consumer_key=config.TWITTER_CONSUMER_KEY,
        consumer_secret=config.TWITTER_CONSUMER_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )


def fetch_tweets(
    client: tweepy.Client,
    search_term: str,
    count: int,
    lang: str = "en",
    exclude_retweets: bool = True,
) -> list:
    """
    Fetch recent tweets matching search_term from the Twitter API v2.

    Automatically pages through results if count exceeds the per-request
    maximum (100 tweets) enforced by the Twitter API.

    Args:
        client:           Authenticated tweepy.Client instance.
        search_term:      Keyword or hashtag to search for.
        count:            Total number of tweets to retrieve.
        lang:             BCP-47 language code filter (default: "en").
        exclude_retweets: Strip retweets from results when True.

    Returns:
        List of raw tweet text strings. May be shorter than count if fewer
        matching tweets are available.
    """
    tweets = []

    # Build Twitter API v2 query string
    query = search_term
    if lang:
        query += f" lang:{lang}"
    if exclude_retweets:
        query += " -is:retweet"

    remaining = count
    next_token = None

    while remaining > 0:
        batch = min(remaining, config.MAX_TWEETS_PER_REQUEST)
        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=batch,
                next_token=next_token,
                tweet_fields=["text", "created_at", "lang"],
            )
        except tweepy.TweepyException as exc:
            logger.error("Twitter API error: %s", exc)
            break

        if not response.data:
            logger.info("No more tweets available for '%s'.", search_term)
            break

        tweets.extend(tweet.text for tweet in response.data)
        remaining -= len(response.data)

        meta = getattr(response, "meta", {}) or {}
        next_token = meta.get("next_token")
        if not next_token:
            break

    if not tweets:
        logger.warning("No tweets retrieved for search term '%s'.", search_term)

    return tweets
