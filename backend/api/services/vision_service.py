import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def identify_food_from_image(base64_image: str) -> str:
    """
    Uses Google Gemini Vision to identify the food in the given base64 image.
    Returns a short description of the food item.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Unknown Food (API Key missing)"

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    
    msg = HumanMessage(
        content=[
            {"type": "text", "text": "What food item is in this image? Provide a brief, concise description outlining the main components (e.g., 'Grilled chicken salad with tomatoes'). Only reply with the description, no conversational text."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    
    try:
        response = llm.invoke([msg])
        return response.content.strip()
    except Exception as e:
        return f"Error identifying food: {str(e)}"
