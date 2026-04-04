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
from api.services.calendar_api import get_authorization_url, exchange_code, get_free_time_blocks
from api.RAG.pipeline import generate_rag_meal_plan




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dining_halls(request):
    """List all Cornell dining halls."""
    halls = DiningHall.objects.all()
    return Response(DiningHallSerializer(halls, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update the current user's profile."""
    profile = UserProfile.objects(django_user_id=request.user.id).first()

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
        profile = UserProfile(django_user_id=request.user.id)

    for field, value in data.items():
        setattr(profile, field, value)

    if "macro_goals" in data:
        from api.models import Macros
        profile.macro_goals = Macros(**data["macro_goals"])

    profile.save()
    return Response(UserProfileSerializer(profile).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite_meal(request):
    """Toggle a meal name in the user's favorite_meals list."""
    profile = UserProfile.objects(django_user_id=request.user.id).first()
    if not profile:
        profile = UserProfile(django_user_id=request.user.id)
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
@permission_classes([IsAuthenticated])
def generate_meal_plan(request):
    """Generate a personalized daily meal plan."""
    profile = UserProfile.objects(django_user_id=request.user.id).first()
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
@permission_classes([IsAuthenticated])
def meal_plan_history(request):
    """Return the user's past and current meal plans."""
    from api.models import MealPlan

    plans = MealPlan.objects(django_user_id=request.user.id).order_by("-date").limit(14)
    return Response(MealPlanSerializer(plans, many=True).data)


# Wait Times


@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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

# ------------------------------------------------------------------
# AI / Calendar / RAG
# ------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def calendar_connect(request):
    redirect_uri = "http://localhost:5173/calendar-callback"
    url, state, code_verifier = get_authorization_url(redirect_uri)
    if url:
        if code_verifier and state:
            cache.set(f"pkce_{state}", code_verifier, timeout=600)
        return Response({"auth_url": url}, status=status.HTTP_200_OK)
    return Response({"error": "Failed to generate auth url"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def calendar_callback(request):
    code = request.GET.get('code') or request.data.get('code')
    state = request.GET.get('state') or request.data.get('state')
    if not code:
        return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    code_verifier = cache.get(f"pkce_{state}") if state else None
    
    redirect_uri = "http://localhost:5173/calendar-callback"
    token_dict = exchange_code(code, redirect_uri, code_verifier)
    if not token_dict:
        return Response({"error": "Failed to exchange token"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "message": "Successfully exchanged code. Use this token dictionary for AI generation.",
        "token_dict": token_dict
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_ai_meal_plan(request):
    target_date = request.data.get("date", date.today().isoformat())
    token_dict = request.data.get("google_auth_token", {})
    
    profile = UserProfile.objects(django_user_id=request.user.id).first()
    if not profile:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
    if token_dict and profile:
        profile.google_auth_token = token_dict
        profile.save()
    elif not token_dict and profile.google_auth_token:
        token_dict = profile.google_auth_token
        
    gaps = get_free_time_blocks(token_dict, None)
    
    result = generate_rag_meal_plan(profile, gaps, target_date)
    return Response({"ai_plan": result}, status=status.HTTP_200_OK)

