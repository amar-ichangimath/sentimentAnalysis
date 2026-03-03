"""
visualizer.py
-------------
Generates the word cloud image and provides chart data helpers
consumed by the Dash dashboard.
"""

import os
import logging
import matplotlib
matplotlib.use("Agg")   # non-interactive backend (safe for servers)
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

import config

logger = logging.getLogger(__name__)


def generate_wordcloud(text: str, output_path: str = config.WORDCLOUD_OUTPUT_PATH) -> str:
    """
    Build a word cloud from *text* and save it as a PNG file.

    Args:
        text:        Space-separated words (e.g. combined tweet text).
        output_path: Destination file path for the PNG image.

    Returns:
        The resolved output_path on success.

    Raises:
        ValueError: If text is empty or whitespace-only.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate word cloud from empty text.")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    wc = WordCloud(
        width=config.WORDCLOUD_WIDTH,
        height=config.WORDCLOUD_HEIGHT,
        max_font_size=config.WORDCLOUD_MAX_FONT,
        stopwords=STOPWORDS,
        background_color="white",
        colormap="viridis",
    ).generate(text)

    plt.figure(figsize=(16, 8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info("Word cloud saved to '%s'.", output_path)
    return output_path


def build_pie_data(summary: dict) -> tuple:
    """
    Convert a SentimentAnalyzer.summary() dict into Plotly pie chart inputs.

    Args:
        summary: Dict returned by SentimentAnalyzer.summary().

    Returns:
        (labels, values) tuple of lists ready for go.Pie().
    """
    labels = ["Positive", "Negative", "Neutral"]
    values = [
        summary.get("positive", {}).get("count", 0),
        summary.get("negative", {}).get("count", 0),
        summary.get("neutral",  {}).get("count", 0),
    ]
    return labels, values


def build_line_data(polarity_values: list) -> dict:
    """
    Build Plotly scatter trace data for the polarity trend line.

    Args:
        polarity_values: List of VADER compound scores in tweet order.

    Returns:
        Dict suitable for use as a Plotly trace.
    """
    return {
        "x": list(range(1, len(polarity_values) + 1)),
        "y": polarity_values,
        "mode": "lines+markers",
        "name": "Polarity",
        "line": {"color": "#636EFA"},
        "marker": {"size": 4},
    }
