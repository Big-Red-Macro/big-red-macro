"""
Wait-time Gradient Boosting regressor.

Trains a single GradientBoostingRegressor on all WaitTimeSample history with
dining_type encoded as a feature. Falls back to None when the model file does
not exist or when fewer than MIN_SAMPLES are available.

Features (7):
  dining_type_code  – 0=residential, 1=cafe, 2=retail
  day_of_week       – 0 (Mon) … 6 (Sun)
  hour              – 0 … 23
  minute_bin        – 0 / 15 / 30 / 45  (quantised)
  is_weekend        – 0 or 1
  occupancy_pct     – 0.0 … 1.0  (imputed to 0.5 when absent)
  campus_area_code  – 0=Central, 1=North, 2=West, 3=East  (from real API campusArea)

Target: estimated_wait_minutes (int)
"""

import logging
import os

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# Directory is two levels above this file: backend/ml_models/
_HERE = os.path.dirname(__file__)
MODEL_DIR = os.path.abspath(os.path.join(_HERE, "..", "..", "ml_models"))
MODEL_PATH = os.path.join(MODEL_DIR, "wait_time_global.joblib")

MIN_SAMPLES = 30

DINING_TYPE_CODE = {"residential": 0, "cafe": 1, "retail": 2}
CAMPUS_AREA_CODE = {"Central": 0, "North": 1, "West": 2, "East": 3}


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def _row(sample) -> list:
    """Convert one WaitTimeSample document into a feature row."""
    dining_type = getattr(sample.dining_hall, "dining_type", "residential") or "residential"
    campus_area = getattr(sample.dining_hall, "campus_area", "Central") or "Central"
    return [
        DINING_TYPE_CODE.get(dining_type, 0),
        int(sample.day_of_week),
        int(sample.hour),
        (int(sample.minute) // 15) * 15,
        1 if int(sample.day_of_week) >= 5 else 0,
        float(sample.occupancy_pct) if sample.occupancy_pct is not None else 0.5,
        CAMPUS_AREA_CODE.get(campus_area, 0),
    ]


def _build_dataset(samples):
    X = [_row(s) for s in samples]
    y = [int(s.estimated_wait_minutes) for s in samples]
    return np.array(X, dtype=float), np.array(y, dtype=float)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train(samples=None) -> bool:
    """
    Train (or retrain) the global wait-time model.

    Parameters
    ----------
    samples : optional list/queryset of WaitTimeSample documents.
              If None, all documents are fetched from the DB.

    Returns True on success, False when there is insufficient data.
    """
    if samples is None:
        from api.models import WaitTimeSample
        samples = list(WaitTimeSample.objects.all())

    if len(samples) < MIN_SAMPLES:
        logger.info(
            "wait_time_model.train: need ≥%d samples, have %d — skipping",
            MIN_SAMPLES,
            len(samples),
        )
        return False

    X, y = _build_dataset(samples)

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "gbr",
                GradientBoostingRegressor(
                    n_estimators=150,
                    max_depth=4,
                    learning_rate=0.08,
                    subsample=0.8,
                    random_state=42,
                ),
            ),
        ]
    )
    pipeline.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info("wait_time_model: trained on %d samples → %s", len(X), MODEL_PATH)
    return True


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

# Module-level cache so the model is loaded at most once per process.
_cached_pipeline = None


def _load_pipeline():
    global _cached_pipeline
    if _cached_pipeline is not None:
        return _cached_pipeline
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        _cached_pipeline = joblib.load(MODEL_PATH)
        logger.info("wait_time_model: loaded model from %s", MODEL_PATH)
    except Exception as exc:
        logger.warning("wait_time_model: failed to load model — %s", exc)
        _cached_pipeline = None
    return _cached_pipeline


def invalidate_cache():
    """Call after retraining so the next prediction picks up the new weights."""
    global _cached_pipeline
    _cached_pipeline = None


def predict(dining_hall, day_of_week: int, hour: int, minute: int, occupancy_pct: float = 0.5) -> int | None:
    """
    Return a predicted wait time in minutes, or None if the model is unavailable.

    Parameters
    ----------
    dining_hall   : DiningHall document (needs .dining_type attribute)
    day_of_week   : 0=Mon … 6=Sun
    hour          : 0 … 23
    minute        : 0 … 59
    occupancy_pct : 0.0 … 1.0
    """
    pipeline = _load_pipeline()
    if pipeline is None:
        return None

    dining_type = getattr(dining_hall, "dining_type", "residential") or "residential"
    campus_area = getattr(dining_hall, "campus_area", "Central") or "Central"
    features = np.array(
        [[
            DINING_TYPE_CODE.get(dining_type, 0),
            day_of_week,
            hour,
            (minute // 15) * 15,
            1 if day_of_week >= 5 else 0,
            float(occupancy_pct) if occupancy_pct is not None else 0.5,
            CAMPUS_AREA_CODE.get(campus_area, 0),
        ]],
        dtype=float,
    )

    try:
        raw = pipeline.predict(features)[0]
        return max(0, round(float(raw)))
    except Exception as exc:
        logger.warning("wait_time_model.predict: %s", exc)
        return None
