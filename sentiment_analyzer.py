"""
sentiment_analyzer.py
---------------------
Cleans tweet text and performs sentiment analysis using VADER (nltk).

VADER is purpose-built for social media: it handles slang, capitalisation,
punctuation, and emoji far better than general-purpose tools like TextBlob.
"""

import re
import logging
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import config

logger = logging.getLogger(__name__)

# Download VADER lexicon on first run (skipped if already present)
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    logger.info("Downloading VADER lexicon...")
    nltk.download("vader_lexicon", quiet=True)


class SentimentAnalyzer:
    """
    Cleans a list of raw tweet strings and scores each one for sentiment.

    Attributes:
        tweets:  Original raw tweet strings passed at construction time.
        results: List of dicts populated after calling analyze(). Each dict
                 contains: text, polarity, positive, negative, neutral, label.

    Example usage:
        analyzer = SentimentAnalyzer(raw_tweets)
        analyzer.analyze()
        print(analyzer.summary())
    """

    def __init__(self, tweets: list) -> None:
        self.tweets = tweets
        self.results = []
        self._sia = SentimentIntensityAnalyzer()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyze(self) -> None:
        """
        Clean every tweet and compute VADER sentiment scores.
        Populates self.results — call this before accessing any other method.
        """
        self.results = []
        for raw in self.tweets:
            cleaned = self._clean(raw)
            if not cleaned:
                continue
            scores = self._sia.polarity_scores(cleaned)
            label = self._label(scores["compound"])
            self.results.append(
                {
                    "text":     cleaned,
                    "polarity": scores["compound"],   # -1.0 to +1.0
                    "positive": scores["pos"],
                    "negative": scores["neg"],
                    "neutral":  scores["neu"],
                    "label":    label,
                }
            )
        logger.info("Analysed %d tweets.", len(self.results))

    def summary(self) -> dict:
        """
        Return counts and percentages for each sentiment label.

        Returns:
            dict with keys positive, negative, neutral (each having count/pct)
            and a top-level total key.
        """
        if not self.results:
            return {
                "positive": {"count": 0, "pct": 0.0},
                "negative": {"count": 0, "pct": 0.0},
                "neutral":  {"count": 0, "pct": 0.0},
                "total": 0,
            }

        total = len(self.results)
        counts = {"positive": 0, "negative": 0, "neutral": 0}
        for r in self.results:
            counts[r["label"].lower()] += 1

        result = {
            lbl: {"count": c, "pct": round(c / total * 100, 1)}
            for lbl, c in counts.items()
        }
        result["total"] = total
        return result

    def polarity_values(self) -> list:
        """Return a flat list of compound polarity scores (float)."""
        return [r["polarity"] for r in self.results]

    def combined_text(self) -> str:
        """Return all cleaned tweet text as a single string (for word cloud)."""
        return " ".join(r["text"] for r in self.results)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clean(tweet: str) -> str:
        """
        Remove URLs, @mentions, hashtag symbols, and non-alphanumeric chars.

        Args:
            tweet: Raw tweet string.

        Returns:
            Cleaned string with normalised whitespace.
        """
        tweet = re.sub(r"https?://\S+|www\.\S+", " ", tweet)   # URLs
        tweet = re.sub(r"@\w+", " ", tweet)                      # @mentions
        tweet = re.sub(r"#", "", tweet)                          # hashtag symbol
        tweet = re.sub(r"[^0-9A-Za-z\s!?.,']", " ", tweet)      # special chars
        return " ".join(tweet.split())                            # normalise whitespace

    @staticmethod
    def _label(compound: float) -> str:
        """Map a VADER compound score to a human-readable sentiment label."""
        if compound >= config.POSITIVE_THRESHOLD:
            return "Positive"
        if compound <= config.NEGATIVE_THRESHOLD:
            return "Negative"
        return "Neutral"
