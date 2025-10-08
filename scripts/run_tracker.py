"""Command line entrypoint for the live meme trend tracker."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from trend_tracker import TrendTracker
from trend_tracker.config import load_config
from trend_tracker.data_sources.http_source import LocalJSONSource
from trend_tracker.storage import TrendStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the live meme trend tracker")
    parser.add_argument("--sample-data", action="store_true", help="Use bundled sample data instead of hitting live APIs")
    parser.add_argument("--limit", type=int, default=5, help="Number of items to display in the report")
    parser.add_argument("--state", type=Path, default=Path("tracker_state.json"), help="Path for persisted tracker state")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    config = load_config()
    store = TrendStore(str(args.state))
    if args.sample_data:
        tiktok = LocalJSONSource("tiktok", "sample_data/tiktok_sample.json")
        instagram = LocalJSONSource("instagram", "sample_data/instagram_sample.json")
        tracker = TrendTracker(config, tiktok_source=tiktok, instagram_source=instagram, storage=store)
    else:
        tracker = TrendTracker(config, storage=store)

    result = tracker.run_once()
    report = tracker.render_report(result, limit=args.limit)
    print(report)


if __name__ == "__main__":
    main()
