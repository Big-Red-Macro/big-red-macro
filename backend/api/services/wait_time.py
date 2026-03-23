"""
Predictive wait-time service.

Uses a simple heuristic model that can be swapped for a trained
scikit-learn time-series model once enough WaitTimeSample data exists.
"""

from datetime import datetime
import logging

from api.models import DiningHall, WaitTimeSample

logger = logging.getLogger(__name__)

# Peak hours by meal period (hour of day -> baseline wait multiplier)
PEAK_PROFILE = {
    "breakfast": {8: 1.5, 9: 2.0, 10: 1.2},
    "lunch": {11: 1.8, 12: 3.0, 13: 2.5, 14: 1.3},
    "dinner": {17: 1.5, 18: 2.5, 19: 2.8, 20: 1.5},
    "brunch": {10: 1.5, 11: 2.0, 12: 2.5},
}

BASE_WAIT_MINUTES = {
    "residential": 8,
    "cafe": 4,
    "retail": 2,
}


class WaitTimeService:
    def predict(self, dining_hall: DiningHall, meal_period: str) -> int:
        """Return estimated wait time in minutes for a dining hall right now."""
        now = datetime.now()
        hour = now.hour

        # Try historical model first
        historical = self._historical_average(dining_hall, meal_period, hour)
        if historical is not None:
            return historical

        # Fallback: heuristic
        return self._heuristic(dining_hall, meal_period, hour)

    def _historical_average(
        self, dining_hall: DiningHall, meal_period: str, hour: int
    ) -> int | None:
        """Average the last 4 weeks of samples for this hall/period/hour."""
        samples = WaitTimeSample.objects(
            dining_hall=dining_hall,
            day_of_week=datetime.now().weekday(),
            hour=hour,
        ).order_by("-recorded_at").limit(20)

        if not samples:
            return None

        avg = sum(s.estimated_wait_minutes for s in samples) / len(samples)
        return round(avg)

    def _heuristic(self, dining_hall: DiningHall, meal_period: str, hour: int) -> int:
        base = BASE_WAIT_MINUTES.get(dining_hall.dining_type, 8)
        multiplier = PEAK_PROFILE.get(meal_period, {}).get(hour, 1.0)
        return round(base * multiplier)

    def record_sample(
        self,
        dining_hall: DiningHall,
        estimated_wait: int,
        occupancy_pct: float = None,
    ):
        """Persist a new wait-time observation (called from check-in or admin)."""
        now = datetime.utcnow()
        sample = WaitTimeSample(
            dining_hall=dining_hall,
            recorded_at=now,
            day_of_week=now.weekday(),
            hour=now.hour,
            minute=now.minute,
            estimated_wait_minutes=estimated_wait,
            occupancy_pct=occupancy_pct,
        )
        sample.save()
        return sample
