from rest_framework import serializers


class MacrosSerializer(serializers.Serializer):
    calories = serializers.FloatField()
    protein_g = serializers.FloatField()
    carbs_g = serializers.FloatField()
    fat_g = serializers.FloatField()
    fiber_g = serializers.FloatField(required=False, default=0)
    sodium_mg = serializers.FloatField(required=False, default=0)


class MenuItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, default="")
    category = serializers.CharField(allow_blank=True, default="")
    station = serializers.CharField(allow_blank=True, default="")
    macros = MacrosSerializer(required=False)
    allergens = serializers.ListField(child=serializers.CharField(), default=list)
    is_vegan = serializers.BooleanField(default=False)
    is_vegetarian = serializers.BooleanField(default=False)
    is_halal = serializers.BooleanField(default=False)
    is_gluten_free = serializers.BooleanField(default=False)


class DiningHallSerializer(serializers.Serializer):
    id = serializers.CharField(source="pk")
    name = serializers.CharField()
    short_name = serializers.CharField()
    location_lat = serializers.FloatField()
    location_lng = serializers.FloatField()
    dining_type = serializers.CharField()
    accepts_brbs = serializers.BooleanField()
    accepts_meal_swipe = serializers.BooleanField()
    supports_get_app = serializers.BooleanField()
    operating_hours = serializers.DictField()


class UserProfileSerializer(serializers.Serializer):
    cornell_netid = serializers.CharField(allow_blank=True, default="")
    macro_goals = MacrosSerializer(required=False)
    allergens = serializers.ListField(child=serializers.CharField(), default=list)
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(), default=list
    )
    meal_plan_type = serializers.ChoiceField(
        choices=["traditional", "west_campus", "bear_necessities", "none"],
        default="traditional",
    )
    home_location = serializers.DictField(required=False)


class MealSerializer(serializers.Serializer):
    period = serializers.CharField()
    dining_hall_id = serializers.CharField()
    dining_hall_name = serializers.CharField()
    items = serializers.ListField(child=serializers.DictField())
    macros = serializers.DictField()
    estimated_wait_minutes = serializers.IntegerField()
    supports_get_app = serializers.BooleanField()


class MealPlanSerializer(serializers.Serializer):
    id = serializers.CharField(source="pk")
    date = serializers.CharField()
    meals = MealSerializer(many=True)
    total_macros = MacrosSerializer()
    goal_macros = MacrosSerializer()
    generated_at = serializers.DateTimeField()


class WaitTimeSerializer(serializers.Serializer):
    dining_hall_id = serializers.CharField()
    dining_hall_name = serializers.CharField()
    estimated_wait_minutes = serializers.IntegerField()
    meal_period = serializers.CharField()
