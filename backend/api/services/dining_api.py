"""
Cornell Open Data Initiative — Dining API client.
Docs: https://now.dining.cornell.edu/api/1.0/dining/eateries.json
"""

import logging
from datetime import date
from typing import Optional

import requests
from django.conf import settings

from api.models import DailyMenu, DiningHall, Macros, MenuItem

logger = logging.getLogger(__name__)

MEAL_PERIODS = ["breakfast", "brunch", "lunch", "dinner"]


class CornellDiningClient:
    BASE_URL = settings.CORNELL_DINING_API_BASE

    def get_eateries(self) -> list[dict]:
        """Fetch all Cornell eateries and their current menus."""
        url = f"{self.BASE_URL}/dining/eateries.json"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json().get("data", {}).get("eateries", [])
        except requests.RequestException as e:
            logger.error("Failed to fetch Cornell Dining eateries: %s", e)
            return []

    def get_menu_for_date(
        self, eatery_id: int, target_date: Optional[date] = None
    ) -> dict:
        """Fetch the menu for a specific eatery and date."""
        if target_date is None:
            target_date = date.today()
        url = f"{self.BASE_URL}/dining/eateries/{eatery_id}/menus.json"
        params = {"startdate": target_date.isoformat(), "enddate": target_date.isoformat()}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json().get("data", {})
        except requests.RequestException as e:
            logger.error("Failed to fetch menu for eatery %s: %s", eatery_id, e)
            return {}

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    def _parse_macros(self, nutrition: dict) -> Macros:
        def _val(key: str) -> float:
            item = nutrition.get(key, {})
            if isinstance(item, dict):
                return float(item.get("quantity", 0) or 0)
            return float(item or 0)

        return Macros(
            calories=_val("calories"),
            protein_g=_val("protein"),
            carbs_g=_val("totalCarbohydrates"),
            fat_g=_val("totalFat"),
            fiber_g=_val("dietaryFiber"),
            sodium_mg=_val("sodium"),
        )

    def _parse_allergens(self, item_data: dict) -> list[str]:
        raw = item_data.get("dietaryRestrictions", [])
        # Cornell API returns codes like "V", "VG", "H", "LC", "GF", "A", "T", "N"
        allergen_map = {
            "A": "alcohol",
            "T": "tree_nuts",
            "N": "peanuts",
            "GF": "gluten_free",  # actually a positive label — handle separately
        }
        return [allergen_map[code] for code in raw if code in allergen_map]

    def _parse_dietary_flags(self, item_data: dict) -> dict:
        codes = set(item_data.get("dietaryRestrictions", []))
        return {
            "is_vegan": "VG" in codes,
            "is_vegetarian": "V" in codes or "VG" in codes,
            "is_halal": "H" in codes,
            "is_gluten_free": "GF" in codes,
        }

    def _parse_menu_item(self, item_data: dict) -> MenuItem:
        nutrition = item_data.get("nutritionInfo", {})
        flags = self._parse_dietary_flags(item_data)
        return MenuItem(
            name=item_data.get("item", "Unknown"),
            description=item_data.get("description", ""),
            macros=self._parse_macros(nutrition),
            allergens=self._parse_allergens(item_data),
            station=item_data.get("category", ""),
            **flags,
        )

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_all_menus(self, target_date: Optional[date] = None) -> int:
        """Pull menus from Cornell Dining API and upsert into MongoDB."""
        if target_date is None:
            target_date = date.today()
        date_str = target_date.isoformat()
        count = 0

        eateries = self.get_eateries()
        for eatery in eateries:
            hall = self._upsert_dining_hall(eatery)
            eatery_id = eatery.get("id")
            operating_hours = eatery.get("operatingHours", [])

            # Find today's hours
            todays_hours = next(
                (h for h in operating_hours if h.get("date") == date_str), None
            )
            if not todays_hours:
                continue

            for event in todays_hours.get("events", []):
                period = event.get("descr", "").lower()
                if period not in MEAL_PERIODS:
                    continue

                items = [
                    self._parse_menu_item(i)
                    for cat in event.get("menu", [])
                    for i in cat.get("items", [])
                ]

                DailyMenu.objects(
                    dining_hall=hall, date=date_str, meal_period=period
                ).update_one(
                    set__items=items,
                    set__fetched_at=__import__("datetime").datetime.utcnow(),
                    upsert=True,
                )
                count += 1

        logger.info("Ingested %d menu periods for %s", count, date_str)
        return count

    def _upsert_dining_hall(self, eatery: dict) -> DiningHall:
        coords = eatery.get("coordinates", {})
        hall, _ = DiningHall.objects.get_or_create(
            name=eatery.get("name", "Unknown"),
            defaults={
                "short_name": eatery.get("slug", ""),
                "location_lat": float(coords.get("latitude", 0)),
                "location_lng": float(coords.get("longitude", 0)),
                "accepts_brbs": True,
                "supports_get_app": eatery.get("onlineOrdering", False),
            },
        )
        return hall
