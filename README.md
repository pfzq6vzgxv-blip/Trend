# Trend

A lightweight live tracker that analyses meme performance on TikTok and Instagram Reels and projects how each meme is likely to trend over the next few hours. It can work with real API endpoints when credentials are provided or operate completely offline with bundled sample data.

## Features

- Normalizes TikTok and Instagram Reels data into a unified schema
- Calculates engagement rate, velocity, acceleration, and a composite virality score
- Uses linear regression on historical view counts to forecast near-term growth
- Persists history between runs to enable meaningful delta calculations
- Ships with sample datasets so you can try the tracker without API keys

## Quick start (sample data)

```bash
python scripts/run_tracker.py --sample-data --limit 5 --verbose
```

The command prints a report similar to:

```
Live Meme Trend Tracker
======================
Generated at: 2024-05-11T12:15:12.345678Z

Top 5 Memes by Virality Score:

[tiktok] Cat vibing to eurodance
  Creator: catastic | Views: 1,450,000 | Engagement: 14.41%
  Velocity: 130,000 views/hr | Accel: 30,000
  Virality Score: 16.12 | Projected Views (+6h): 1,860,000
  URL: https://www.tiktok.com/@catastic/video/123
```

A JSON file (default `tracker_state.json`) is created to store view history between runs.

## Using live APIs

1. Export the required tokens/URLs for whichever data provider you prefer. Examples:

   ```bash
   export TIKTOK_DATASET_URL="https://api.apify.com/v2/datasets/your_dataset/items?clean=true"
   export INSTAGRAM_API_URL="https://instagram28.p.rapidapi.com/instagram/reels/trending/"
   export INSTAGRAM_RAPIDAPI_KEY="<rapidapi-key>"
   ```

2. Run the tracker without `--sample-data`:

   ```bash
   python scripts/run_tracker.py --limit 10
   ```

The tracker automatically merges the latest snapshot with the stored history and recomputes metrics.

## Project structure

- `trend_tracker/` – core package with data models, analytics, forecasting, and orchestration logic
- `sample_data/` – ready-to-use JSON payloads that mimic real API responses
- `scripts/run_tracker.py` – convenience CLI for running the tracker manually or via cron

## Extending the tracker

- Add new data sources by implementing `TrendDataSource`
- Customize metric calculations in `trend_tracker/analyzer.py`
- Swap out the forecasting approach in `trend_tracker/forecaster.py`

## Requirements

The tracker only depends on `requests` from PyPI. Install with:

```bash
pip install -r requirements.txt
```

or manually:

```bash
pip install requests
```

## License

MIT
