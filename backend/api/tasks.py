"""Celery tasks for background data ingestion."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def refresh_daily_menus():
    """Pull today's menus from Cornell Dining API. Runs hourly via Celery Beat."""
    from api.services.dining_api import CornellDiningClient

    client = CornellDiningClient()
    count = client.ingest_all_menus()
    logger.info("refresh_daily_menus: ingested %d menu periods", count)
    return count
