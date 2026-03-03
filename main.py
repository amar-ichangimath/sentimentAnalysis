"""
main.py
-------
Entry point for the Twitter Sentiment Analysis Dashboard.

Usage:
    python main.py
    python main.py --term "OpenAI" --count 200
"""

import argparse
import logging
import os
import sys

import config
from twitter_client import create_client, fetch_tweets
from sentiment_analyzer import SentimentAnalyzer
from visualizer import generate_wordcloud
from dashboard import create_app

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Twitter Sentiment Analysis Dashboard"
    )
    parser.add_argument(
        "--term",
        type=str,
        default=None,
        help="Search term or hashtag (overrides interactive prompt)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of tweets to fetch (overrides interactive prompt)",
    )
    parser.add_argument(
        "--no-wordcloud",
        action="store_true",
        help="Skip word cloud generation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # --- Prompt for inputs if not supplied via CLI ---
    search_term = args.term or input(
        f"Enter keyword/hashtag to search "
        f"[default: {config.DEFAULT_SEARCH_TERM}]: "
    ).strip() or config.DEFAULT_SEARCH_TERM

    tweet_count = args.count
    if tweet_count is None:
        raw = input(
            f"Number of tweets to fetch [default: {config.DEFAULT_TWEET_COUNT}]: "
        ).strip()
        tweet_count = int(raw) if raw.isdigit() else config.DEFAULT_TWEET_COUNT

    # --- Authenticate & fetch tweets ---
    logger.info("Authenticating with Twitter API v2...")
    try:
        client = create_client()
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)

    logger.info("Fetching up to %d tweets for '%s'...", tweet_count, search_term)
    raw_tweets = fetch_tweets(client, search_term, tweet_count)

    if not raw_tweets:
        logger.error("No tweets retrieved. Exiting.")
        sys.exit(1)

    logger.info("Retrieved %d tweets.", len(raw_tweets))

    # --- Sentiment analysis ---
    logger.info("Running sentiment analysis...")
    analyzer = SentimentAnalyzer(raw_tweets)
    analyzer.analyze()

    summary = analyzer.summary()
    logger.info(
        "Results — Positive: %(positive)s | Negative: %(negative)s | Neutral: %(neutral)s",
        {k: f"{v['count']} ({v['pct']}%)" for k, v in summary.items() if k != "total"},
    )

    # --- Word cloud ---
    wordcloud_path = config.WORDCLOUD_OUTPUT_PATH
    if not args.no_wordcloud:
        try:
            os.makedirs(config.WORDCLOUD_OUTPUT_DIR, exist_ok=True)
            generate_wordcloud(analyzer.combined_text(), wordcloud_path)
        except ValueError as exc:
            logger.warning("Word cloud skipped: %s", exc)
            wordcloud_path = ""

    # --- Launch dashboard ---
    logger.info(
        "Starting dashboard at http://%s:%d",
        config.DASHBOARD_HOST,
        config.DASHBOARD_PORT,
    )
    app = create_app(
        polarity_values=analyzer.polarity_values(),
        summary=summary,
        wordcloud_path=wordcloud_path,
    )
    app.run(
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        debug=config.DASHBOARD_DEBUG,
    )


if __name__ == "__main__":
    main()
