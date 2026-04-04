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

## Getting Started for(Local Development)

Big Red Macro is fully containerized using Docker. 

### needed
- Docker and Docker Compose installed.
- A valid `.env` file placed inside the `/backend` directory containing your Google OAuth keys and Gemini API keys. 

### Booting

1. From the project root, launch the orchestration:
   ```bash
   docker compose up --build -d
   ```
2. Run database migrations and generate the index structures:
   ```bash
   docker compose exec backend python manage.py makemigrations
   docker compose exec backend python manage.py migrate
   ```
3. Initialize the Cornell Dining Database. This pulls down the latest active menus off the public API:
   ```bash
   docker compose exec backend python manage.py shell -c "from api.services.dining_api import CornellDiningClient; c = CornellDiningClient(); c.ingest_all_menus()"
   ```
4. Create a local testing User!
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

### Accessing the Subsystems
- **Frontend Dashboard:** [http://localhost:5173/](http://localhost:5173/)
- **Backend Django API:** [http://localhost:8000/api/](http://localhost:8000/api/)
- **MongoDB Instance:** Connect to `mongodb://localhost:27017`
