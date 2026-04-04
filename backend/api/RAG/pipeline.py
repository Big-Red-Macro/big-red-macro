import os
import json
import logging
from typing import List
from datetime import date
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from api.models import UserProfile, DailyMenu

logger = logging.getLogger(__name__)

# Pydantic models for structured output
class MealSuggestion(BaseModel):
    meal_time: str = Field(description="The suggested time to eat, e.g., '12:15 PM'")
    dining_hall_name: str = Field(description="The name of the dining hall")
    suggested_items: List[str] = Field(description="List of specific menu items to eat")
    estimated_macros: dict = Field(description="Estimated macros with keys: calories, protein_g, carbs_g, fat_g")
    reasoning: str = Field(description="Why this time and meal was chosen based on the user's schedule and goals")

class DailyItinerary(BaseModel):
    itinerary_date: str = Field(description="The date of the itinerary")
    meals: List[MealSuggestion] = Field(description="Suggested meals for the day")
    daily_summary: str = Field(description="A brief summary or encouragement for the user's day")

def generate_rag_meal_plan(profile: UserProfile, gaps: List[dict], target_date: str) -> dict:
    """
    Generate an AI-powered meal plan using Gemini 1.5 Flash and LangChain.
    """
    # Force API key for this test
    user_key = os.getenv("GEMINI_API_KEY", "AIzaSyAGGVx9iXQG7SnrmBpUm7OPfhs_5ZqklHE")
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

    gaps_str = json.dumps(gaps, indent=2)

    # 3. Setup LangChain + Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI meal planning assistant for Cornell students. "
                   "You must provide a structured daily meal itinerary based on the user's schedule gaps, "
                   "their macro goals, their dietary restrictions and allergies, and the menus available at Cornell dining halls. "
                   "You must strictly adhere to the user's dietary restrictions (e.g. if they are vegan, ONLY select vegan items). "
                   "Try to incorporate their favorite foods if they are available on the menus today. "
                   "Return the result nicely formatted according to the required schema."),
        ("human", "User's Macro Goals: {macro_text}\n"
                  "User's Dietary Preferences & Needs:\n{preferences_str}\n\n"
                  "User's Free Time Blocks (gaps in schedule): {gaps_str}\n"
                  "Target Date: {target_date}\n\n"
                  "Available Menus Highlight:\n{context_str}\n\n"
                  "Plan exactly one meal for each major time block (e.g. Breakfast, Lunch, Dinner) "
                  "if the gaps align with typical meal times. Pick specific items from the menus "
                  "provided to hit the macro goals and satisfy dietary needs. Return the final structured output.")
    ])

    structured_llm = llm.with_structured_output(DailyItinerary)
    chain = prompt | structured_llm

    try:
        res: DailyItinerary = chain.invoke({
            "macro_text": macro_text,
            "preferences_str": preferences_str,
            "gaps_str": gaps_str,
            "target_date": target_date,
            "context_str": context_str
        })
        return res.dict()
    except Exception as e:
        logger.error(f"Failed to generate RAG meal plan: {e}")
        return {"error": str(e)}
