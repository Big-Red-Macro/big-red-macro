"""
Cornell Open Data Initiative — Dining API client.

Real API base: https://admin-now.dining.cornell.edu/api/1.0/
Docs:          https://codi.engineering.cornell.edu/data/diningdata.html

Key facts discovered from the live API (2026-03):
  - All eatery + menu data is returned in a single call: GET dining/eateries.json
  - There is NO separate per-eatery menu endpoint.
  - Menu items carry only: item (name), healthy (bool), sortIdx.
  - No per-item nutrition, allergen, or dietary-restriction codes exist in the API.
  - Macros are estimated via api.ml.macro_estimator using category priors.
  - NLP category is assigned by api.ml.item_classifier.
  - payMethods determines accepts_brbs / accepts_meal_swipe.
  - eateryTypes determines dining_type (residential / cafe / retail).

Menu format differences between venue types:
  Dining rooms  → operatingHours.events.menu  (specific daily items per meal period)
  Cafes/retail  → diningItems                 (permanent category-level offerings,
                                               e.g. "Burgers", "Grab-n-Go")
                  operatingHours.events carry start/end times but empty menus.

Non-standard event descr values seen in the wild:
  "late lunch"       → normalised to "lunch"
  "late night"       → normalised to "dinner"
  "available all day"→ ingested for breakfast, lunch, and dinner
  "open" / ""        → hours-only events with no menu items (skipped after item parse)
"""

import logging
from datetime import date, datetime, timezone
from typing import Optional

import requests
from django.conf import settings

from api.models import DailyMenu, DiningHall, Macros, MenuItem

logger = logging.getLogger(__name__)

# Canonical meal periods stored in MongoDB
MEAL_PERIODS = {"breakfast", "brunch", "lunch", "dinner"}

# Non-standard API event descr → canonical period
_PERIOD_NORMALISE: dict[str, str] = {
    "late lunch": "lunch",
    "late night":  "dinner",
}

# "available all day" items are duplicated into all three main periods
_ALL_DAY_PERIODS = ("breakfast", "lunch", "dinner")

# eateryTypes.descrshort → our dining_type vocab
_EATERY_TYPE_MAP: dict[str, str] = {
    "dining room":       "residential",
    "cafe":              "cafe",
    "coffee shop":       "cafe",
    "food court":        "cafe",
    "convenience store": "cafe",
    "cart":              "retail",
}

# payMethods.descrshort substrings that indicate BRB / meal-swipe acceptance
_BRB_KEYWORDS   = {"meal plan - debit"}
_SWIPE_KEYWORDS = {"meal plan - swipe"}
_GET_KEYWORDS   = {"mobile payment", "apple pay", "google"}


class CornellDiningClient:
    BASE_URL = settings.CORNELL_DINING_API_BASE  # https://admin-now.dining.cornell.edu/api/1.0

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.BASE_URL}/{path}"
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("Cornell Dining API request failed [%s]: %s", url, exc)
            return {}


    def get_eateries(self) -> list[dict]:
        """
        Fetch all Cornell eateries with embedded menus (single endpoint).

        Returns the raw list from data.eateries, or [] on failure.
        """
        data = self._get("dining/eateries.json")
        return data.get("data", {}).get("eateries", [])

    def get_announcements(self) -> list[dict]:
        """Fetch site-wide dining announcements."""
        data = self._get("dining/announcements.json")
        return data.get("data", {}).get("announcements", [])


    @staticmethod
    def _normalise_period(raw: str) -> Optional[str]:
        """
        Map a Cornell API event descr to a canonical meal period.

        Returns None for events that should be skipped entirely
        (hours-only 'open' events, blank strings).
        """
        raw = (raw or "").strip().lower()
        if raw in MEAL_PERIODS:
            return raw
        if raw in _PERIOD_NORMALISE:
            return _PERIOD_NORMALISE[raw]
        if raw == "available all day":
            return "available_all_day"   # handled specially in the caller
        return None  # "open", "", and unknown values → skip

    @staticmethod
    def _dining_type(eatery: dict) -> str:
        """Map Cornell eateryTypes to our residential / cafe / retail vocab."""
        for t in eatery.get("eateryTypes", []):
            mapped = _EATERY_TYPE_MAP.get(t.get("descrshort", "").lower())
            if mapped:
                return mapped
        return "cafe"

    @staticmethod
    def _payment_flags(eatery: dict) -> dict:
        """Return accepts_brbs, accepts_meal_swipe, supports_get_app flags."""
        accepts_brbs = False
        accepts_meal_swipe = False
        supports_get_app = bool(eatery.get("onlineOrdering"))
        for pm in eatery.get("payMethods", []):
            short = pm.get("descrshort", "").lower()
            if any(k in short for k in _BRB_KEYWORDS):
                accepts_brbs = True
            if any(k in short for k in _SWIPE_KEYWORDS):
                accepts_meal_swipe = True
            if any(k in short for k in _GET_KEYWORDS):
                supports_get_app = True
        return {
            "accepts_brbs":      accepts_brbs,
            "accepts_meal_swipe": accepts_meal_swipe,
            "supports_get_app":  supports_get_app,
        }

    @staticmethod
    def _operating_hours_summary(eatery: dict) -> dict:
        """
        Build a human-readable hours dict keyed by canonical meal period.

        Includes non-standard periods (late lunch → lunch, late night → dinner).
        Example: {"brunch": "11:00am–2:00pm", "dinner": "5:00pm–7:00pm"}
        """
        hours: dict[str, str] = {}
        today_str = date.today().isoformat()
        for oh in eatery.get("operatingHours", []):
            if oh.get("date") == today_str:
                for ev in oh.get("events", []):
                    raw = (ev.get("descr") or "").strip().lower()
                    # Use the full open window for "open" events (cafes)
                    if raw in ("open", ""):
                        hours["open"] = f"{ev.get('start', '')}–{ev.get('end', '')}"
                        continue
                    period = CornellDiningClient._normalise_period(raw)
                    if period and period != "available_all_day":
                        hours[period] = f"{ev.get('start', '')}–{ev.get('end', '')}"
        return hours

    def _parse_menu_item(self, item_data: dict, station: str) -> MenuItem:
        """
        Build a MenuItem from a raw API item dict.

        The Cornell API provides only: item (name), healthy (bool), sortIdx.
        NLP category and estimated macros are generated by the ML pipeline.
        """
        from api.ml import item_classifier
        from api.ml.macro_estimator import estimate as estimate_macros

        name = (item_data.get("item") or "").strip() or "Unknown"
        healthy = bool(item_data.get("healthy", False))
        category = item_classifier.classify(name)
        est = estimate_macros(category, station, healthy)

        return MenuItem(
            name=name,
            category=category,
            station=station,
            healthy=healthy,
            macros=Macros(
                calories=est.calories,
                protein_g=est.protein_g,
                carbs_g=est.carbs_g,
                fat_g=est.fat_g,
                fiber_g=est.fiber_g,
                sodium_mg=est.sodium_mg,
            ),
            # Allergen / dietary flags: not available in the Cornell API.
            # Future: enrich via NetNutrition scrape or manual tagging.
            allergens=[],
            is_vegan=False,
            is_vegetarian=False,
            is_halal=False,
            is_gluten_free=False,
        )

    def _items_from_event_menu(self, event: dict) -> list[MenuItem]:
        """Parse items from a dining-room-style event.menu list."""
        items = []
        for cat in event.get("menu", []):
            station = (cat.get("category") or "").strip()
            for raw_item in cat.get("items", []):
                items.append(self._parse_menu_item(raw_item, station))
        return items

    def _items_from_dining_items(self, eatery: dict) -> list[MenuItem]:
        """
        Build MenuItems from an eatery's static diningItems list.

        diningItems are permanent category-level offerings used by cafes
        (e.g. "Burgers", "Grab-n-Go").  They don't change daily but they
        represent what the cafe actually serves, so they're valid for meal
        planning when no event-level menu exists.
        """
        items = []
        for raw in eatery.get("diningItems", []):
            station = (raw.get("category") or "").strip()
            items.append(self._parse_menu_item(raw, station))
        return items


    def ingest_all_menus(self, target_date: Optional[date] = None) -> int:
        """
        Pull menus from Cornell Dining API and upsert into MongoDB.

        Handles both dining-room (event-level daily menus) and cafe
        (diningItems static catalogue) formats.

        Returns the number of (eatery, date, period) records upserted.
        """
        if target_date is None:
            target_date = date.today()
        date_str = target_date.isoformat()
        count = 0

        eateries = self.get_eateries()
        if not eateries:
            logger.warning("ingest_all_menus: no eateries returned from Cornell API")
            return 0

        for eatery in eateries:
            hall = self._upsert_dining_hall(eatery)
            upserted_periods: set[str] = set()

            for oh in eatery.get("operatingHours", []):
                if oh.get("date") != date_str:
                    continue

                for event in oh.get("events", []):
                    raw_period = (event.get("descr") or "").strip().lower()
                    period = self._normalise_period(raw_period)
                    if period is None:
                        continue

                    if period == "available_all_day":
                        target_periods = _ALL_DAY_PERIODS
                        items = self._items_from_event_menu(event)
                    else:
                        target_periods = (period,)
                        items = self._items_from_event_menu(event)

                    if not items:
                        continue

                    for p in target_periods:
                        DailyMenu.objects(
                            dining_hall=hall, date=date_str, meal_period=p,
                        ).update_one(
                            set__items=items,
                            set__fetched_at=datetime.now(timezone.utc),
                            upsert=True,
                        )
                        upserted_periods.add(p)
                        count += 1

            # Only runs when the event loop produced no menu items for this eatery.
            if not upserted_periods and eatery.get("diningItems"):
                items = self._items_from_dining_items(eatery)
                if items:
                    # Determine which periods the cafe is open today
                    open_periods = self._open_periods_today(eatery, date_str)
                    if not open_periods:
                        # If no structured periods found, default to all main periods
                        open_periods = list(MEAL_PERIODS - {"brunch"})
                    for p in open_periods:
                        DailyMenu.objects(
                            dining_hall=hall, date=date_str, meal_period=p,
                        ).update_one(
                            set__items=items,
                            set__fetched_at=datetime.now(timezone.utc),
                            upsert=True,
                        )
                        count += 1

        logger.info("ingest_all_menus: upserted %d menu periods for %s", count, date_str)
        return count

    @staticmethod
    def _open_periods_today(eatery: dict, date_str: str) -> list[str]:
        """
        Return which canonical meal periods the eatery is open on date_str,
        inferred from its operatingHours event timestamps.
        """
        periods: list[str] = []
        for oh in eatery.get("operatingHours", []):
            if oh.get("date") != date_str:
                continue
            for ev in oh.get("events", []):
                start_ts = ev.get("startTimestamp")
                end_ts = ev.get("endTimestamp")
                if start_ts is None or end_ts is None:
                    continue
                start_hour = datetime.fromtimestamp(start_ts).hour
                end_hour   = datetime.fromtimestamp(end_ts).hour
                # Classify by start hour
                if 5 <= start_hour < 11:
                    if "breakfast" not in periods:
                        periods.append("breakfast")
                if 11 <= start_hour < 15:
                    if "lunch" not in periods:
                        periods.append("lunch")
                if 15 <= start_hour or end_hour >= 17:
                    if "dinner" not in periods:
                        periods.append("dinner")
        return periods

    def _upsert_dining_hall(self, eatery: dict) -> DiningHall:
        coords = eatery.get("coordinates") or {}
        payment = self._payment_flags(eatery)
        campus_area = (eatery.get("campusArea") or {}).get("descrshort", "")

        hall_name = eatery.get("name", "Unknown")
        defaults = {
            "short_name":      eatery.get("slug") or eatery.get("nameshort", ""),
            "location_lat":    float(coords.get("latitude") or eatery.get("latitude") or 0),
            "location_lng":    float(coords.get("longitude") or eatery.get("longitude") or 0),
            "dining_type":     self._dining_type(eatery),
            "campus_area":     campus_area,
            "eatery_id":       int(eatery.get("id") or 0),
            "operating_hours": self._operating_hours_summary(eatery),
            **payment,
        }
        hall = DiningHall.objects(name=hall_name).first()
        if not hall:
            hall = DiningHall(name=hall_name, **defaults)
            hall.save()

        # Refresh mutable fields on every ingest (hours and payment flags can change)
        update_kwargs = {
            "set__operating_hours": self._operating_hours_summary(eatery),
            "set__campus_area":     campus_area,
            "set__eatery_id":       int(eatery.get("id") or 0),
            **{f"set__{k}": v for k, v in payment.items()},
        }
        DiningHall.objects(name=hall.name).update_one(**update_kwargs)
        hall.reload()
        return hall
