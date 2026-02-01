"""Command-line interface for spider-aggregation."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from spider_aggregation.config import get_config
from spider_aggregation.core import (
    ContentParser,
    Deduplicator,
    FeedFetcher,
    FeedScheduler,
    create_deduplicator,
    create_fetcher,
    create_parser,
    create_scheduler,
)
from spider_aggregation.logger import get_logger
from spider_aggregation.storage.database import DatabaseManager
from spider_aggregation.storage.repositories.entry_repo import EntryRepository
from spider_aggregation.storage.repositories.feed_repo import FeedRepository
from spider_aggregation.models.feed import FeedCreate

logger = get_logger(__name__)
console = Console()

# Default database path
DEFAULT_DB_PATH = "data/spider_aggregation.db"


@click.group()
@click.version_option(version="0.1.0")
@click.option(
    "--db-path",
    default=DEFAULT_DB_PATH,
    help="Path to the database file",
    envvar="SPIDER_DB_PATH",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, db_path: str, verbose: bool):
    """Spider Aggregation - Personal knowledge/research dynamic monitoring tool."""
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db_path
    ctx.obj["verbose"] = verbose

    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


@cli.command()
@click.pass_context
def init(ctx: click.Context):
    """Initialize the database."""
    db_path = ctx.obj["db_path"]

    console.print("[bold cyan]Initializing Spider Aggregation database...[/bold cyan]")

    # Check if database already exists
    db_file = Path(db_path)
    if db_file.exists():
        if not click.confirm(f"Database already exists at {db_path}. Reinitialize?"):
            console.print("[yellow]Initialization cancelled.[/yellow]")
            return

    # Create database manager and initialize
    manager = DatabaseManager(db_path)
    manager.init_db()

    console.print(f"[green]✅ Database initialized at: {db_path}[/green]")


@cli.command()
@click.argument("url")
@click.option("--name", "-n", help="Feed name (default: auto-detected)")
@click.option("--description", "-d", help="Feed description")
@click.option("--enabled/--disabled", default=True, help="Enable/disable feed (default: enabled)")
@click.option("--interval", "-i", type=int, help="Fetch interval in minutes")
@click.pass_context
def add_feed(
    ctx: click.Context,
    url: str,
    name: Optional[str],
    description: Optional[str],
    enabled: bool,
    interval: Optional[int],
):
    """Add a new RSS/Atom feed."""
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    console.print(f"[bold cyan]Adding feed: {url}[/bold cyan]\n")

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        feed_repo = FeedRepository(session)

        # Check if feed already exists
        existing = feed_repo.get_by_url(url)
        if existing:
            console.print(f"[yellow]⚠️  Feed already exists with ID: {existing.id}[/yellow]")
            return

        # Fetch feed to get metadata
        console.print("📡 Fetching feed metadata...")
        fetcher = create_fetcher()

        # Create temporary feed for fetching
        from spider_aggregation.models.feed import FeedModel

        temp_feed = FeedModel(
            id=0,
            url=url,
            name=name or "Unknown",
            enabled=enabled,
            fetch_interval_minutes=interval or 60,
        )

        try:
            result = fetcher.fetch_feed(temp_feed)

            if not result.success:
                console.print(f"[red]❌ Failed to fetch feed: {result.error}[/red]")
                return

            # Use fetched metadata if not provided
            if not name and result.feed_info:
                name = result.feed_info.get("title") or "Untitled Feed"
                if not description:
                    description = result.feed_info.get("description")

            if name:
                console.print(f"   ✅ Feed title: [cyan]{name}[/cyan]")

        except Exception as e:
            console.print(f"[yellow]⚠️  Could not fetch metadata: {e}[/yellow]")
            if not name:
                name = click.prompt("Enter feed name", type=str)

        # Create feed
        feed_data = FeedCreate(
            url=url,
            name=name,
            description=description,
            enabled=enabled,
            fetch_interval_minutes=interval or 60,
        )

        feed = feed_repo.create(feed_data)

        console.print(f"\n[green]✅ Feed added with ID: {feed.id}[/green]")
        console.print(f"   Name: {feed.name}")
        console.print(f"   URL: {feed.url}")
        console.print(f"   Enabled: {feed.enabled}")
        console.print(f"   Interval: {feed.fetch_interval_minutes} minutes")


@cli.command("list-feeds")
@click.option("--enabled-only/--all", default=False, help="Show only enabled feeds")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.pass_context
def list_feeds(ctx: click.Context, enabled_only: bool, verbose: bool):
    """List all feeds."""
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        feed_repo = FeedRepository(session)
        feeds = feed_repo.list(enabled_only=enabled_only)

        if not feeds:
            console.print("[yellow]No feeds found.[/yellow]")
            return

        # Create table
        table = Table(title="Feeds", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Name", style="green")
        table.add_column("URL", style="blue")
        table.add_column("Enabled", justify="center", width=8)
        table.add_column("Interval", justify="right", width=8)

        if verbose:
            table.add_column("Last Fetched", width=16)
            table.add_column("Entry Count", justify="right", width=10)

        for feed in feeds:
            row = [
                str(feed.id),
                feed.name[:30] + "..." if len(feed.name) > 30 else feed.name,
                feed.url[:40] + "..." if len(feed.url) > 40 else feed.url,
                "✓" if feed.enabled else "✗",
                f"{feed.fetch_interval_minutes}m",
            ]

            if verbose:
                entry_repo = EntryRepository(session)
                entry_count = entry_repo.count(feed_id=feed.id)
                last_fetched = (
                    feed.last_fetched_at.strftime("%Y-%m-%d %H:%M")
                    if feed.last_fetched_at
                    else "Never"
                )
                row.extend([last_fetched, str(entry_count)])

            table.add_row(*row)

        console.print(table)
        console.print(f"\nTotal: {len(feeds)} feed(s)")


@cli.command()
@click.argument("feed_id", required=False, type=int)
@click.option("--all", "-a", "all_feeds", is_flag=True, help="Fetch all enabled feeds")
@click.option("--force", "-f", is_flag=True, help="Force fetch even if not due")
@click.pass_context
def fetch(ctx: click.Context, feed_id: Optional[int], all_feeds: bool, force: bool):
    """Manually trigger feed fetch.

    If neither FEED_ID nor --all is specified, fetches all due feeds.
    """
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    if feed_id and all_feeds:
        console.print("[red]❌ Cannot specify both FEED_ID and --all[/red]")
        sys.exit(1)

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        feed_repo = FeedRepository(session)
        entry_repo = EntryRepository(session)

        # Determine which feeds to fetch
        feeds_to_fetch = []

        if feed_id:
            feed = feed_repo.get(feed_id)
            if not feed:
                console.print(f"[red]❌ Feed with ID {feed_id} not found[/red]")
                sys.exit(1)
            feeds_to_fetch = [feed]
        elif all_feeds:
            feeds_to_fetch = [f for f in feed_repo.list() if f.enabled]
        else:
            # Fetch due feeds
            feeds_to_fetch = feed_repo.get_feeds_to_fetch()

        if not feeds_to_fetch:
            console.print("[yellow]No feeds to fetch.[/yellow]")
            return

        console.print(f"[bold cyan]Fetching {len(feeds_to_fetch)} feed(s)...[/bold cyan]\n")

        # Create fetcher, parser, and deduplicator
        fetcher = create_fetcher(session=session)
        parser = create_parser()
        dedup = create_deduplicator(session=session, strategy="medium")

        total_entries = 0
        total_created = 0
        total_skipped = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching feeds...", total=len(feeds_to_fetch))

            for feed in feeds_to_fetch:
                progress.update(task, description=f"Fetching {feed.name}...")

                # Fetch feed
                result = fetcher.fetch_feed(feed)

                if not result.success:
                    console.print(f"\n[red]❌ {feed.name}: {result.error}[/red]")
                    progress.advance(task)
                    continue

                # Parse and store entries
                created = 0
                skipped = 0

                for raw_entry in result.entries:
                    parsed = parser.parse_entry(raw_entry)

                    # Check duplicates
                    dup_result = dedup.check_duplicate(parsed, feed_id=feed.id)
                    if dup_result.is_duplicate:
                        skipped += 1
                        continue

                    # Compute hashes
                    hashes = dedup.compute_hashes(parsed)

                    # Create entry
                    from spider_aggregation.models.entry import EntryCreate

                    entry_data = EntryCreate(
                        feed_id=feed.id,
                        title=parsed["title"] or "",
                        link=parsed["link"] or "",
                        author=parsed.get("author"),
                        summary=parsed.get("summary"),
                        content=parsed.get("content"),
                        published_at=parsed.get("published_at"),
                        title_hash=hashes["title_hash"],
                        link_hash=hashes["link_hash"],
                        content_hash=hashes["content_hash"],
                        tags=parsed.get("tags"),
                        language=parsed.get("language"),
                        reading_time_seconds=parsed.get("reading_time_seconds"),
                    )

                    entry_repo.create(entry_data)
                    created += 1

                total_entries += result.entries_count
                total_created += created
                total_skipped += skipped

                console.print(
                    f"\n✅ {feed.name}: {created} new, {skipped} skipped ({result.entries_count} total)"
                )
                progress.advance(task)

        console.print(f"\n[bold green]✅ Fetch complete![/bold green]")
        console.print(f"   Total entries: {total_entries}")
        console.print(f"   New entries: {total_created}")
        console.print(f"   Skipped (duplicates): {total_skipped}")


@cli.command()
@click.option("--workers", "-w", type=int, default=3, help="Number of worker threads")
@click.pass_context
def start(ctx: click.Context, workers: int):
    """Start the scheduler for automatic feed fetching."""
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    console.print("[bold cyan]Starting Spider Aggregation scheduler...[/bold cyan]\n")

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        feed_repo = FeedRepository(session)
        feeds = [f for f in feed_repo.list() if f.enabled]

        if not feeds:
            console.print("[yellow]No enabled feeds found.[/yellow]")
            console.print("Add feeds with: spider-aggregation add-feed <url>")
            return

        console.print(f"Found {len(feeds)} enabled feed(s):\n")
        for feed in feeds:
            console.print(f"  • {feed.name} (every {feed.fetch_interval_minutes}m)")

    console.print("\n[yellow]Press Ctrl+C to stop the scheduler[/yellow]\n")

    # Create scheduler with db_manager for jobs to create sessions
    scheduler = create_scheduler(session=None, max_workers=workers, db_manager=manager)

    try:
        scheduler.start()

        # Add jobs for all enabled feeds
        with manager.session() as session:
            feed_repo = FeedRepository(session)
            feeds = [f for f in feed_repo.list() if f.enabled]

            for feed in feeds:
                job_id = scheduler.add_feed_job(
                    feed_id=feed.id,
                    interval_minutes=feed.fetch_interval_minutes,
                )
                console.print(f"✅ Scheduled {feed.name} ({job_id})")

        console.print("\n[bold green]Scheduler is running![/bold green]")
        console.print("[dim]Fetching will occur automatically based on feed intervals.[/dim]\n")

        # Keep running until interrupted
        import time

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Stopping scheduler...[/yellow]")
        scheduler.stop(wait=True)
        console.print("[green]✅ Scheduler stopped.[/green]")


@cli.command("list-entries")
@click.option("--feed-id", "-f", type=int, help="Filter by feed ID")
@click.option("--limit", "-l", type=int, default=20, help="Number of entries to show")
@click.option("--offset", type=int, default=0, help="Offset for pagination")
@click.option("--language", help="Filter by language code (e.g., en, zh)")
@click.option("--search", "-s", help="Search in title and content")
@click.pass_context
def list_entries(
    ctx: click.Context,
    feed_id: Optional[int],
    limit: int,
    offset: int,
    language: Optional[str],
    search: Optional[str],
):
    """List entries from the database."""
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        entry_repo = EntryRepository(session)

        # Get entries
        entries = entry_repo.list(
            feed_id=feed_id,
            limit=limit,
            offset=offset,
        )

        if not entries:
            console.print("[yellow]No entries found.[/yellow]")
            return

        # Apply filters
        if language:
            entries = [e for e in entries if e.language == language]

        if search:
            search_lower = search.lower()
            entries = [
                e
                for e in entries
                if search_lower in (e.title or "").lower()
                or search_lower in (e.content or "").lower()
                or search_lower in (e.summary or "").lower()
            ]

        if not entries:
            console.print("[yellow]No entries match the filters.[/yellow]")
            return

        # Create table
        table = Table(title="Entries", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Title", style="green")
        table.add_column("Feed ID", style="blue", width=8)
        table.add_column("Lang", width=5)
        table.add_column("Reading Time", width=12)
        table.add_column("Published", width=16)

        for entry in entries:
            title = entry.title[:50] + "..." if len(entry.title) > 50 else entry.title
            lang = entry.language or "N/A"
            reading_time = (
                f"{entry.reading_time_seconds}s" if entry.reading_time_seconds else "N/A"
            )
            published = (
                entry.published_at.strftime("%Y-%m-%d %H:%M") if entry.published_at else "N/A"
            )

            table.add_row(str(entry.id), title, str(entry.feed_id), lang, reading_time, published)

        console.print(table)
        console.print(f"\nShowing {len(entries)} entry(s)")


@cli.command()
@click.argument("feed_id", type=int)
@click.option("--enable/--disable", default=True, help="Enable or disable the feed")
@click.pass_context
def enable_feed(ctx: click.Context, feed_id: int, enable: bool):
    """Enable or disable a feed."""
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        feed_repo = FeedRepository(session)
        feed = feed_repo.get_by_id(feed_id)

        if not feed:
            console.print(f"[red]❌ Feed with ID {feed_id} not found[/red]")
            sys.exit(1)

        if enable:
            feed_repo.enable_feed(feed)
            console.print(f"[green]✅ Feed '{feed.name}' enabled[/green]")
        else:
            feed_repo.disable_feed(feed)
            console.print(f"[yellow]⚠️  Feed '{feed.name}' disabled[/yellow]")


@cli.command()
@click.argument("feed_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this feed?")
@click.pass_context
def delete_feed(ctx: click.Context, feed_id: int):
    """Delete a feed and all its entries."""
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        feed_repo = FeedRepository(session)
        feed = feed_repo.get_by_id(feed_id)

        if not feed:
            console.print(f"[red]❌ Feed with ID {feed_id} not found[/red]")
            sys.exit(1)

        # Count entries
        entry_repo = EntryRepository(session)
        entry_count = entry_repo.count(feed_id=feed_id)

        console.print(f"Deleting feed '{feed.name}' and {entry_count} entries...")

        feed_repo.delete(feed)

        console.print(f"[green]✅ Feed deleted[/green]")


@cli.command()
@click.option("--days", type=int, default=30, help="Delete entries older than N days")
@click.confirmation_option(prompt="Are you sure you want to delete old entries?")
@click.pass_context
def cleanup(ctx: click.Context, days: int):
    """Clean up old entries from the database."""
    db_path = ctx.obj["db_path"]

    if not Path(db_path).exists():
        console.print("[red]❌ Database not found. Run 'spider-aggregation init' first.[/red]")
        sys.exit(1)

    console.print(f"[bold cyan]Cleaning up entries older than {days} days...[/bold cyan]")

    manager = DatabaseManager(db_path)

    with manager.session() as session:
        entry_repo = EntryRepository(session)
        deleted_count = entry_repo.cleanup_old_entries(days=days)

        console.print(f"[green]✅ Deleted {deleted_count} old entry(ies)[/green]")


def main():
    """Main entry point for the CLI."""
    cli(obj={})
