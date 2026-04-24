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

# Pydantic models for structured output: Need to work on this, its a bit cooked
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

class ChatbotResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question")

def generate_rag_meal_plan(profile: UserProfile, target_date: str):
    """
    Generate an AI-powered meal plan using Gemini (1.5 Flash) and LangChain.
    """
    # Load API key from environment (set in .env)
    user_key = os.getenv("GEMINI_API_KEY")
    if not user_key:
        raise ValueError("GEMINI_API_KEY is not set. Add it to your .env file.")
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
                hours = m.dining_hall.operating_hours if m.dining_hall.operating_hours else {}
                hours_str = json.dumps(hours)
                menu_context.append(f"### {hall_name} ({period}) - Operating Hours: {hours_str}\n{items_str}")
    
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

    # LangChain + Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI meal planning assistant for Cornell students. "
                   "You must provide a structured daily meal itinerary based on the user's macro goals, "
                   "their dietary restrictions and allergies, their favorite foods, and the menus available at Cornell dining halls. "
                   "You must strictly adhere to the user's dietary restrictions (e.g. if they are vegan, ONLY select vegan items). "
                   "Try to incorporate their favorite foods if they are available on the menus today. "
                   "Ensure you only suggest eating at a dining hall when it is open based on the Operating Hours provided. "
                   "Return the result nicely formatted according to the required schema."),
        ("human", "User's Macro Goals: {macro_text}\n"
                  "User's Dietary Preferences & Needs:\n{preferences_str}\n\n"
                  "Target Date: {target_date}\n\n"
                  "Available Menus and Operating Hours Highlight:\n{context_str}\n\n"
                  "Plan exactly one meal for each major time block (e.g. Breakfast, Lunch, Dinner). "
                  "Pick specific items from the menus "
                  "provided to hit the macro goals and satisfy dietary needs. Return the final structured output.")
    ])

    structured_llm = llm.with_structured_output(DailyItinerary)
    chain = prompt | structured_llm

    try:
        res: DailyItinerary = chain.invoke({
            "macro_text": macro_text,
            "preferences_str": preferences_str,
            "target_date": target_date,
            "context_str": context_str
        })
        return res.model_dump() if hasattr(res, "model_dump") else res.dict()
    except Exception as e:
        logger.error(f"Failed to generate RAG meal plan: {e}")
        return {"error": str(e)}

def chatbot_query(question: str, target_date: str):
    """
    Handle general dining hall queries using Langchain and Gemini.
    """
    user_key = os.getenv("GEMINI_API_KEY")
    if not user_key:
        return {"answer": "GEMINI_API_KEY is not set. Add it to your .env file."}
    os.environ["GOOGLE_API_KEY"] = user_key
    
    menus = DailyMenu.objects(date=target_date)
    from api.models import DiningHall
    halls = DiningHall.objects.all()
    
    context_lines = []
    context_lines.append("### Dining Halls Operating Hours & General Info ###")
    for h in halls:
        hours_str = json.dumps(h.operating_hours) if h.operating_hours else "Unknown"
        context_lines.append(f"- {h.name} ({h.short_name}): {hours_str}")
        
    context_lines.append("\n### Today's Menus Highlight ###")
    for m in menus:
        if m.dining_hall and m.items:
            items_str = ", ".join([item.name for item in m.items[:15]])
            context_lines.append(f"{m.dining_hall.name} ({m.meal_period}): {items_str}")
            
    context_str = "\n".join(context_lines)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.4,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful Cornell Dining chatbot. "
                   "You answer questions from students regarding dining halls, "
                   "their operating hours, and today's menus based strictly on the provided context. "
                   "If the information is not in the context, say you don't know."),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    
    structured_llm = llm.with_structured_output(ChatbotResponse)
    chain = prompt | structured_llm
    
    try:
        res: ChatbotResponse = chain.invoke({
            "context": context_str,
            "question": question
        })
        return res.model_dump() if hasattr(res, "model_dump") else res.dict()
    except Exception as e:
        logger.error(f"Failed to answer chatbot query: {e}")
        return {"answer": f"Error: {str(e)}"}

