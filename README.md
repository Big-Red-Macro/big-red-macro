# Big Red Macro

**Big Red Macro** is an intelligent, AI-driven dining planner built exclusively for Cornell University students. It seamlessly connects real-time data from the Cornell Dining API with your Google Calendar to generate hyper-personalized daily meal itineraries that perfectly balance your academic schedule, dietary restrictions, and macro goals.

## Some Features

- **Real-Time Cornell Dining Aggregation:** Automatically scrapes the Cornell Open Data API to build daily local menus and cache hall operating hours.
- **Smart Dining Dashboard:** Explore all open and closed campus dining halls. View their active menus, check what dining plans they accept (Swipes vs. BRBs), and explicitly filter by campus area (North, West, Central).
- **Personalized "Favorites" Network:** Tap the heart icon on any menu item across any dining hall to add it to your profile's `favorite_meals`. 
- **Automated AI Meal Planner:** 
  - Sync securely with **Google Calendar** using an official OAuth 2.0 PKCE flow.
  - The backend leverages the **Gemini 2.5 Flash** LLM acting as a LangChain RAG pipeline.
  - It analyzes your free-time gaps and forcefully constraints itself to plan out your Breakfast, Lunch, and Dinner—strictly targeting your dietary restrictions (e.g. Vegan, Halal) and aggressively pushing menu options you marked as your favorites.
- **Cornell-Native Aesthetic:** A premium UI utilizing deep Cornell Red gradients and modern glassmorphism.

## Stack

- **Frontend:** Vue 3, Vite, Tailwind CSS (Custom Cornell Red `.cornell-red`), Pinia, Vue Router.
- **Backend:** Python, Django REST Framework, Django-MongoEngine.
- **Database:** MongoDB (Caching menus, user profiles, AI configurations).
- **AI Infrastructure:** Google GenAI SDK (`gemini-2.5-flash`), heavily engineered LangChain Prompt Templates.
- **External Integrations:** Google Calendar Data API, Cornell Open Data Initiative REST API.

## Getting Started

### Prerequisites

- **Docker & Docker Compose** — the recommended way to run everything.
- A **Google API Key** with the Gemini API enabled (required for the Vision pipeline and AI meal planner).
- A **Google OAuth 2.0 Web client ID** for Google sign-in. Add `http://localhost:5173` to the client's authorized JavaScript origins in Google Cloud.

### 1. Environment Variables

Copy the example env file and fill in your keys:

```bash
cp backend/.env.example backend/.env
```

Then open `backend/.env` and configure:

| Variable | What it is | How to get it |
|---|---|---|
| `SECRET_KEY` | Django signing key | Generate one: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `GOOGLE_API_KEY` | Powers the Vision pipeline (Gemini) + Google Calendar integration | Go to [Google AI Studio](https://aistudio.google.com/apikey) → Create an API key. Make sure the Gemini API is enabled. |
| `GOOGLE_CLIENT_ID` | Verifies Google sign-in credentials on the backend and configures the frontend sign-in button | Google Cloud Console → APIs & Services → Credentials → Create OAuth client ID → Web application. Add `http://localhost:5173` under Authorized JavaScript origins. |
| `GOOGLE_CLIENT_SECRET` | Exchanges Google Calendar OAuth codes for calendar tokens | Copy it from the same Google OAuth Web client. |
| `GOOGLE_CALENDAR_REDIRECT_URI` | Calendar OAuth callback URL sent to Google | Default: `http://localhost:5173/calendar-callback`. Add this exact URL under Authorized redirect URIs for the same OAuth client. |
| `MAPBOX_ACCESS_TOKEN` | Campus map and walking directions | Go to [Mapbox](https://account.mapbox.com/access-tokens/) → Create a token (the default public token works). |
| `MONGODB_URI` | MongoDB connection string | Defaults to `mongodb://localhost:27017/bigredmacro`. Docker handles this automatically. |
| `REDIS_URL` | Redis connection for Celery task queue | Defaults to `redis://localhost:6379/0`. Docker handles this automatically. |
| `CORNELL_DINING_API_BASE` | Cornell Dining API base URL | Default: `https://admin-now.dining.cornell.edu/api/1.0` |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins | Default: `http://localhost:5173` |

### 2. Running with Docker (Recommended)

Docker Compose spins up **4 containers**: MongoDB, Redis, Django Backend, and Celery Worker.

```bash
# Set your Google API key so docker-compose can pass it to containers
export GOOGLE_API_KEY="your-key-here"
export GOOGLE_CLIENT_ID="your-oauth-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-oauth-client-secret"
export GOOGLE_CALENDAR_REDIRECT_URI="http://localhost:5173/calendar-callback"

# Build and start all services
docker compose up --build -d
```

Then run first-time setup:

```bash
# Run database migrations (Django auth tables)
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# Pull today's dining menus from the Cornell API
docker compose exec backend python manage.py shell -c \
  "from api.services.dining_api import CornellDiningClient; c = CornellDiningClient(); c.ingest_all_menus()"

# Create a local testing user
docker compose exec backend python manage.py createsuperuser
```

### 3. Running Locally (No Docker)

If you prefer to run without Docker, you need to install and start these services yourself:

| Service | Install (macOS) | Default Port |
|---|---|---|
| **MongoDB 7** | `brew install mongodb-community` then `brew services start mongodb-community` | `27017` |
| **Redis 7** | `brew install redis` then `brew services start redis` | `6379` |

Then install Python dependencies and run:

```bash
cd backend
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

To start the Celery worker (handles background tasks like the 4 AM favorite-food alerts):

```bash
cd backend
celery -A bigredmacro worker -l info -B
```

### 4. No MongoDB Schema Changes Needed

MongoEngine handles schema dynamically — all collections (including `notifications` for the favorite food alerts) are created automatically the first time they are written to. No manual migration or collection setup is required.

### Accessing the Subsystems

| Service | URL |
|---|---|
| **Frontend Dashboard** | [http://localhost:5173](http://localhost:5173) |
| **Backend Django API** | [http://localhost:8000/api/](http://localhost:8000/api/) |
| **MongoDB** | `mongodb://localhost:27017` |
| **Redis** | `redis://localhost:6379` |

### Viewing Your Databases

#### MongoDB (menus, users, meal plans, notifications)

Use [MongoDB Compass](https://www.mongodb.com/products/compass) (GUI):

```bash
brew install --cask mongodb-compass
```

Open Compass, connect to `mongodb://localhost:27017`, and click on the **bigredmacro** database. You'll see collections like `dining_halls`, `daily_menus`, `user_profiles`, `meal_plans`, `notifications`, etc.

Or from the terminal:

```bash
mongosh mongodb://localhost:27017/bigredmacro
```



#### SQLite (Django auth only — users, tokens, sessions)

This is the small `backend/auth.db` file used only for Django's auth system. You can open it with [DB Browser for SQLite](https://sqlitebrowser.org/), or from the terminal:

```bash
sqlite3 backend/auth.db ".tables"
```
