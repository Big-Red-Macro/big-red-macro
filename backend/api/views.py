from datetime import date

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.cache import cache

from api.models import DailyMenu, DiningHall, UserProfile, WaitTimeSample
from api.serializers import (
    DiningHallSerializer,
    MealPlanSerializer,
    MenuItemSerializer,
    UserProfileSerializer,
    WaitTimeSerializer,
)
from api.services.dining_api import CornellDiningClient
from api.services.meal_planner import MealPlannerService
from api.services.wait_time import WaitTimeService
from api.RAG.pipeline import generate_rag_meal_plan, chatbot_query




@api_view(["GET"])
@permission_classes([AllowAny])
def dining_halls(request):
    """List all Cornell dining halls."""
    halls = DiningHall.objects.all()
    return Response(DiningHallSerializer(halls, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def dining_hall_menu(request, hall_id: str):
    """Get today's (or a specific date's) menu for a dining hall."""
    target_date = request.query_params.get("date", date.today().isoformat())
    period = request.query_params.get("period")

    qs = DailyMenu.objects(dining_hall=hall_id, date=target_date)
    if period:
        qs = qs.filter(meal_period=period)

    result = []
    for menu in qs:
        result.append(
            {
                "meal_period": menu.meal_period,
                "items": MenuItemSerializer(menu.items, many=True).data,
            }
        )
    return Response(result)


# User Profile


@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def user_profile(request):
    """Get or update the current user's profile."""
    profile = UserProfile.objects(django_user_id=1).first()

    if request.method == "GET":
        if not profile:
            return Response(
                {"detail": "Profile not set up yet."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(UserProfileSerializer(profile).data)

    # PUT
    serializer = UserProfileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if not profile:
        profile = UserProfile(django_user_id=1)

    for field, value in data.items():
        setattr(profile, field, value)

    if "macro_goals" in data:
        from api.models import Macros
        profile.macro_goals = Macros(**data["macro_goals"])

    profile.save()
    return Response(UserProfileSerializer(profile).data)

@api_view(["POST"])
@permission_classes([AllowAny])
def toggle_favorite_meal(request):
    """Toggle a meal name in the user's favorite_meals list."""
    profile = UserProfile.objects(django_user_id=1).first()
    if not profile:
        profile = UserProfile(django_user_id=1)
        profile.save()

    meal_name = request.data.get("meal_name")
    if not meal_name:
        return Response({"detail": "meal_name is required."}, status=status.HTTP_400_BAD_REQUEST)

    if meal_name in profile.favorite_meals:
        profile.favorite_meals.remove(meal_name)
    else:
        profile.favorite_meals.append(meal_name)

    profile.save()
    return Response({"favorite_meals": profile.favorite_meals})





@api_view(["POST"])
@permission_classes([AllowAny])
def generate_meal_plan(request):
    """Generate a personalized daily meal plan."""
    profile = UserProfile.objects(django_user_id=1).first()
    if not profile:
        return Response(
            {"detail": "Please complete your profile before generating a meal plan."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    target_date_str = request.data.get("date", date.today().isoformat())
    try:
        target_date = date.fromisoformat(target_date_str)
    except ValueError:
        return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    location = request.data.get("location")  # {"lat": ..., "lng": ...}

    service = MealPlannerService()
    plan = service.generate_plan(profile, target_date, location)
    return Response(MealPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def meal_plan_history(request):
    """Return the user's past and current meal plans."""
    from api.models import MealPlan

    plans = MealPlan.objects(django_user_id=1).order_by("-date").limit(14)
    return Response(MealPlanSerializer(plans, many=True).data)


# Wait Times


@api_view(["GET"])
@permission_classes([AllowAny])
def wait_times(request):
    """Return current predicted wait times for all dining halls."""
    period = request.query_params.get("period", "lunch")
    service = WaitTimeService()
    result = []
    for hall in DiningHall.objects.all():
        wait = service.predict(hall, period)
        result.append(
            {
                "dining_hall_id": str(hall.id),
                "dining_hall_name": hall.name,
                "estimated_wait_minutes": wait,
                "meal_period": period,
            }
        )
    return Response(WaitTimeSerializer(result, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def record_checkin(request):
    """Record a dining hall check-in (geofence trigger) and log wait time."""
    hall_id = request.data.get("dining_hall_id")
    wait = request.data.get("estimated_wait_minutes")
    occupancy = request.data.get("occupancy_pct")

    if not hall_id:
        return Response({"detail": "dining_hall_id required."}, status=400)

    hall = DiningHall.objects(id=hall_id).first()
    if not hall:
        return Response({"detail": "Dining hall not found."}, status=404)

    service = WaitTimeService()
    sample = service.record_sample(hall, wait or 0, occupancy)
    return Response({"status": "recorded", "sample_id": str(sample.id)})


# Admin: Menu Refresh


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_menus(request):
    """Manually trigger a Cornell Dining API menu refresh (admin only)."""
    if not request.user.is_staff:
        return Response({"detail": "Forbidden."}, status=403)

    target_date_str = request.data.get("date", date.today().isoformat())
    try:
        target_date = date.fromisoformat(target_date_str)
    except ValueError:
        return Response({"detail": "Invalid date."}, status=400)

    client = CornellDiningClient()
    count = client.ingest_all_menus(target_date)
    return Response({"ingested_periods": count, "date": target_date_str})



@api_view(['POST'])
@permission_classes([AllowAny])
def generate_ai_meal_plan(request):
    target_date_str = request.data.get("date", date.today().isoformat())
    
    profile = UserProfile.objects(django_user_id=1).first()
    if not profile:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        target_date = date.fromisoformat(target_date_str)
    except ValueError:
        target_date = date.today()
        
    result = generate_rag_meal_plan(profile, target_date_str)
    return Response({"ai_plan": result}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_ask(request):
    question = request.data.get("question")
    target_date_str = request.data.get("date", date.today().isoformat())
    
    if not question:
        return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        target_date = date.fromisoformat(target_date_str)
    except ValueError:
        target_date = date.today()
        
    result = chatbot_query(question, target_date_str)
    return Response(result, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def log_meal_from_image(request):
    """
    Accepts a base64 encoded image, identifies the food via Vision API,
    and returns the best match from today's menu.
    """
    from api.services.vision_service import identify_food_from_image
    from api.models import DailyMenu
    from datetime import date

    b64_image = request.data.get("image")
    if not b64_image:
        return Response({"detail": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)
        
    description = identify_food_from_image(b64_image)
    if "Error" in description or "Unknown" in description:
        return Response({"detail": description}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    today = date.today().isoformat()
    menus = DailyMenu.objects(date=today)
    
    best_match = None
    best_score = 0
    desc_words = set(description.lower().replace(",", "").replace(".", "").split())
    
    for menu in menus:
        for item in menu.items:
            item_words = set(item.name.lower().replace(",", "").replace(".", "").split())
            score = len(desc_words.intersection(item_words))
            if score > best_score:
                best_score = score
                best_match = item
                
    if best_match:
        from api.serializers import MenuItemSerializer
        return Response({
            "identified_as": description,
            "matched_item": MenuItemSerializer(best_match).data
        })
    
    return Response({
        "identified_as": description,
        "detail": "Could not find a matching item on today's menu."
    })
