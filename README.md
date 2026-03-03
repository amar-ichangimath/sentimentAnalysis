# Twitter Sentiment Analysis Dashboard

Fetches tweets via Twitter API v2, scores sentiment with VADER, and shows results on a Dash 2.0 dashboard.

## Features
- Twitter API v2 via Tweepy 4+ (replaces deprecated v1.1)
- VADER sentiment scoring (purpose-built for social media)
- Dash 2.0 dashboard with polarity trend line and pie chart
- Automatic pagination for large tweet counts
- Configurable entirely via config.py
- CLI flags for non-interactive use

## Project Structure

sentiment-dashboard/
|-- .env.example          # Credential template, copy to .env
|-- .gitignore
|-- requirements.txt
|-- config.py             # All tuneable settings
|-- twitter_client.py     # API auth and tweet fetching
|-- sentiment_analyzer.py # Text cleaning and VADER scoring
|-- visualizer.py         # Word cloud and chart data helpers
|-- dashboard.py          # Dash 2.0 app layout
|-- main.py               # Entry point
|-- outputs/              # Generated images (gitignored)

## Setup

1. Clone and enter the repo
2. Create a virtualenv: python3 -m venv venv && source venv/bin/activate
3. Install: pip install -r requirements.txt
4. Copy .env.example to .env and fill in your Twitter API keys

## Usage

Interactive:  python main.py
CLI:          python main.py --term "OpenAI" --count 200

Dashboard launches at http://127.0.0.1:8050

## Configuration

All settings are in config.py. Key options:
- DEFAULT_SEARCH_TERM  (default: Python)
- DEFAULT_TWEET_COUNT  (default: 100)
- POSITIVE_THRESHOLD   (default: 0.05)
- NEGATIVE_THRESHOLD   (default: -0.05)
- DASHBOARD_PORT       (default: 8050)

## Extending

- More charts: add dcc.Graph to dashboard.py using analyzer.results
- Better accuracy: swap VADER for a HuggingFace Transformer in sentiment_analyzer.py
- Export: add pd.DataFrame(analyzer.results).to_csv(results.csv) in main.py
- Schedule: wrap main() with APScheduler
