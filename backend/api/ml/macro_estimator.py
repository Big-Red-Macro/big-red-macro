"""
Macro estimator for Cornell Dining menu items.

The Cornell Dining API provides item names and a `healthy` flag but NO per-item
nutrition data.  This module fills that gap with category-informed priors that
represent typical Cornell dining portion sizes.

Architecture
------------
Stage 1 — category prior
  Each NLP category (protein, grain, vegetable, …) carries a baseline macro
  profile derived from USDA average serving sizes for that food group.

Stage 2 — station modifier
  The dining station (e.g. "Grill", "Salad Bar", "Chef's Table - Sides")
  adjusts the baseline via a multiplicative factor table.

Stage 3 — healthy flag discount
  When Cornell Dining marks an item as "healthy", calories are scaled down and
  protein density is scaled up, consistent with their stated healthy-item criteria
  (≤500 kcal, ≤35% fat, ≥10g protein for entrées).

These priors are deliberately conservative averages.  When real NetNutrition data
becomes available it should override these estimates rather than blend with them.
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MacroEstimate:
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float


# ---------------------------------------------------------------------------
# Category priors  (typical single-serving values for Cornell dining portions)
# ---------------------------------------------------------------------------

# Format: calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg
_CATEGORY_PRIORS: dict[str, MacroEstimate] = {
    "protein":    MacroEstimate(220, 26, 4,  10, 0,  480),  # ~4 oz cooked meat/fish/tofu
    "grain":      MacroEstimate(210,  6, 42,  3, 2,  220),  # ~1 cup cooked grain / 1 roll
    "vegetable":  MacroEstimate( 70,  3, 12,  2, 3,  160),  # ~¾ cup cooked vegetables
    "fruit":      MacroEstimate( 80,  1, 20,  0, 2,    5),  # ~1 medium piece / ½ cup
    "dairy":      MacroEstimate(140,  8,  8,  8, 0,  200),  # ~1½ oz cheese or ¾ cup yogurt
    "dessert":    MacroEstimate(280,  3, 40, 12, 1,  190),  # average baked dessert portion
    "beverage":   MacroEstimate( 50,  1, 11,  0, 0,   20),  # non-dairy, non-alcoholic 8 oz
    "condiment":  MacroEstimate( 60,  1,  6,  4, 1,  310),  # ~2 Tbsp sauce / dressing
    "mixed":      MacroEstimate(300, 12, 35, 12, 3,  520),  # composite entrée default
}

_DEFAULT_PRIOR = _CATEGORY_PRIORS["mixed"]


# ---------------------------------------------------------------------------
# Station modifiers  (multipliers applied to the category prior)
# Station names come from the Cornell API's menu category field.
# ---------------------------------------------------------------------------

@dataclass
class _StationMod:
    cal: float = 1.0
    pro: float = 1.0
    carb: float = 1.0
    fat: float = 1.0


_STATION_MODS: dict[str, _StationMod] = {
    # High-protein grill items tend to be larger servings
    "Grill":                _StationMod(cal=1.3, pro=1.5, carb=0.8, fat=1.2),
    # Soups are broth-diluted → lower macros
    "Soup":                 _StationMod(cal=0.6, pro=0.8, carb=0.7, fat=0.6),
    # Salad bar items are lower calorie
    "Salad":                _StationMod(cal=0.7, pro=0.8, carb=0.9, fat=0.7),
    # Sides are half-portion
    "Chef's Table - Sides": _StationMod(cal=0.6, pro=0.6, carb=0.7, fat=0.6),
    "Chef's Table":         _StationMod(cal=1.1, pro=1.2, carb=1.0, fat=1.0),
    # Desserts are already estimated as dessert category
    "Desserts":             _StationMod(cal=1.0, pro=1.0, carb=1.0, fat=1.0),
    # Beverages served at station
    "Beverage":             _StationMod(cal=0.8, pro=0.8, carb=0.8, fat=0.8),
    # Condiments
    "Condiments/Toppings":  _StationMod(cal=0.5, pro=0.5, carb=0.5, fat=0.6),
    # International / ethnic stations tend toward fuller entrées
    "International":        _StationMod(cal=1.1, pro=1.1, carb=1.1, fat=1.0),
    # Deli / sandwiches
    "Deli":                 _StationMod(cal=1.2, pro=1.3, carb=1.1, fat=1.1),
    "Sandwich":             _StationMod(cal=1.2, pro=1.3, carb=1.1, fat=1.1),
    # Pizza is calorie-dense
    "Pizza":                _StationMod(cal=1.4, pro=1.1, carb=1.4, fat=1.4),
    # Breakfast-specific
    "Breakfast":            _StationMod(cal=1.0, pro=1.0, carb=1.0, fat=1.0),
    "Bakery":               _StationMod(cal=1.1, pro=0.8, carb=1.3, fat=1.0),
}

# Healthy flag: Cornell's "healthy" badge targets ≤500 kcal, lower fat, higher protein ratio
_HEALTHY_SCALE = _StationMod(cal=0.75, pro=1.15, carb=0.85, fat=0.65)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def estimate(category: str, station: str = "", healthy: bool = False) -> MacroEstimate:
    """
    Return estimated macros for a menu item.

    Parameters
    ----------
    category : NLP category string from item_classifier (e.g. "protein", "grain")
    station  : Cornell Dining station/category string from the API (e.g. "Grill")
    healthy  : Cornell Dining healthy flag

    Returns
    -------
    MacroEstimate with float fields
    """
    prior = _CATEGORY_PRIORS.get(category, _DEFAULT_PRIOR)

    # Station modifier (exact match first, then substring search)
    mod = _STATION_MODS.get(station)
    if mod is None:
        for key, m in _STATION_MODS.items():
            if key.lower() in station.lower():
                mod = m
                break
    if mod is None:
        mod = _StationMod()

    cal = prior.calories * mod.cal
    pro = prior.protein_g * mod.pro
    carb = prior.carbs_g * mod.carb
    fat = prior.fat_g * mod.fat

    if healthy:
        cal *= _HEALTHY_SCALE.cal
        pro *= _HEALTHY_SCALE.pro
        carb *= _HEALTHY_SCALE.carb
        fat *= _HEALTHY_SCALE.fat

    return MacroEstimate(
        calories=round(cal, 1),
        protein_g=round(pro, 1),
        carbs_g=round(carb, 1),
        fat_g=round(fat, 1),
        fiber_g=prior.fiber_g,
        sodium_mg=round(prior.sodium_mg * mod.cal, 0),  # sodium roughly tracks calories
    )
