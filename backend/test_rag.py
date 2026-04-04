import os
import json
from dotenv import load_dotenv

load_dotenv(".env")
os.environ["PYTHONPATH"] = "."

# Mock the database to avoid needing Django or MongoDB for the test
class MockMacros:
    def __init__(self, calories, protein_g, carbs_g, fat_g):
        self.calories = calories
        self.protein_g = protein_g
        self.carbs_g = carbs_g
        self.fat_g = fat_g

class MockItem:
    def __init__(self, name, macros):
        self.name = name
        self.macros = macros

class MockHall:
    def __init__(self):
        self.name = "Becker House"

class MockMenu:
    def __init__(self):
        self.dining_hall = MockHall()
        self.meal_period = "lunch"
        self.items = [
            MockItem("Grilled Chicken Breast", MockMacros(220, 35, 1, 8)),
            MockItem("Steamed Broccoli", MockMacros(50, 3, 10, 1)),
            MockItem("Pasta with Sauce", MockMacros(450, 12, 60, 10))
        ]

class MockProfile:
    def __init__(self):
        self.macro_goals = MockMacros(600, 40, 40, 20)

# Inject mocks before we import the pipeline
import sys
from unittest.mock import MagicMock
api_models = MagicMock()
api_models.UserProfile = MockProfile
api_models.DailyMenu = MagicMock()
api_models.DailyMenu.objects = MagicMock(return_value=[MockMenu()])
api_models.DiningHall = MagicMock()
sys.modules['api.models'] = api_models

# Now import the pipeline so it uses our mocked components
from api.RAG.pipeline import generate_rag_meal_plan

def run_test():
    profile = MockProfile()
    gaps = [{"start": "12:15", "end": "13:30", "duration_minutes": 75}]
    
    print("\n[Input] Provided schedule gaps to AI:")
    print(json.dumps(gaps, indent=2))
    print("\n[Running] generating RAG meal plan using gemini-1.5-flash with environment API Key...\n")
    
    try:
        result = generate_rag_meal_plan(profile, gaps, "2026-04-05")
        print("=== AI Pipeline Output ===")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error executing RAG: {e}")

if __name__ == "__main__":
    run_test()
