"""
Digest service for aggregating and summarizing feed entries.

This is an Application Service that orchestrates multiple components:
- Repositories (for data access)
- LLM Client (for AI summarization)
- EmailService (for sending emails)

Application Services coordinate workflows and cross-cutting concerns.
They are different from Domain Service Facades (core/services/).
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from spider_aggregation.config import get_config
from spider_aggregation.core.llm_client import BaseLLMClient, LLMResponse, create_llm_client
from spider_aggregation.logger import get_logger
from spider_aggregation.models import DigestLogCreate, DigestLogModel, EntryModel, FeedModel
from spider_aggregation.application.email_service import EmailResult, create_email_service
from spider_aggregation.storage.repositories.entry_repo import EntryRepository
from spider_aggregation.storage.repositories.feed_repo import FeedRepository

logger = get_logger(__name__)


@dataclass
class FeedEntries:
    """Entries from a single feed."""

    feed: FeedModel
    entries: list[EntryModel] = field(default_factory=list)


@dataclass
class DigestResult:
    """Result of digest generation."""

    success: bool
    entry_count: int = 0
    feed_count: int = 0
    subject: str = ""
    summary_content: str = ""
    error: Optional[str] = None


class DigestService:
    """Service for generating and sending digest emails."""

    # System prompt for aggregation mode
    AGGREGATION_SYSTEM_PROMPT = """你是一位专业的信息摘要助手。你的任务是将多篇RSS订阅文章进行聚合总结。

请遵循以下要求：
1. 提取这些文章的核心主题和关键信息
2. 总结内容要简洁明了，突出重点
3. 按主题或重要程度组织内容
4. 如果文章涉及技术内容，保留关键的技术细节
5. 使用中文输出总结

输出格式：
- 总览：简要概括这批文章的整体内容（2-3句话）
- 要点：列出3-5个关键要点，每个要点包含简要说明
- 重点文章：如果有特别重要的文章，单独提及标题和核心内容"""

    def __init__(
        self,
        session: Session,
        llm_client: Optional[BaseLLMClient] = None,
        entries_per_feed: Optional[int] = None,
        max_age_hours: Optional[int] = None,
        mode: Optional[str] = None,
    ):
        """Initialize digest service.

        Args:
            session: Database session
            llm_client: LLM client (created from config if not provided)
            entries_per_feed: Number of entries to include per feed
            max_age_hours: Only include entries from last N hours
            mode: Digest mode (aggregate or individual)
        """
        self.session = session
        self.config = get_config()
        self.digest_config = self.config.digest
        self.email_config = self.config.email

        self.entries_per_feed = entries_per_feed or self.digest_config.entries_per_feed
        self.max_age_hours = max_age_hours or self.digest_config.max_age_hours
        self.mode = mode or self.digest_config.mode

        self.llm_client = llm_client
        self._llm_initialized = False

    def _ensure_llm(self) -> bool:
        """Ensure LLM client is initialized.

        Returns:
            True if LLM is ready
        """
        if self._llm_initialized:
            return True

        if not self.config.llm.enabled:
            logger.error("LLM is not enabled in config")
            return False

        try:
            self.llm_client = self.llm_client or create_llm_client()
            self._llm_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return False

    def _collect_entries(self) -> list[FeedEntries]:
        """Collect recent entries from all enabled feeds.

        Returns:
            List of FeedEntries grouped by feed
        """
        feed_repo = FeedRepository(self.session)
        entry_repo = EntryRepository(self.session)

        # Get all enabled feeds
        feeds = feed_repo.list(enabled=True, limit=1000)

        cutoff_time = datetime.utcnow() - timedelta(hours=self.max_age_hours)

        result = []
        for feed in feeds:
            # Get recent entries for this feed
            entries = (
                self.session.query(EntryModel)
                .filter(
                    EntryModel.feed_id == feed.id,
                    EntryModel.published_at >= cutoff_time,
                )
                .order_by(EntryModel.published_at.desc())
                .limit(self.entries_per_feed)
                .all()
            )

            if entries:
                result.append(FeedEntries(feed=feed, entries=entries))
                logger.debug(f"Collected {len(entries)} entries from feed '{feed.name}'")

        return result

    def _build_aggregation_prompt(self, feed_entries: list[FeedEntries]) -> str:
        """Build prompt for aggregation mode.

        Args:
            feed_entries: List of feed entries to summarize

        Returns:
            Prompt string
        """
        lines = ["请将以下RSS订阅文章进行聚合总结：\n"]

        for fe in feed_entries:
            lines.append(f"\n## {fe.feed.name or fe.feed.url}\n")

            for i, entry in enumerate(fe.entries, 1):
                lines.append(f"\n### 文章{i}: {entry.title}")
                lines.append(f"链接: {entry.link}")

                # Use summary or content, truncated
                content = entry.summary or entry.content or ""
                if len(content) > 1000:
                    content = content[:1000] + "..."
                lines.append(f"内容: {content}\n")

        lines.append("\n请根据以上文章生成聚合总结。")
        return "\n".join(lines)

    def _generate_summary(self, feed_entries: list[FeedEntries]) -> LLMResponse:
        """Generate aggregated summary using LLM.

        Args:
            feed_entries: List of feed entries

        Returns:
            LLMResponse with summary
        """
        if not self._ensure_llm():
            return LLMResponse(success=False, error="LLM client not available")

        prompt = self._build_aggregation_prompt(feed_entries)

        logger.info(f"Generating aggregated summary for {len(feed_entries)} feeds")
        return self.llm_client.chat(
            prompt=prompt,
            system_prompt=self.AGGREGATION_SYSTEM_PROMPT,
        )

    def _build_email_content(
        self, feed_entries: list[FeedEntries], summary: str
    ) -> tuple[str, str]:
        """Build email content (plain text and HTML).

        Args:
            feed_entries: List of feed entries
            summary: Generated summary

        Returns:
            Tuple of (plain_text, html)
        """
        # Build subject
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        subject = f"{self.digest_config.subject_prefix} 订阅聚合总结 - {now}"

        # Build plain text
        text_lines = [
            subject,
            "=" * 50,
            "",
            "## AI聚合总结",
            "",
            summary,
            "",
            "=" * 50,
            "",
            "## 包含的文章",
            "",
        ]

        for fe in feed_entries:
            text_lines.append(f"\n### {fe.feed.name or fe.feed.url}")
            for entry in fe.entries:
                text_lines.append(f"- {entry.title}")
                text_lines.append(f"  {entry.link}")
            text_lines.append("")

        text_lines.append("--")
        text_lines.append("由 MindWeaver 自动生成")

        plain_text = "\n".join(text_lines)

        # Build HTML
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '<meta charset="utf-8">',
            "<style>",
            "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }",
            "h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }",
            "h2 { color: #34495e; margin-top: 30px; }",
            "h3 { color: #7f8c8d; }",
            ".summary { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }",
            ".feed { margin: 20px 0; padding: 15px; background: #fff; border: 1px solid #e9ecef; border-radius: 6px; }",
            ".entry { margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 3px solid #3498db; }",
            ".entry-title { font-weight: bold; margin-bottom: 5px; }",
            ".entry-link { color: #3498db; text-decoration: none; font-size: 0.9em; }",
            ".footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e9ecef; color: #95a5a6; font-size: 0.85em; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{subject}</h1>",
            '<div class="summary">',
            "<h2>AI聚合总结</h2>",
            f"<pre style='white-space: pre-wrap; word-wrap: break-word;'>{summary.replace(chr(10), '<br>')}</pre>",
            "</div>",
            "<h2>包含的文章</h2>",
        ]

        for fe in feed_entries:
            html_parts.append('<div class="feed">')
            feed_name = fe.feed.name or fe.feed.url
            html_parts.append(f"<h3>{feed_name}</h3>")

            for entry in fe.entries:
                html_parts.append('<div class="entry">')
                html_parts.append(f'<div class="entry-title">{entry.title}</div>')
                html_parts.append(f'<a class="entry-link" href="{entry.link}">{entry.link}</a>')
                html_parts.append("</div>")

            html_parts.append("</div>")

        html_parts.extend(
            [
                '<div class="footer">',
                "由 MindWeaver 自动生成",
                "</div>",
                "</body>",
                "</html>",
            ]
        )

        html = "\n".join(html_parts)
        return plain_text, html

    def generate_and_send(self, force: bool = False) -> DigestResult:
        """Generate digest and send email.

        Args:
            force: Force generation even if disabled in config

        Returns:
            DigestResult
        """
        if not force and not self.digest_config.enabled:
            logger.info("Digest is disabled in config")
            return DigestResult(success=False, error="Digest is disabled")

        if not self.email_config.enabled:
            logger.error("Email is not enabled in config")
            return DigestResult(success=False, error="Email is not enabled")

        if not self.email_config.to_addresses:
            logger.error("No recipients configured")
            return DigestResult(success=False, error="No recipients configured")

        # Collect entries
        feed_entries = self._collect_entries()
        if not feed_entries:
            logger.info("No entries to summarize")
            return DigestResult(
                success=True,
                entry_count=0,
                feed_count=0,
                subject="无新内容",
                summary_content="本次没有发现新的订阅内容。",
            )

        entry_count = sum(len(fe.entries) for fe in feed_entries)
        feed_count = len(feed_entries)

        logger.info(f"Collected {entry_count} entries from {feed_count} feeds")

        # Generate summary
        llm_response = self._generate_summary(feed_entries)
        if not llm_response.success:
            error = f"Failed to generate summary: {llm_response.error}"
            logger.error(error)
            self._log_digest(
                status="failed",
                entry_count=entry_count,
                feed_ids=[fe.feed.id for fe in feed_entries],
                subject="生成失败",
                error_message=error,
            )
            return DigestResult(success=False, error=error)

        summary = llm_response.content or ""

        # Build email content
        plain_text, html = self._build_email_content(feed_entries, summary)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        subject = f"{self.digest_config.subject_prefix} 订阅聚合总结 - {now}"

        # Send email
        email_service = create_email_service()
        result = email_service.send_email(
            to_addresses=self.email_config.to_addresses,
            subject=subject,
            body_text=plain_text,
            body_html=html,
        )

        if result.success:
            logger.info("Digest email sent successfully")
            self._log_digest(
                status="success",
                entry_count=entry_count,
                feed_ids=[fe.feed.id for fe in feed_entries],
                subject=subject,
                summary_content=summary,
            )
            return DigestResult(
                success=True,
                entry_count=entry_count,
                feed_count=feed_count,
                subject=subject,
                summary_content=summary,
            )
        else:
            error = f"Failed to send email: {result.error}"
            logger.error(error)
            self._log_digest(
                status="failed",
                entry_count=entry_count,
                feed_ids=[fe.feed.id for fe in feed_entries],
                subject=subject,
                error_message=error,
            )
            return DigestResult(success=False, error=error)

    def _log_digest(
        self,
        status: str,
        entry_count: int,
        feed_ids: list[int],
        subject: str,
        summary_content: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Log digest to database.

        Args:
            status: Digest status
            entry_count: Number of entries
            feed_ids: List of feed IDs
            subject: Email subject
            summary_content: Generated summary
            error_message: Error message if failed
        """
        try:
            log = DigestLogModel(
                status=status,
                entry_count=entry_count,
                feed_ids=json.dumps(feed_ids),
                subject=subject,
                to_addresses=json.dumps(self.email_config.to_addresses),
                summary_content=summary_content,
                error_message=error_message,
            )
            self.session.add(log)
            self.session.commit()
            logger.debug(f"Digest logged: {log.id}")
        except Exception as e:
            logger.error(f"Failed to log digest: {e}")
            self.session.rollback()


def create_digest_service(
    session: Session,
    llm_client: Optional[BaseLLMClient] = None,
    entries_per_feed: Optional[int] = None,
    max_age_hours: Optional[int] = None,
    mode: Optional[str] = None,
) -> DigestService:
    """Factory function to create DigestService.

    Args:
        session: Database session
        llm_client: Optional LLM client
        entries_per_feed: Entries per feed
        max_age_hours: Max age of entries
        mode: Digest mode

    Returns:
        Configured DigestService
    """
    return DigestService(
        session=session,
        llm_client=llm_client,
        entries_per_feed=entries_per_feed,
        max_age_hours=max_age_hours,
        mode=mode,
    )
