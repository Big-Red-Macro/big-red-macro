import logging
from datetime import date, datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings

from api.models import AIItinerary, DailyMenu, DailyNutritionLog, DiningHall, UserProfile, WaitTimeSample
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

logger = logging.getLogger(__name__)

MEAL_PERIOD_ORDER = {
    "breakfast": 0,
    "brunch": 1,
    "lunch": 2,
    "dinner": 3,
}


def _today_str():
    return date.today().isoformat()


def _valid_date_or_today(value):
    try:
        return date.fromisoformat(value or _today_str()).isoformat()
    except ValueError:
        return _today_str()


def _empty_macros():
    return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}


def _clean_macros(value):
    value = value or {}
    return {
        "calories": float(value.get("calories") or 0),
        "protein_g": float(value.get("protein_g") or 0),
        "carbs_g": float(value.get("carbs_g") or 0),
        "fat_g": float(value.get("fat_g") or 0),
    }


def _nutrition_payload(log):
    meals = log.meals or {}
    manual = _clean_macros(log.manual)
    total = _empty_macros()
    for meal in meals.values():
        if meal.get("checked"):
            macros = _clean_macros(meal.get("macros"))
            for key in total:
                total[key] += macros[key]
    for key in total:
        total[key] += manual[key]
        total[key] = round(total[key])
    return {
        "date": log.date,
        "meals": meals,
        "manual": manual,
        "totals": total,
    }


def _serialize_menu_queryset(qs, requested_date, source_date):
    result = []
    for menu in sorted(qs, key=lambda m: MEAL_PERIOD_ORDER.get(m.meal_period, 99)):
        result.append(
            {
                "meal_period": menu.meal_period,
                "items": MenuItemSerializer(menu.items, many=True).data,
                "date": menu.date,
                "requested_date": requested_date,
                "source_date": source_date,
                "is_fallback": menu.date != requested_date,
            }
        )
    return result


def _hall_menu_queryset(hall, target_date, period=None):
    qs = DailyMenu.objects(dining_hall=hall, date=target_date, source="cornell_dining_api")
    if period:
        qs = qs.filter(meal_period=period)
    return list(qs)


def _latest_hall_menu_queryset(hall, period=None):
    latest_qs = DailyMenu.objects(dining_hall=hall, source="cornell_dining_api")
    if period:
        latest_qs = latest_qs.filter(meal_period=period)

    latest_menu = latest_qs.order_by("-date").first()
    if not latest_menu:
        return [], None

    qs = DailyMenu.objects(dining_hall=hall, date=latest_menu.date, source="cornell_dining_api")
    if period:
        qs = qs.filter(meal_period=period)
    return list(qs), latest_menu.date



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
    target_date = _valid_date_or_today(request.query_params.get("date"))
    period = request.query_params.get("period")
    hall = DiningHall.objects(id=hall_id).first()
    if not hall:
        return Response({"detail": "Dining hall not found."}, status=404)

    menus = _hall_menu_queryset(hall, target_date, period)
    source_date = target_date
    source = "exact"

    if not menus:
        refresh_cache_key = f"dining_menu_refresh_attempted:{target_date}"
        if not cache.get(refresh_cache_key):
            try:
                CornellDiningClient().ingest_all_menus(date.fromisoformat(target_date))
                menus = _hall_menu_queryset(hall, target_date, period)
            except Exception as exc:
                logger.warning("Could not refresh Cornell Dining menus for %s: %s", target_date, exc)
            finally:
                cache.set(refresh_cache_key, True, timeout=15 * 60)

    if not menus:
        menus, source_date = _latest_hall_menu_queryset(hall, period)
        if menus:
            source = "latest_cached"

    return Response(
        {
            "requested_date": target_date,
            "source_date": source_date,
            "source": source if menus else "none",
            "is_fallback": bool(menus and source_date != target_date),
            "menus": _serialize_menu_queryset(menus, target_date, source_date),
        }
    )


# User Profile


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update the current user's profile."""
    profile = UserProfile.objects(django_user_id=request.user.id).first()

    if request.method == "GET":
        if not profile:
            profile = UserProfile(django_user_id=request.user.id)
            profile.save()
        return Response(UserProfileSerializer(profile).data)

    # PUT
    serializer = UserProfileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if not profile:
        profile = UserProfile(django_user_id=request.user.id)

    for field, value in data.items():
        if field == "macro_goals":
            continue
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



@api_view(['GET'])
@permission_classes([AllowAny])
def calendar_connect(request):
    redirect_uri = settings.GOOGLE_CALENDAR_REDIRECT_URI
    url, state, code_verifier = get_authorization_url(redirect_uri)
    if url:
        if code_verifier and state:
            cache.set(f"pkce_{state}", code_verifier, timeout=600)
        return Response(
            {"auth_url": url, "redirect_uri": redirect_uri},
            status=status.HTTP_200_OK,
        )
    return Response({"error": "Failed to generate auth url"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def calendar_callback(request):
    oauth_error = request.GET.get('error') or request.data.get('error')
    if oauth_error:
        return Response(
            {"error": oauth_error, "detail": request.GET.get('error_description') or request.data.get('error_description') or "Google Calendar authorization was cancelled or denied."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code = request.GET.get('code') or request.data.get('code')
    state = request.GET.get('state') or request.data.get('state')
    if not code:
        return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    code_verifier = cache.get(f"pkce_{state}") if state else None
    
    redirect_uri = settings.GOOGLE_CALENDAR_REDIRECT_URI
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
    target_date_str = _valid_date_or_today(request.data.get("date"))
    token_dict = request.data.get("google_auth_token", {})
    
    profile = UserProfile.objects(django_user_id=request.user.id).first()
    if not profile:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
    if token_dict and profile:
        profile.google_auth_token = token_dict
        profile.save()
    elif not token_dict and profile.google_auth_token:
        token_dict = profile.google_auth_token

    target_date = date.fromisoformat(target_date_str)
        
    gaps = get_free_time_blocks(token_dict, target_date)
    
    result = generate_rag_meal_plan(profile, gaps, target_date_str)
    AIItinerary.objects(
        django_user_id=request.user.id,
        date=target_date_str,
    ).update_one(
        set__plan=result,
        set__updated_at=datetime.utcnow(),
        set_on_insert__generated_at=datetime.utcnow(),
        upsert=True,
    )
    DailyNutritionLog.objects(
        django_user_id=request.user.id,
        date=target_date_str,
    ).update_one(
        set__meals={},
        set__manual=_empty_macros(),
        set__updated_at=datetime.utcnow(),
        upsert=True,
    )
    return Response({"ai_plan": result}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saved_ai_itinerary(request):
    target_date_str = _valid_date_or_today(request.query_params.get("date"))
    saved = AIItinerary.objects(
        django_user_id=request.user.id,
        date=target_date_str,
    ).first()
    if not saved:
        return Response(
            {"date": target_date_str, "ai_plan": None},
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "date": target_date_str,
            "ai_plan": saved.plan,
            "generated_at": saved.generated_at.isoformat() if saved.generated_at else None,
            "updated_at": saved.updated_at.isoformat() if saved.updated_at else None,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def nutrition_log(request):
    target_date_str = _valid_date_or_today(
        request.query_params.get("date") if request.method == "GET" else request.data.get("date")
    )
    log = DailyNutritionLog.objects(
        django_user_id=request.user.id,
        date=target_date_str,
    ).first()

    if request.method == "GET":
        if not log:
            log = DailyNutritionLog(
                django_user_id=request.user.id,
                date=target_date_str,
                meals={},
                manual=_empty_macros(),
            )
            log.save()
        return Response(_nutrition_payload(log), status=status.HTTP_200_OK)

    if not log:
        log = DailyNutritionLog(django_user_id=request.user.id, date=target_date_str)

    log.meals = request.data.get("meals", {}) or {}
    log.manual = _clean_macros(request.data.get("manual"))
    log.updated_at = datetime.utcnow()
    log.save()
    return Response(_nutrition_payload(log), status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
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
