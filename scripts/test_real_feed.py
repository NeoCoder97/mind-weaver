#!/usr/bin/env python
"""Quick test script for real RSS feed testing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spider_aggregation.core import create_fetcher, create_parser
from spider_aggregation.models import FeedModel
from rich.console import Console

console = Console()

def test_cloudflare_rss():
    """Test Cloudflare RSS feed."""
    rss_url = "https://blog.cloudflare.com/zh-cn/rss"

    console.print(f"\n🔍 Testing: Cloudflare Blog RSS\n")
    console.print(f"📡 URL: {rss_url}\n")

    # Fetch
    console.print("📡 Fetching...")
    fetcher = create_fetcher()

    # Create mock feed
    feed = FeedModel(
        id=1,
        url=rss_url,
        name="Cloudflare Blog",
        enabled=True,
        fetch_interval_minutes=60,
    )

    result = fetcher.fetch_feed(feed)

    if not result.success:
        console.print(f"❌ Fetch failed: {result.error}")
        return

    console.print(f"✅ Fetched {result.entries_count} entries")
    console.print(f"⏱️  Time: {result.fetch_time_seconds:.2f}s\n")

    # Parse some entries
    parser = create_parser()

    console.print("📖 Parsing first 5 entries:\n")
    for i, entry in enumerate(result.entries[:5], 1):
        parsed = parser.parse_entry(entry)
        title = parsed.get("title", "No title")[:60]
        console.print(f"{i}. {title}")
        console.print(f"   Language: {parsed.get('language', 'N/A')}")
        console.print(f"   Link: {parsed.get('link', 'N/A')}")
        console.print()

    console.print("✅ Test completed!")


if __name__ == "__main__":
    try:
        test_cloudflare_rss()
    except KeyboardInterrupt:
        console.print("\n⚠️  Test interrupted by user")
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
