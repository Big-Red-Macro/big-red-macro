import os
import json
import logging
from typing import List
from datetime import date, datetime
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from api.models import UserProfile, DailyMenu, DiningHall

logger = logging.getLogger(__name__)

# Pydantic models for structured output
class MealSuggestion(BaseModel):
    meal_time: str = Field(description="The suggested time to eat, e.g., '12:15 PM'")
    meal_period: str = Field(description="Breakfast, Lunch, Dinner, or Brunch")
    dining_hall_name: str = Field(description="The name of the dining hall")
    suggested_items: List[str] = Field(description="List of specific menu items to eat")
    estimated_macros: dict = Field(description="Estimated macros with keys: calories, protein_g, carbs_g, fat_g")
    reasoning: str = Field(description="Why this time and meal was chosen based on the user's schedule and goals")

class DailyItinerary(BaseModel):
    itinerary_date: str = Field(description="The date of the itinerary")
    meals: List[MealSuggestion] = Field(description="Suggested meals for the day")
    daily_summary: str = Field(description="A brief summary or encouragement for the user's day")

PERIOD_LABELS = {
    "breakfast": "Breakfast",
    "brunch": "Brunch",
    "lunch": "Lunch",
    "dinner": "Dinner",
}

AREA_DEFAULT_HALLS = {
    "Central": {
        "breakfast": "Trillium",
        "brunch": "Okenshields",
        "lunch": "Okenshields",
        "dinner": "Okenshields",
    },
    "North": {
        "breakfast": "North Star Dining Room",
        "brunch": "Robert Purcell Marketplace Eatery",
        "lunch": "North Star Dining Room",
        "dinner": "Robert Purcell Marketplace Eatery",
    },
    "West": {
        "breakfast": "Becker House Dining Room",
        "brunch": "Becker House Dining Room",
        "lunch": "Becker House Dining Room",
        "dinner": "Becker House Dining Room",
    },
}

GENERIC_HALL_NAMES = {
    "cornell dining hall",
    "cornell dining halls",
    "cornell dining",
    "dining hall",
    "campus dining",
}

PERIOD_FALLBACK_TIMES = {
    "breakfast": "8:30 AM",
    "brunch": "11:00 AM",
    "lunch": "12:30 PM",
    "dinner": "6:15 PM",
}

GENERIC_PERIOD_PLANS = {
    "breakfast": {
        "dining_hall_name": "Morrison Dining",
        "items": ["Eggs or tofu scramble", "Oatmeal with fruit", "Greek yogurt", "Coffee or water"],
        "macros": {"calories": 620, "protein_g": 38, "carbs_g": 72, "fat_g": 18},
    },
    "lunch": {
        "dining_hall_name": "Okenshields",
        "items": ["Lean protein entree", "Rice or roasted potatoes", "Mixed vegetables", "Side salad"],
        "macros": {"calories": 760, "protein_g": 48, "carbs_g": 88, "fat_g": 22},
    },
    "dinner": {
        "dining_hall_name": "Becker House Dining Room",
        "items": ["Grilled protein option", "Whole-grain or pasta side", "Vegetable side", "Fruit"],
        "macros": {"calories": 820, "protein_g": 52, "carbs_g": 92, "fat_g": 26},
    },
}


def _macro_dict(macros) -> dict:
    if not macros:
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
    return {
        "calories": round(macros.calories or 0),
        "protein_g": round(macros.protein_g or 0, 1),
        "carbs_g": round(macros.carbs_g or 0, 1),
        "fat_g": round(macros.fat_g or 0, 1),
    }


def _sum_macros(items: list) -> dict:
    total = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
    for item in items:
        macros = _macro_dict(getattr(item, "macros", None))
        for key in total:
            total[key] += macros[key]
    return {key: round(value, 1) for key, value in total.items()}


def _item_allowed(item, profile: UserProfile) -> bool:
    allergens = {a.lower() for a in (profile.allergens or [])}
    item_allergens = {a.lower() for a in (item.allergens or [])}
    if allergens & item_allergens:
        return False

    restrictions = {r.lower() for r in (profile.dietary_restrictions or [])}
    if "vegan" in restrictions and not item.is_vegan:
        return False
    if "vegetarian" in restrictions and not item.is_vegetarian:
        return False
    if "halal" in restrictions and not item.is_halal:
        return False
    if "gluten_free" in restrictions and not item.is_gluten_free:
        return False
    return True


def _item_score(item, favorites: set) -> float:
    macros = _macro_dict(getattr(item, "macros", None))
    score = macros["protein_g"] * 4 + macros["calories"] / 120
    if getattr(item, "healthy", False):
        score += 8
    if item.name.lower() in favorites:
        score += 30
    return score


def _period_for_gap(gap: dict) -> str:
    start = str(gap.get("start", "12:00"))[:5]
    try:
        hour = int(start.split(":")[0])
    except (TypeError, ValueError):
        return "lunch"
    if hour < 11:
        return "breakfast"
    if hour < 15:
        return "lunch"
    return "dinner"


def _format_gap_time(gap: dict, period: str) -> str:
    raw_start = gap.get("start")
    if not raw_start:
        return PERIOD_FALLBACK_TIMES.get(period, "12:00 PM")
    try:
        return datetime.strptime(str(raw_start)[:5], "%H:%M").strftime("%-I:%M %p")
    except ValueError:
        return PERIOD_FALLBACK_TIMES.get(period, "12:00 PM")


def _periods_from_gaps(gaps: List[dict]) -> list:
    periods = []
    for gap in gaps or []:
        period = _period_for_gap(gap)
        if period not in periods:
            periods.append(period)
    for period in ["breakfast", "lunch", "dinner"]:
        if period not in periods:
            periods.append(period)
    return periods[:3]


def _preferred_area(gap: dict) -> str:
    return gap.get("predicted_area") or "Central"


def _default_hall_for_gap(period: str, gap: dict) -> str:
    area = _preferred_area(gap)
    return AREA_DEFAULT_HALLS.get(area, AREA_DEFAULT_HALLS["Central"]).get(
        period,
        AREA_DEFAULT_HALLS.get(area, AREA_DEFAULT_HALLS["Central"])["lunch"],
    )


def _hall_directory() -> str:
    halls = DiningHall.objects.order_by("campus_area", "name")
    lines = []
    for hall in halls:
        periods = ", ".join(sorted((hall.operating_hours or {}).keys())) or "unknown periods"
        lines.append(f"- {hall.name} ({hall.campus_area or 'Unknown'} Campus; {periods})")
    if not lines:
        return (
            "- Okenshields (Central Campus; breakfast, lunch, dinner)\n"
            "- North Star Dining Room (North Campus; breakfast, lunch, dinner)\n"
            "- Robert Purcell Marketplace Eatery (North Campus; breakfast, lunch, dinner)\n"
            "- Becker House Dining Room (West Campus; breakfast, lunch, dinner)\n"
            "- Trillium (Central Campus; breakfast, lunch)"
        )
    return "\n".join(lines)


def _valid_hall_names() -> set:
    names = {hall.name for hall in DiningHall.objects.only("name")}
    if not names:
        names = {
            "Okenshields",
            "North Star Dining Room",
            "Robert Purcell Marketplace Eatery",
            "Becker House Dining Room",
            "Trillium",
        }
    return names


def _menus_for_period(target_date: str, period: str) -> tuple[list, str]:
    periods_to_try = [period]
    if period == "breakfast":
        periods_to_try.append("brunch")

    for period_name in periods_to_try:
        menus = list(DailyMenu.objects(date=target_date, meal_period=period_name))
        if menus:
            return menus, target_date

    for period_name in periods_to_try:
        latest_menu = DailyMenu.objects(meal_period=period_name).order_by("-date").first()
        if latest_menu:
            menus = list(DailyMenu.objects(date=latest_menu.date, meal_period=period_name))
            return menus, latest_menu.date

    latest_menu = DailyMenu.objects.order_by("-date").first()
    if latest_menu:
        menus = list(DailyMenu.objects(date=latest_menu.date))
        return menus, latest_menu.date

    return [], target_date


def _generic_meal(period: str, gap: dict) -> dict:
    plan = GENERIC_PERIOD_PLANS.get(period, GENERIC_PERIOD_PLANS["lunch"])
    hall_name = _default_hall_for_gap(period, gap)
    schedule_window = ""
    if gap.get("start") and gap.get("end"):
        schedule_window = f" during your {gap['start']}-{gap['end']} free block"
    area_text = f" near {_preferred_area(gap)} Campus"

    return {
        "meal_time": _format_gap_time(gap, period),
        "meal_period": PERIOD_LABELS.get(period, period.title()),
        "dining_hall_name": hall_name or plan["dining_hall_name"],
        "suggested_items": plan["items"],
        "estimated_macros": plan["macros"],
        "reasoning": (
            f"This is a balanced Cornell dining stop{area_text}{schedule_window}. "
            "It prioritizes a protein source, steady carbs, produce, and enough calories to carry you to the next meal."
        ),
    }


def _fallback_itinerary(profile: UserProfile, gaps: List[dict], target_date: str, note: str = "") -> dict:
    favorites = {item.lower() for item in (profile.favorite_meals or [])}
    meals = []
    menu_dates_used = set()

    for period in _periods_from_gaps(gaps):
        gap = next((g for g in (gaps or []) if _period_for_gap(g) == period), {})
        period_menus, menu_date = _menus_for_period(target_date, period)
        if not period_menus:
            meals.append(_generic_meal(period, gap))
            continue
        menu_dates_used.add(menu_date)

        best_menu = None
        best_items = []
        preferred_area = _preferred_area(gap).lower()
        ranked_menus = sorted(
            period_menus,
            key=lambda menu: 0 if (menu.dining_hall and (menu.dining_hall.campus_area or "").lower() == preferred_area) else 1,
        )
        for menu in ranked_menus:
            candidates = [
                item for item in (menu.items or [])
                if _item_allowed(item, profile)
            ]
            candidates_with_macros = [item for item in candidates if item.macros]
            if candidates_with_macros:
                candidates = candidates_with_macros
            candidates = sorted(candidates, key=lambda item: _item_score(item, favorites), reverse=True)
            selected = candidates[:4]
            if len(selected) > len(best_items):
                best_menu = menu
                best_items = selected

        if not best_menu or not best_items:
            meals.append(_generic_meal(period, gap))
            continue

        schedule_window = ""
        if gap.get("start") and gap.get("end"):
            schedule_window = f" during your {gap['start']}-{gap['end']} free block"

        hall_name = best_menu.dining_hall.name if best_menu.dining_hall else "Cornell Dining"
        meals.append({
            "meal_time": _format_gap_time(gap, period),
            "meal_period": PERIOD_LABELS.get(period, period.title()),
            "dining_hall_name": hall_name,
            "suggested_items": [item.name for item in best_items],
            "estimated_macros": _sum_macros(best_items),
            "reasoning": (
                f"{hall_name} is a strong {PERIOD_LABELS.get(period, period)} choice near "
                f"{_preferred_area(gap)} Campus{schedule_window}, with a protein-forward mix that respects your saved preferences."
            ),
        })

    if any(gap.get("source") == "fallback" for gap in (gaps or [])):
        summary = "Built from today's Cornell Dining menus using default meal windows because Google Calendar events could not be read."
    else:
        summary = "Built from your free calendar blocks and today's Cornell Dining menus."
    if menu_dates_used and (menu_dates_used != {target_date}):
        latest_date = sorted(menu_dates_used)[-1]
        summary = f"Built from default meal windows and the latest cached Cornell Dining menus ({latest_date})."
    if not menu_dates_used:
        summary = "Built from default meal windows and balanced Cornell dining recommendations."
    if note:
        summary += " AI planning was unavailable, so this itinerary uses the local fallback planner."

    return {
        "itinerary_date": target_date,
        "meals": meals,
        "daily_summary": summary,
    }


def _normalize_ai_itinerary(plan: dict, gaps: List[dict]) -> dict:
    valid_halls = _valid_hall_names()
    meals = plan.get("meals") or []
    for index, meal in enumerate(meals):
        gap = gaps[index] if index < len(gaps or []) else {}
        period = (meal.get("meal_period") or _period_for_gap(gap)).lower()
        if period not in PERIOD_LABELS:
            period = _period_for_gap(gap)

        hall_name = (meal.get("dining_hall_name") or "").strip()
        if hall_name.lower() in GENERIC_HALL_NAMES or hall_name not in valid_halls:
            meal["dining_hall_name"] = _default_hall_for_gap(period, gap)

        meal["meal_period"] = PERIOD_LABELS.get(period, period.title())
        if not meal.get("reasoning"):
            meal["reasoning"] = (
                f"Chosen near {_preferred_area(gap)} Campus based on your schedule location "
                "and the meal window."
            )
    plan["meals"] = meals
    return plan


def generate_rag_meal_plan(profile: UserProfile, gaps: List[dict], target_date: str) -> dict:
    """
    Generate an AI-powered meal plan using Gemini 1.5 Flash and LangChain.
    """
    # Load API key from environment (set in .env)
    user_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not user_key:
        return _fallback_itinerary(
            profile,
            gaps,
            target_date,
            "GOOGLE_API_KEY/GEMINI_API_KEY is not set.",
        )
    os.environ["GOOGLE_API_KEY"] = user_key
    
    menus = DailyMenu.objects(date=target_date)
    menu_context = []
    
    for m in menus:
        if m.dining_hall and m.items:
            hall_name = m.dining_hall.name
            period = m.meal_period
            
            items_str = ""
            for item in m.items[:15]: 
                if item.macros:
                    items_str += f" - {item.name}: {item.macros.calories}kcal, {item.macros.protein_g}g protein\n"
            
            if items_str:
                menu_context.append(f"### {hall_name} ({period})\n{items_str}")
    
    context_str = "\n".join(menu_context)
    if not context_str:
        context_str = "No specific menu data available for this date."

    macros = profile.macro_goals
    if macros:
        macro_text = f"Calories: {macros.calories}, Protein: {macros.protein_g}g, Carbs: {macros.carbs_g}g, Fat: {macros.fat_g}g"
    else:
        macro_text = "Balanced diet, ~2000 calories"

    preferences_str = ""
    if profile.dietary_restrictions:
        preferences_str += f"- Dietary Restrictions: {', '.join(profile.dietary_restrictions)}\n"
    if profile.allergens:
        preferences_str += f"- Allergens to avoid: {', '.join(profile.allergens)}\n"
    if profile.favorite_meals:
        preferences_str += f"- Favorite foods to prioritize: {', '.join(profile.favorite_meals)}\n"
    if not preferences_str:
        preferences_str = "No specific dietary restrictions or favorites."

    body_str = ""
    if getattr(profile, 'height_cm', None) and getattr(profile, 'weight_kg', None):
        total_inches = profile.height_cm / 2.54
        feet = int(total_inches // 12)
        inches = round(total_inches % 12)
        lbs = round(profile.weight_kg / 0.453592)
        body_str += f"- Height: {feet}'{inches}\", Weight: {lbs} lbs"
        if getattr(profile, 'age', None):
            body_str += f", Age: {profile.age}"
        if getattr(profile, 'sex', None):
            body_str += f", Sex: {profile.sex}"
        body_str += "\n"
    if getattr(profile, 'activity_level', None):
        body_str += f"- Activity Level: {profile.activity_level}\n"
    if getattr(profile, 'fitness_goal', None):
        body_str += f"- Fitness Goal: {profile.fitness_goal}\n"
    if not body_str:
        body_str = "No body metrics provided."

    gaps_str = json.dumps(gaps, indent=2)
    hall_directory = _hall_directory()

    # LangChain + Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI meal planning assistant for Cornell students. "
                   "You must provide a structured daily meal itinerary based on the user's schedule gaps, "
                   "their macro goals, their dietary restrictions and allergies, and the menus available at Cornell dining halls. "
                   "Choose a specific Cornell dining location from the provided dining hall directory. "
                   "Never use generic names like 'Cornell Dining Hall' or 'campus dining'. "
                   "Use each gap's predicted_area, previous_location, and next_location to pick a nearby hall. "
                   "You must strictly adhere to the user's dietary restrictions (e.g. if they are vegan, ONLY select vegan items). "
                   "Try to incorporate their favorite foods if they are available on the menus today. "
                   "Return the result nicely formatted according to the required schema."),
        ("human", "User's Body Metrics & Physical Profile:\n{body_str}\n\n"
                  "User's Macro Goals: {macro_text}\n"
                  "User's Dietary Preferences & Needs:\n{preferences_str}\n\n"
                  "User's Free Time Blocks (gaps in schedule): {gaps_str}\n"
                  "Target Date: {target_date}\n\n"
                  "Dining Hall Directory:\n{hall_directory}\n\n"
                  "Available Menus Highlight:\n{context_str}\n\n"
                  "Plan exactly one meal for each major time block (e.g. Breakfast, Lunch, Dinner) "
                  "if the gaps align with typical meal times. Pick specific items from the menus "
                  "provided to hit the macro goals and satisfy dietary needs. Consider the user's fitness goal "
                  "and body metrics when selecting portion sizes and macronutrient balance. "
                  "Return the final structured output.")
    ])

    structured_llm = llm.with_structured_output(DailyItinerary)
    chain = prompt | structured_llm

    try:
        res: DailyItinerary = chain.invoke({
            "body_str": body_str,
            "macro_text": macro_text,
            "preferences_str": preferences_str,
            "gaps_str": gaps_str,
            "target_date": target_date,
            "hall_directory": hall_directory,
            "context_str": context_str
        })
        return _normalize_ai_itinerary(res.model_dump(), gaps)
    except Exception as e:
        logger.error(f"Failed to generate RAG meal plan: {e}")
        return _fallback_itinerary(profile, gaps, target_date, str(e))
