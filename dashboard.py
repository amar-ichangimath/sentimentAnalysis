"""
dashboard.py - Dash 2.0 application layout and callbacks.
"""

import base64
import logging
from dash import Dash, dcc, html
import plotly.graph_objs as go

import config
from visualizer import build_pie_data, build_line_data

logger = logging.getLogger(__name__)


def create_app(polarity_values: list, summary: dict, wordcloud_path: str) -> Dash:
    """
    Instantiate and configure the Dash 2.0 application.

    Args:
        polarity_values: List of VADER compound scores from SentimentAnalyzer.
        summary:         Dict returned by SentimentAnalyzer.summary().
        wordcloud_path:  Filepath to the word cloud PNG image.

    Returns:
        A configured Dash app instance. Call app.run() to start the server.
    """
    app = Dash(__name__, title=config.DASHBOARD_TITLE)

    pie_labels, pie_values = build_pie_data(summary)
    line_trace = build_line_data(polarity_values)
    wordcloud_src = _encode_image(wordcloud_path)

    total   = summary.get("total", 0)
    pos_pct = summary.get("positive", {}).get("pct", 0)
    neg_pct = summary.get("negative", {}).get("pct", 0)
    neu_pct = summary.get("neutral",  {}).get("pct", 0)

    app.layout = html.Div(
        style={"fontFamily": "Arial, sans-serif", "maxWidth": "1100px",
               "margin": "0 auto", "padding": "20px"},
        children=[
            html.H1(
                config.DASHBOARD_TITLE,
                style={"textAlign": "center", "color": "#2c3e50"},
            ),

            # KPI summary cards
            html.Div(
                style={"display": "flex", "gap": "16px", "marginBottom": "24px"},
                children=[
                    _kpi_card("Total Tweets", total,          "#3498db"),
                    _kpi_card("Positive",     f"{pos_pct}%",  "#2ecc71"),
                    _kpi_card("Negative",     f"{neg_pct}%",  "#e74c3c"),
                    _kpi_card("Neutral",      f"{neu_pct}%",  "#95a5a6"),
                ],
            ),

            # Polarity trend line chart
            dcc.Graph(
                id="polarity-line",
                figure={
                    "data": [go.Scatter(**line_trace)],
                    "layout": go.Layout(
                        title="Polarity Score per Tweet",
                        xaxis={"title": "Tweet #"},
                        yaxis={"title": "Compound Score", "range": [-1, 1]},
                        hovermode="x unified",
                        plot_bgcolor="#f9f9f9",
                    ),
                },
            ),

            # Sentiment distribution donut chart
            dcc.Graph(
                id="sentiment-pie",
                figure={
                    "data": [
                        go.Pie(
                            labels=pie_labels,
                            values=pie_values,
                            hole=0.35,
                            marker_colors=["#2ecc71", "#e74c3c", "#95a5a6"],
                        )
                    ],
                    "layout": go.Layout(title="Sentiment Distribution"),
                },
            ),

            # Word cloud image
            html.H2("Word Cloud", style={"textAlign": "center", "color": "#2c3e50"}),
            html.Img(
                src=wordcloud_src,
                style={
                    "width": "100%",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                },
            ),
        ],
    )

    return app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kpi_card(label: str, value, color: str) -> html.Div:
    """Return a styled KPI summary card component."""
    return html.Div(
        style={
            "flex": "1", "background": color, "color": "white",
            "borderRadius": "8px", "padding": "16px", "textAlign": "center",
        },
        children=[
            html.P(label, style={"margin": "0 0 4px", "fontSize": "14px"}),
            html.H2(str(value), style={"margin": "0"}),
        ],
    )


def _encode_image(image_path: str) -> str:
    """Base64-encode an image file for embedding in an HTML img src tag."""
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        logger.warning("Word cloud image not found at '%s'.", image_path)
        return ""
