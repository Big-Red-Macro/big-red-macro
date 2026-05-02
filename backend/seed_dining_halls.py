"""
Seed Cornell dining halls into MongoDB with known data.
Run: DJANGO_SETTINGS_MODULE=bigredmacro.settings python seed_dining_halls.py
"""
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bigredmacro.settings")
django.setup()

from api.models import DiningHall, DailyMenu, MenuItem, Macros
from datetime import date, datetime, timezone
import random

HALLS = [
    {
        "name": "Okenshields",
        "short_name": "okenshields",
        "location_lat": 42.4490,
        "location_lng": -76.4837,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "Central",
        "operating_hours": {"breakfast": "7:30am–10:00am", "lunch": "11:00am–2:00pm", "dinner": "5:00pm–7:30pm"},
    },
    {
        "name": "North Star Dining Room",
        "short_name": "northstar",
        "location_lat": 42.4532,
        "location_lng": -76.4804,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "North",
        "operating_hours": {"breakfast": "7:00am–10:30am", "lunch": "11:00am–2:30pm", "dinner": "5:00pm–8:00pm"},
    },
    {
        "name": "Robert Purcell Marketplace Eatery",
        "short_name": "rpme",
        "location_lat": 42.4560,
        "location_lng": -76.4780,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "North",
        "operating_hours": {"breakfast": "7:00am–10:30am", "lunch": "11:00am–2:30pm", "dinner": "5:00pm–8:30pm"},
    },
    {
        "name": "Risley Dining Room",
        "short_name": "risley",
        "location_lat": 42.4541,
        "location_lng": -76.4843,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "North",
        "operating_hours": {"dinner": "5:00pm–8:00pm"},
    },
    {
        "name": "104West!",
        "short_name": "104west",
        "location_lat": 42.4469,
        "location_lng": -76.4877,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "West",
        "operating_hours": {"lunch": "11:30am–2:00pm", "dinner": "5:00pm–8:00pm"},
    },
    {
        "name": "Becker House Dining Room",
        "short_name": "becker",
        "location_lat": 42.4474,
        "location_lng": -76.4890,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "West",
        "operating_hours": {"breakfast": "7:30am–10:00am", "lunch": "11:30am–2:00pm", "dinner": "5:00pm–8:00pm"},
    },
    {
        "name": "Jansen's Dining Room at Bethe House",
        "short_name": "jansens",
        "location_lat": 42.4478,
        "location_lng": -76.4883,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "West",
        "operating_hours": {"dinner": "5:00pm–8:00pm"},
    },
    {
        "name": "Keeton House Dining Room",
        "short_name": "keeton",
        "location_lat": 42.4472,
        "location_lng": -76.4895,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "West",
        "operating_hours": {"dinner": "5:00pm–8:00pm"},
    },
    {
        "name": "Rose House Dining Room",
        "short_name": "rose",
        "location_lat": 42.4480,
        "location_lng": -76.4888,
        "dining_type": "residential",
        "accepts_brbs": True,
        "accepts_meal_swipe": True,
        "supports_get_app": False,
        "campus_area": "West",
        "operating_hours": {"dinner": "5:00pm–8:00pm"},
    },
    {
        "name": "Morrison Dining",
        "short_name": "morrison",
        "location_lat": 42.4465,
        "location_lng": -76.4862,
        "dining_type": "cafe",
        "accepts_brbs": True,
        "accepts_meal_swipe": False,
        "supports_get_app": True,
        "campus_area": "West",
        "operating_hours": {"lunch": "11:00am–2:30pm"},
    },
    {
        "name": "Cafe Jennie",
        "short_name": "cafejennie",
        "location_lat": 42.4468,
        "location_lng": -76.4870,
        "dining_type": "cafe",
        "accepts_brbs": True,
        "accepts_meal_swipe": False,
        "supports_get_app": True,
        "campus_area": "West",
        "operating_hours": {"breakfast": "8:00am–11:00am", "lunch": "11:00am–4:00pm"},
    },
    {
        "name": "Terrace Restaurant",
        "short_name": "terrace",
        "location_lat": 42.4503,
        "location_lng": -76.4822,
        "dining_type": "cafe",
        "accepts_brbs": True,
        "accepts_meal_swipe": False,
        "supports_get_app": False,
        "campus_area": "Central",
        "operating_hours": {"lunch": "11:30am–1:30pm"},
    },
    {
        "name": "Trillium",
        "short_name": "trillium",
        "location_lat": 42.4488,
        "location_lng": -76.4810,
        "dining_type": "cafe",
        "accepts_brbs": True,
        "accepts_meal_swipe": False,
        "supports_get_app": True,
        "campus_area": "Central",
        "operating_hours": {"breakfast": "7:30am–11:00am", "lunch": "11:00am–4:00pm"},
    },
    {
        "name": "Martha's Cafe",
        "short_name": "marthas",
        "location_lat": 42.4470,
        "location_lng": -76.4815,
        "dining_type": "cafe",
        "accepts_brbs": True,
        "accepts_meal_swipe": False,
        "supports_get_app": True,
        "campus_area": "Central",
        "operating_hours": {"breakfast": "7:30am–11:00am", "lunch": "11:00am–3:00pm"},
    },
    {
        "name": "Amit Bhatia Libe Cafe",
        "short_name": "libecafe",
        "location_lat": 42.4479,
        "location_lng": -76.4842,
        "dining_type": "cafe",
        "accepts_brbs": True,
        "accepts_meal_swipe": False,
        "supports_get_app": True,
        "campus_area": "Central",
        "operating_hours": {"breakfast": "8:00am–11:00am", "lunch": "11:00am–4:00pm"},
    },
    {
        "name": "Mac's Cafe",
        "short_name": "macs",
        "location_lat": 42.4445,
        "location_lng": -76.4820,
        "dining_type": "cafe",
        "accepts_brbs": True,
        "accepts_meal_swipe": False,
        "supports_get_app": False,
        "campus_area": "Central",
        "operating_hours": {"breakfast": "7:30am–11:00am", "lunch": "11:00am–3:00pm"},
    },
]


# Sample menu items for residential dining halls
BREAKFAST_ITEMS = [
    ("Scrambled Eggs", "Grill", 220, 14, 2, 17, False, False),
    ("Turkey Bacon", "Grill", 120, 10, 1, 8, False, False),
    ("Buttermilk Pancakes", "Grill", 350, 8, 52, 12, True, False),
    ("Fresh Fruit Bowl", "Salad Bar", 95, 1, 24, 0, True, True),
    ("Greek Yogurt Parfait", "Salad Bar", 180, 12, 28, 3, True, False),
    ("Oatmeal", "Hot Cereal", 160, 6, 28, 3, True, True),
    ("Hash Browns", "Grill", 210, 2, 26, 11, True, True),
    ("Whole Wheat Toast", "Bakery", 130, 5, 22, 2, True, True),
    ("Veggie Egg White Omelette", "Grill", 150, 18, 4, 7, True, False),
    ("Breakfast Burrito", "International", 420, 18, 38, 22, False, False),
]

LUNCH_ITEMS = [
    ("Grilled Chicken Breast", "Grill", 280, 42, 0, 12, False, False),
    ("Caesar Salad", "Salad Bar", 190, 8, 12, 14, True, False),
    ("Black Bean Burger", "Grill", 340, 16, 42, 12, True, True),
    ("Pasta Marinara", "International", 380, 12, 62, 8, True, True),
    ("Teriyaki Tofu Stir Fry", "International", 290, 18, 32, 10, True, True),
    ("Turkey Club Wrap", "Deli", 420, 28, 36, 18, False, False),
    ("Tomato Basil Soup", "Soup", 150, 4, 22, 6, True, True),
    ("Brown Rice Bowl", "International", 310, 8, 58, 6, True, True),
    ("Grilled Salmon", "Grill", 360, 38, 0, 22, False, False),
    ("Mediterranean Quinoa Bowl", "Salad Bar", 340, 14, 44, 12, True, True),
    ("BBQ Pulled Pork Sandwich", "Grill", 480, 32, 38, 20, False, False),
    ("Garden Vegetable Pizza", "Pizza", 320, 14, 36, 14, True, False),
]

DINNER_ITEMS = [
    ("Herb Roasted Chicken", "Entree", 380, 44, 4, 20, False, False),
    ("Baked Ziti", "Pasta", 420, 18, 52, 16, True, False),
    ("Pan-Seared Tilapia", "Entree", 260, 36, 2, 12, False, False),
    ("Vegetable Curry", "International", 310, 10, 42, 12, True, True),
    ("Beef Stir Fry", "International", 440, 34, 28, 22, False, False),
    ("Mushroom Risotto", "Entree", 360, 8, 48, 14, True, False),
    ("Roasted Sweet Potatoes", "Sides", 180, 3, 38, 2, True, True),
    ("Steamed Broccoli", "Sides", 55, 4, 10, 1, True, True),
    ("Garlic Bread", "Bakery", 190, 4, 24, 8, True, False),
    ("Chocolate Lava Cake", "Dessert", 380, 5, 48, 20, True, False),
    ("Grilled Steak", "Grill", 490, 48, 0, 32, False, False),
    ("Spinach Artichoke Dip", "Appetizer", 220, 6, 14, 16, True, False),
]

def make_item(data):
    name, station, cal, prot, carbs, fat, veg, vegan = data
    return MenuItem(
        name=name,
        station=station,
        macros=Macros(calories=cal, protein_g=prot, carbs_g=carbs, fat_g=fat, fiber_g=random.randint(1, 6), sodium_mg=random.randint(200, 800)),
        is_vegetarian=veg,
        is_vegan=vegan,
        is_halal=random.random() > 0.7,
        is_gluten_free=random.random() > 0.8,
        allergens=[],
        healthy=cal < 300,
    )

def seed():
    today = date.today().isoformat()
    
    for hall_data in HALLS:
        hall = DiningHall.objects(name=hall_data["name"]).first()
        if hall:
            action = "Exists"
        else:
            hall = DiningHall(**hall_data)
            hall.save()
            action = "Created"
        print(f"  {action}: {hall.name} ({hall.campus_area})")
        
        # Seed menus for residential dining halls
        if hall.dining_type == "residential":
            hours = hall_data.get("operating_hours", {})
            
            if "breakfast" in hours:
                items = [make_item(d) for d in random.sample(BREAKFAST_ITEMS, min(7, len(BREAKFAST_ITEMS)))]
                DailyMenu.objects(dining_hall=hall, date=today, meal_period="breakfast").update_one(
                    set__items=items, set__source="seed_demo", set__fetched_at=datetime.now(timezone.utc), upsert=True
                )
            
            if "lunch" in hours:
                items = [make_item(d) for d in random.sample(LUNCH_ITEMS, min(9, len(LUNCH_ITEMS)))]
                DailyMenu.objects(dining_hall=hall, date=today, meal_period="lunch").update_one(
                    set__items=items, set__source="seed_demo", set__fetched_at=datetime.now(timezone.utc), upsert=True
                )
            
            if "dinner" in hours:
                items = [make_item(d) for d in random.sample(DINNER_ITEMS, min(9, len(DINNER_ITEMS)))]
                DailyMenu.objects(dining_hall=hall, date=today, meal_period="dinner").update_one(
                    set__items=items, set__source="seed_demo", set__fetched_at=datetime.now(timezone.utc), upsert=True
                )
        
        # Cafes get lunch items
        elif hall.dining_type == "cafe":
            items = [make_item(d) for d in random.sample(LUNCH_ITEMS, min(6, len(LUNCH_ITEMS)))]
            DailyMenu.objects(dining_hall=hall, date=today, meal_period="lunch").update_one(
                set__items=items, set__source="seed_demo", set__fetched_at=datetime.now(timezone.utc), upsert=True
            )

    print(f"\nDone! {DiningHall.objects.count()} halls, {DailyMenu.objects.count()} menu periods seeded.")

if __name__ == "__main__":
    seed()
