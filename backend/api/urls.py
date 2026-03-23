from django.urls import path
from api import views

urlpatterns = [
    # Dining halls & menus
    path("dining-halls/", views.dining_halls, name="dining-halls"),
    path("dining-halls/<str:hall_id>/menu/", views.dining_hall_menu, name="hall-menu"),
    # User profile
    path("profile/", views.user_profile, name="user-profile"),
    # Meal plans
    path("meal-plan/generate/", views.generate_meal_plan, name="generate-meal-plan"),
    path("meal-plan/history/", views.meal_plan_history, name="meal-plan-history"),
    # Wait times & check-in
    path("wait-times/", views.wait_times, name="wait-times"),
    path("checkin/", views.record_checkin, name="checkin"),
    # Admin
    path("admin/refresh-menus/", views.refresh_menus, name="refresh-menus"),
]
