"""
Application services for MindWeaver.

This module contains application-level services that orchestrate workflows
and cross-cutting concerns. These services operate at a higher level than
the domain service facades in core/services/.

Services here:
- EmailService: SMTP email sending (infrastructure)
- DigestService: Digest generation and email workflow (application workflow)

Architecture:
    Web Layer -> Application Services -> (Domain Services + Repositories)
                      ↓
                 Application Services (application/)
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
    Domain Services              Repositories
    (core/services/)          (storage/repositories/)
        ↓                           ↓
    Core Modules              Database
    (core/*)

Example:
    # Application service coordinates multiple components
    from spider_aggregation.application import DigestService

    digest_service = DigestService(session)
    digest_service.generate_and_send()
"""

from spider_aggregation.application.digest_service import DigestService, create_digest_service
from spider_aggregation.application.email_service import EmailService, create_email_service

__all__ = [
    "DigestService",
    "create_digest_service",
    "EmailService",
    "create_email_service",
]
