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

@shared_task
def check_favorites_and_notify():
    """
    Check today's menus against user favorites and generate Notifications.
    Runs daily at 4:00 AM via Celery Beat.
    """
    from api.models import DailyMenu, UserProfile, Notification
    from datetime import date
    
    today = date.today().isoformat()
    menus = DailyMenu.objects(date=today).select_related()
    
    # Cache available items to avoid redundant looping
    available_items = set()
    hall_menus = {} # map item to dining hall name
    for menu in menus:
        for item in menu.items:
            item_name = item.name.lower()
            available_items.add(item_name)
            if item_name not in hall_menus:
                hall_menus[item_name] = set()
            hall_menus[item_name].add(menu.dining_hall.name)
            
    profiles = UserProfile.objects(favorite_meals__not__size=0)
    alerts_created = 0
    for profile in profiles:
        for fav in profile.favorite_meals:
            fav_lower = fav.lower()
            # Simple substring match
            matched_items = [item for item in available_items if fav_lower in item]
            if matched_items:
                halls = set()
                for mi in matched_items:
                    halls.update(hall_menus[mi])
                
                halls_str = ", ".join(list(halls))
                msg = f"Your favorite '{fav}' is being served today at: {halls_str}."
                
                Notification(
                    django_user_id=profile.django_user_id,
                    message=msg
                ).save()
                alerts_created += 1
                
    logger.info("check_favorites_and_notify: generated %d notifications.", alerts_created)
    return alerts_created
