"""
Meal itinerary generation engine.

Given a user's macro goals, dietary restrictions, and available daily menus,
selects the combination of items across meal periods that best hits their targets.
"""

from datetime import date
from typing import Optional
import logging

from api.models import DailyMenu, DiningHall, Macros, MealPlan, UserProfile
from api.ml.item_scorer import build_user_history, score_item

logger = logging.getLogger(__name__)

MEAL_PERIODS_ORDERED = ["breakfast", "lunch", "dinner"]

# Rough split of daily macros across meal periods
PERIOD_MACRO_SPLIT = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "dinner": 0.40,
}


def _macros_to_dict(m: Macros) -> dict:
    return {
        "calories": m.calories,
        "protein_g": m.protein_g,
        "carbs_g": m.carbs_g,
        "fat_g": m.fat_g,
    }


def _sum_macros(items: list) -> dict:
    total = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for item in items:
        if item.macros:
            total["calories"] += item.macros.calories
            total["protein_g"] += item.macros.protein_g
            total["carbs_g"] += item.macros.carbs_g
            total["fat_g"] += item.macros.fat_g
    return total


def _item_passes_filters(item, profile: UserProfile) -> bool:
    """Return True if item satisfies user's dietary restrictions and allergens."""
    user_allergens = set(profile.allergens or [])
    item_allergens = set(item.allergens or [])
    if user_allergens & item_allergens:
        return False

    restrictions = set(profile.dietary_restrictions or [])
    if "vegan" in restrictions and not item.is_vegan:
        return False
    if "vegetarian" in restrictions and not item.is_vegetarian:
        return False
    if "halal" in restrictions and not item.is_halal:
        return False
    if "gluten_free" in restrictions and not item.is_gluten_free:
        return False
    return True


def _greedy_select(
    candidates: list,
    period_goal: dict,
    max_items: int = 5,
    user_history: dict | None = None,
    profile: UserProfile | None = None,
) -> list:
    """Greedily pick items from a list to approach the period macro goal."""
    scored = sorted(
        candidates,
        key=lambda i: score_item(i, period_goal, user_history, profile),
        reverse=True,
    )
    selected = []
    running = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}

    for item in scored:
        if len(selected) >= max_items:
            break
        if not item.macros:
            continue
        # Don't massively overshoot calories
        if running["calories"] + item.macros.calories > period_goal["calories"] * 1.2:
            continue
        selected.append(item)
        running["calories"] += item.macros.calories
        running["protein_g"] += item.macros.protein_g
        running["carbs_g"] += item.macros.carbs_g
        running["fat_g"] += item.macros.fat_g

    return selected


class MealPlannerService:
    def generate_plan(
        self,
        profile: UserProfile,
        target_date: Optional[date] = None,
        location: Optional[dict] = None,
    ) -> MealPlan:
        if target_date is None:
            target_date = date.today()
        date_str = target_date.isoformat()

        goals = profile.macro_goals or Macros(
            calories=2000, protein_g=150, carbs_g=200, fat_g=65
        )

        user_history = build_user_history(profile.django_user_id)
        meals = []
        total = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}

        for period in MEAL_PERIODS_ORDERED:
            split = PERIOD_MACRO_SPLIT[period]
            period_goal = {
                "calories": goals.calories * split,
                "protein_g": goals.protein_g * split,
                "carbs_g": goals.carbs_g * split,
                "fat_g": goals.fat_g * split,
            }

            # Find all menus for this period today
            menus = DailyMenu.objects(date=date_str, meal_period=period)
            if not menus:
                continue

            # Rank dining halls by proximity if location is given
            ranked_halls = self._rank_dining_halls(menus, location, profile, period)

            for menu in ranked_halls:
                candidates = [
                    item
                    for item in (menu.items or [])
                    if _item_passes_filters(item, profile)
                ]
                if not candidates:
                    continue

                selected = _greedy_select(
                    candidates, period_goal, user_history=user_history, profile=profile
                )
                if not selected:
                    continue

                period_macros = _sum_macros(selected)
                for k in total:
                    total[k] += period_macros[k]

                from api.services.wait_time import WaitTimeService

                wt = WaitTimeService().predict(menu.dining_hall, period)

                meals.append(
                    {
                        "period": period,
                        "dining_hall_id": str(menu.dining_hall.id),
                        "dining_hall_name": menu.dining_hall.name,
                        "items": [
                            {
                                "name": i.name,
                                "station": i.station,
                                "category": i.category,
                                "macros": _macros_to_dict(i.macros) if i.macros else {},
                            }
                            for i in selected
                        ],
                        "macros": period_macros,
                        "estimated_wait_minutes": wt,
                        "supports_get_app": menu.dining_hall.supports_get_app,
                    }
                )
                break  # one dining hall per period

        plan = MealPlan(
            django_user_id=profile.django_user_id,
            date=date_str,
            meals=meals,
            total_macros=Macros(**total),
            goal_macros=goals,
        )
        plan.save()
        return plan

    def _rank_dining_halls(
        self, menus, location: Optional[dict], profile: UserProfile, period: str
    ) -> list:
        """Sort menus by proximity to user's current location (if known)."""
        if not location:
            return list(menus)

        import math

        def distance(menu):
            hall = menu.dining_hall
            dlat = hall.location_lat - location["lat"]
            dlng = hall.location_lng - location["lng"]
            return math.sqrt(dlat**2 + dlng**2)

        return sorted(menus, key=distance)