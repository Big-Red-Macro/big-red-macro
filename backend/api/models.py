from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    FloatField,
    IntField,
    BooleanField,
    ListField,
    EmbeddedDocumentField,
    DateTimeField,
    DictField,
    ReferenceField,
)
from datetime import datetime


class Macros(EmbeddedDocument):
    calories = FloatField(required=True, default=0)
    protein_g = FloatField(required=True, default=0)
    carbs_g = FloatField(required=True, default=0)
    fat_g = FloatField(required=True, default=0)
    fiber_g = FloatField(default=0)
    sodium_mg = FloatField(default=0)


class MenuItem(EmbeddedDocument):
    name = StringField(required=True)
    description = StringField()
    category = StringField()  # NLP-classified bucket (protein, grain, veggie, etc.)
    macros = EmbeddedDocumentField(Macros)
    allergens = ListField(StringField())
    is_vegan = BooleanField(default=False)
    is_vegetarian = BooleanField(default=False)
    is_halal = BooleanField(default=False)
    is_gluten_free = BooleanField(default=False)
    station = StringField()  # e.g. "Grill", "Salad Bar", "International"
    healthy = BooleanField(default=False)  # Cornell Dining "healthy" flag from API


class DiningHall(Document):
    """Static info about each Cornell dining location."""

    meta = {"collection": "dining_halls"}

    name = StringField(required=True, unique=True)
    short_name = StringField(required=True)  # e.g. "okenshields"
    location_lat = FloatField(required=True)
    location_lng = FloatField(required=True)
    dining_type = StringField(
        choices=["residential", "cafe", "retail"], default="residential"
    )
    accepts_brbs = BooleanField(default=True)
    accepts_meal_swipe = BooleanField(default=False)
    supports_get_app = BooleanField(default=False)  # order-ahead via GET
    operating_hours = DictField()  # {"breakfast": "7:00-10:30", ...}
    building_code = StringField()  # for geofencing
    campus_area = StringField()  # e.g. "North", "West", "Central", "East"
    eatery_id = IntField()  # Cornell Dining API numeric ID


class DailyMenu(Document):
    """Menu for a single dining hall on a specific date."""

    meta = {
        "collection": "daily_menus",
        "indexes": [
            {"fields": ["dining_hall", "date", "meal_period"], "unique": True},
            "date",
        ],
    }

    dining_hall = ReferenceField(DiningHall, required=True)
    date = StringField(required=True)  # YYYY-MM-DD
    meal_period = StringField(
        choices=["breakfast", "lunch", "dinner", "brunch"], required=True
    )
    items = ListField(EmbeddedDocumentField(MenuItem))
    fetched_at = DateTimeField(default=datetime.utcnow)


class WaitTimeSample(Document):
    """Historical crowd/wait-time observations for ML training."""

    meta = {
        "collection": "wait_time_samples",
        "indexes": ["dining_hall", "recorded_at"],
    }

    dining_hall = ReferenceField(DiningHall, required=True)
    recorded_at = DateTimeField(required=True)
    day_of_week = IntField(required=True)  # 0=Mon … 6=Sun
    hour = IntField(required=True)
    minute = IntField(required=True)
    estimated_wait_minutes = IntField(required=True)
    occupancy_pct = FloatField()  # 0.0–1.0


class UserProfile(Document):
    """Extended profile stored in MongoDB, keyed by Django user ID."""

    meta = {"collection": "user_profiles"}

    django_user_id = IntField(required=True, unique=True)
    cornell_netid = StringField()
    macro_goals = EmbeddedDocumentField(Macros)
    allergens = ListField(StringField())
    dietary_restrictions = ListField(
        StringField()
    )  # ["vegan", "halal", "gluten_free"]
    class_schedule = ListField(
        DictField()
    )  # [{"day": "MWF", "start": "10:10", "end": "11:00", "location": "Uris Hall"}]
    home_location = DictField()  # {"lat": ..., "lng": ...}
    meal_plan_type = StringField(
        choices=["traditional", "west_campus", "bear_necessities", "none"],
        default="traditional",
    )
    google_auth_token = DictField()
    favorite_meals = ListField(StringField())
    updated_at = DateTimeField(default=datetime.utcnow)


class MealPlan(Document):
    """A generated daily meal itinerary for a user."""

    meta = {
        "collection": "meal_plans",
        "indexes": ["django_user_id", "date"],
    }

    django_user_id = IntField(required=True)
    date = StringField(required=True)  # YYYY-MM-DD
    meals = ListField(
        DictField()
    )  # [{"period": "lunch", "dining_hall": ..., "items": [...], "macros": {...}, "suggested_arrival": "12:15", "estimated_wait": 8}]
    total_macros = EmbeddedDocumentField(Macros)
    goal_macros = EmbeddedDocumentField(Macros)
    generated_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)

class Notification(Document):
    """Stores user notifications (e.g., favorite food alerts)."""
    meta = {"collection": "notifications", "indexes": ["django_user_id", "created_at"]}
    
    django_user_id = IntField(required=True)
    message = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    is_read = BooleanField(default=False)
