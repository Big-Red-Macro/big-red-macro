"""
Menu-item NLP categoriser.

Two-stage approach
------------------
1. Rule-based pseudo-labeller
   Assigns a nutritional category to a menu item from its name/description
   using keyword lists.  Used to generate silver-label training data from
   the DailyMenu corpus.

2. TF-IDF + Logistic Regression classifier
   Trained on the pseudo-labelled corpus and serialised to disk.  Once
   trained it generalises beyond the keyword vocabulary (e.g. "Grilled
   Herb Polenta" → grain even though "polenta" may not be a keyword).

Categories
----------
  protein    – meat, fish, eggs, legumes, tofu
  grain      – rice, bread, pasta, cereals, baked goods
  vegetable  – salads, cooked veg
  fruit      – fresh or cooked fruit
  dairy      – cheese, yogurt, milk-based items
  dessert    – cakes, cookies, ice cream, sweet pastries
  beverage   – hot and cold drinks
  condiment  – sauces, dressings, spreads
  mixed      – catch-all (not used as a training label)
"""

import logging
import os
import re

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

_HERE = os.path.dirname(__file__)
MODEL_DIR = os.path.abspath(os.path.join(_HERE, "..", "..", "ml_models"))
MODEL_PATH = os.path.join(MODEL_DIR, "item_classifier.joblib")

MIN_TRAINING_ITEMS = 50

_KEYWORDS: dict[str, list[str]] = {
    "protein": [
        "chicken", "beef", "steak", "pork", "ham", "bacon", "turkey",
        "fish", "salmon", "tuna", "tilapia", "cod", "shrimp", "scallop",
        "crab", "lobster", "tofu", "tempeh", "seitan", "edamame",
        "lentil", "chickpea", "black bean", "kidney bean", "egg", "eggs",
        "sausage", "burger", "meatball", "meatloaf", "falafel",
    ],
    "grain": [
        "rice", "pasta", "spaghetti", "penne", "fettuccine", "bread",
        "noodle", "roll", "wrap", "tortilla", "bagel", "oatmeal",
        "granola", "cereal", "quinoa", "couscous", "muffin", "croissant",
        "toast", "pita", "waffle", "pancake", "polenta", "grits", "pilaf",
        "risotto", "biscuit", "pretzel", "cracker", "porridge", "hominy",
        "fry", "fries", "chip", "tot", "nacho", "tabbouleh", "bulgar",
        "french toast", "flatbread",
    ],
    "vegetable": [
        "salad", "broccoli", "spinach", "kale", "carrot", "zucchini",
        "pepper", "onion", "tomato", "corn", "pea", "asparagus", "beet",
        "cucumber", "mushroom", "cabbage", "lettuce", "celery", "potato",
        "squash", "eggplant", "artichoke", "brussels", "cauliflower",
        "chard", "arugula", "fennel", "leek", "radish", "turnip",
        "roasted vegetable", "stir fry", "snow pea", "edamame",
        "bok choy", "collard", "sweet potato", "yam",
    ],
    "fruit": [
        "apple", "banana", "orange", "grape", "strawberry", "blueberry",
        "mango", "pineapple", "melon", "peach", "pear", "cherry", "berry",
        "cantaloupe", "watermelon", "kiwi", "papaya", "plum", "apricot",
        "grapefruit", "lemon", "lime", "fig", "fruit", "raisin", "cranberry",
    ],
    "dairy": [
        "cheese", "yogurt", "milk", "butter", "cream", "mozzarella",
        "cheddar", "parmesan", "brie", "feta", "ricotta", "cottage",
        "provolone", "gouda", "swiss", "burrata", "whipped cream", "dairy",
        "queso",
    ],
    "dessert": [
        "cake", "cookie", "brownie", "pie", "pudding", "donut", "sorbet",
        "gelato", "macaron", "tart", "sundae", "mousse", "custard",
        "cheesecake", "tiramisu", "cobbler", "crumble", "scone",
        "shortbread", "eclair", "profiterole", "flan", "baklava",
        "ice cream", "chocolate", "sweet", "dessert", "candy",
    ],
    "beverage": [
        "coffee", "tea", "juice", "water", "smoothie", "latte",
        "cappuccino", "espresso", "cider", "lemonade", "kombucha",
        "milkshake", "hot chocolate", "chai", "matcha", "soda",
        "cocoa", "beverage", "beverages", "pepsi", "cola", "beer",
        "wine", "coke", "drink", "bubble tea",
    ],
    "condiment": [
        "sauce", "ketchup", "mustard", "dressing", "salsa", "hummus",
        "guacamole", "gravy", "aioli", "pesto", "relish", "chutney",
        "vinaigrette", "syrup", "jelly", "mayo", "tahini",
        "tzatziki", "ranch", "sriracha", "hot sauce", "toping", "topping",
    ],
}

# Category priority for tie-breaking (higher index = higher priority)
_CATEGORY_PRIORITY = [
    "condiment", "beverage", "fruit", "vegetable", "dessert",
    "grain", "dairy", "protein",
]

VALID_CATEGORIES = list(_KEYWORDS.keys())  # excludes "mixed"


# ---------------------------------------------------------------------------
# Rule-based pseudo-labeller
# ---------------------------------------------------------------------------

def pseudo_label(text: str) -> str:
    """
    Assign a category to *text* (item name + description) by keyword matching.

    Uses whole-word regex matching to avoid substring false positives
    (e.g. "corn" should not match "cornell", "jam" should not match "jamaican").

    On a tie by keyword-hit count, the higher-priority category wins
    (protein > dairy > grain > … > condiment).

    Returns "mixed" when no keyword hits.
    """
    text = text.lower()
    hits: dict[str, int] = {}
    for category, keywords in _KEYWORDS.items():
        count = 0
        for kw in keywords:
            # Word-boundary at start; allow common suffixes (plurals, past tense)
            # so "beet" matches "beets", "cookie" matches "cookies",
            # but "corn" does NOT match "cornell" and "jam" does NOT match "jamaican".
            pattern = r"\b" + re.escape(kw) + r"(?:e?s|ing|ed)?\b"
            if re.search(pattern, text):
                count += 1
        if count:
            hits[category] = count

    if not hits:
        return "mixed"

    max_count = max(hits.values())
    top = [cat for cat, cnt in hits.items() if cnt == max_count]

    if len(top) == 1:
        return top[0]

    # Tie-break: pick the highest-priority category
    for cat in reversed(_CATEGORY_PRIORITY):
        if cat in top:
            return cat
    return top[0]


# Training

def train(menus=None) -> bool:
    """
    Build a pseudo-labelled corpus from DailyMenu items and train TF-IDF + LR.

    Parameters
    ----------
    menus : optional iterable of DailyMenu documents.
            If None, all documents are fetched from the DB.

    Returns True on success, False when there is insufficient labelled data.
    """
    if menus is None:
        from api.models import DailyMenu
        menus = DailyMenu.objects.all()

    texts: list[str] = []
    labels: list[str] = []

    for menu in menus:
        for item in menu.items or []:
            text = f"{item.name} {item.description or ''}".strip()
            label = pseudo_label(text)
            if label != "mixed":
                texts.append(text.lower())
                labels.append(label)

    if len(texts) < MIN_TRAINING_ITEMS:
        logger.info(
            "item_classifier.train: need ≥%d labelled items, have %d — skipping",
            MIN_TRAINING_ITEMS,
            len(texts),
        )
        return False

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=8000,
                    sublinear_tf=True,
                    min_df=2,
                ),
            ),
            (
                "lr",
                LogisticRegression(
                    C=1.0,
                    max_iter=500,
                    solver="lbfgs",
                    multi_class="multinomial",
                    random_state=42,
                ),
            ),
        ]
    )
    pipeline.fit(texts, labels)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info("item_classifier: trained on %d items → %s", len(texts), MODEL_PATH)
    return True


# Inference

_cached_pipeline = None


def _load_pipeline():
    global _cached_pipeline
    if _cached_pipeline is not None:
        return _cached_pipeline
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        _cached_pipeline = joblib.load(MODEL_PATH)
        logger.info("item_classifier: loaded model from %s", MODEL_PATH)
    except Exception as exc:
        logger.warning("item_classifier: failed to load model — %s", exc)
        _cached_pipeline = None
    return _cached_pipeline


def invalidate_cache():
    global _cached_pipeline
    _cached_pipeline = None


def classify(name: str, description: str = "") -> str:
    """
    Classify a menu item into a nutritional category.

    Uses the trained ML model when available; falls back to the rule-based
    pseudo-labeller otherwise.  Never returns None.
    """
    text = f"{name} {description or ''}".strip().lower()

    pipeline = _load_pipeline()
    if pipeline is not None:
        try:
            return pipeline.predict([text])[0]
        except Exception as exc:
            logger.warning("item_classifier.classify: %s", exc)

    # Rule-based fallback
    return pseudo_label(text)
