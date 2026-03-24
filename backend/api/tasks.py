"""Celery tasks for background data ingestion and ML model retraining."""

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

    # Retrain the item classifier on newly ingested menu data.
    retrain_item_classifier.delay()

    return count


@shared_task
def retrain_wait_time_model():
    """
    Retrain the wait-time GradientBoosting model on all collected samples.
    Runs nightly via Celery Beat (see CELERYBEAT_SCHEDULE in settings.py).
    """
    from api.ml import wait_time_model

    success = wait_time_model.train()
    if success:
        wait_time_model.invalidate_cache()
        logger.info("retrain_wait_time_model: model updated")
    else:
        logger.info("retrain_wait_time_model: insufficient data, model unchanged")
    return success


@shared_task
def retrain_item_classifier():
    """
    Retrain the NLP item classifier on the current DailyMenu corpus.
    Triggered automatically after each menu ingestion.
    """
    from api.ml import item_classifier

    success = item_classifier.train()
    if success:
        item_classifier.invalidate_cache()
        logger.info("retrain_item_classifier: model updated")
    else:
        logger.info("retrain_item_classifier: insufficient data, model unchanged")
    return success
