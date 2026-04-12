"""
Personalised meal-item scorer.

Replaces the fixed-weight protein-density heuristic in meal_planner.py with a
two-component score:

  1. Macro cosine similarity (weight 0.55)
     Measures how well an item's macronutrient calorie-ratio profile aligns
     with the user's target ratio for the meal period.  Uses cosine similarity
     so the absolute magnitude of the goal doesn't skew the result.

  2. Calorie fit (weight 0.30)
     How close the item's calorie count is to the per-item budget derived from
     the period goal.  A sigmoid-like decay penalises items that are far above
     or below the expected per-item contribution.

  3. History preference boost (weight 0.15)
     Soft preference signal built from the user's recent meal plan history.
     Station- and category-level selection frequency is used to nudge items
     the user has historically preferred.

Total score is in [0, 1] with higher = better fit.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Calorie conversion factors (kcal per gram)
_PROTEIN_KCAL = 4.0
_CARBS_KCAL = 4.0
_FAT_KCAL = 9.0

# Component weights (must sum to 1.0)
_W_COSINE = 0.55
_W_CALFIT = 0.30
_W_HISTORY = 0.15

# How many recent meal plans to look back for history
_HISTORY_LOOKBACK = 14


# ---------------------------------------------------------------------------
# Macro ratio helpers
# ---------------------------------------------------------------------------

def _item_macro_vector(item) -> Optional[np.ndarray]:
    """
    Return a 3-vector [protein_kcal_frac, carbs_kcal_frac, fat_kcal_frac]
    normalised to sum to 1, or None if macros are missing/zero.
    """
    m = item.macros
    if m is None:
        return None
    p = m.protein_g * _PROTEIN_KCAL
    c = m.carbs_g * _CARBS_KCAL
    f = m.fat_g * _FAT_KCAL
    total = p + c + f
    if total <= 0:
        return None
    return np.array([p / total, c / total, f / total])


def _goal_macro_vector(period_goal: dict) -> np.ndarray:
    """
    Return the user's target macro ratio vector for a meal period.
    Falls back to a balanced default when goal data is absent.
    """
    p = (period_goal.get("protein_g", 0) or 0) * _PROTEIN_KCAL
    c = (period_goal.get("carbs_g", 0) or 0) * _CARBS_KCAL
    f = (period_goal.get("fat_g", 0) or 0) * _FAT_KCAL
    total = p + c + f
    if total <= 0:
        return np.array([0.30, 0.40, 0.30])  # sane default
    return np.array([p / total, c / total, f / total])


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom < 1e-9:
        return 0.0
    return float(np.dot(a, b) / denom)



def build_user_history(django_user_id: int) -> dict:
    """
    Summarise the user's recent meal-plan history into normalised preference
    dictionaries keyed by station and category.

    Returns
    -------
    {
        "station_prefs":  {station_name: frequency_0_to_1, ...},
        "category_prefs": {category_name: frequency_0_to_1, ...},
    }
    """
    try:
        from api.models import MealPlan

        plans = (
            MealPlan.objects(django_user_id=django_user_id)
            .order_by("-generated_at")
            .limit(_HISTORY_LOOKBACK)
        )

        station_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}

        for plan in plans:
            for meal in plan.meals or []:
                for item in meal.get("items") or []:
                    if station := item.get("station"):
                        station_counts[station] = station_counts.get(station, 0) + 1
                    if category := item.get("category"):
                        category_counts[category] = category_counts.get(category, 0) + 1

        total_s = sum(station_counts.values()) or 1
        total_c = sum(category_counts.values()) or 1

        return {
            "station_prefs": {k: v / total_s for k, v in station_counts.items()},
            "category_prefs": {k: v / total_c for k, v in category_counts.items()},
        }
    except Exception as exc:
        logger.warning("build_user_history failed for user %s: %s", django_user_id, exc)
        return {"station_prefs": {}, "category_prefs": {}}


def score_item(item, period_goal: dict, user_history: Optional[dict] = None) -> float:
    """
    Compute a personalised score for *item* given the period macro goal.

    Parameters
    ----------
    item         : MenuItem embedded document
    period_goal  : dict with keys calories, protein_g, carbs_g, fat_g
    user_history : output of build_user_history(), or None

    Returns
    -------
    float in [0, 1]  (higher = better fit for this user and period)
    """
    if not item.macros or item.macros.calories <= 0:
        return 0.0

    item_vec = _item_macro_vector(item)
    if item_vec is None:
        cosine_score = 0.0
    else:
        goal_vec = _goal_macro_vector(period_goal)
        cosine_score = _cosine(item_vec, goal_vec)

    expected_cal = (period_goal.get("calories") or 600) / 3.0
    item_cal = item.macros.calories
    # Smooth decay: score = 1 at perfect match
    ratio = abs(item_cal - expected_cal) / max(expected_cal, 1.0)
    calorie_fit = 1.0 / (1.0 + ratio)

    history_score = 0.0
    if user_history:
        station_prefs = user_history.get("station_prefs", {})
        category_prefs = user_history.get("category_prefs", {})
        if item.station and item.station in station_prefs:
            history_score += station_prefs[item.station]
        if item.category and item.category in category_prefs:
            history_score += category_prefs[item.category]
        # Normalise: max possible is 2.0 (top-ranked in both station + category)
        history_score = min(history_score / 2.0, 1.0)

    # Cornell Dining "healthy" badge — slight boost for users whose goals
    # lean toward lower fat / lower calorie targets
    healthy_bonus = 0.0
    if getattr(item, "healthy", False):
        # Boost only when user is in a calorie-conservative mode (< 2200 kcal/day goal)
        daily_cal = period_goal.get("calories", 600) / (
            list({"breakfast": 0.25, "lunch": 0.35, "dinner": 0.40}.values())[0]
        )
        if daily_cal < 2200:
            healthy_bonus = 0.05

    return min(
        _W_COSINE * cosine_score
        + _W_CALFIT * calorie_fit
        + _W_HISTORY * history_score
        + healthy_bonus,
        1.0,
    )
