# Game Tindr

A personal desktop app that turns game discovery into a Tinder-style swiping experience.
Swipe right on games you're interested in, left on ones that aren't your taste — the app
learns your preferences from your swipe history and (eventually) recommends games tailored
to you.

This is a solo learning project, built with AI guidance (see `prompt.md` for the full
roadmap and design philosophy), not production software.

## Current status: Phases 0-6 complete (~50% of planned roadmap)

## Features so far
- Fetches real game data from [IGDB](https://www.igdb.com/) (cover art, genres, release year)
- Tinder-style swipeable card UI with drag gesture and fly-off animation
- Swipe history saved to a local SQLite database
- Automatic background queue refilling — new games load before you run out, with no UI freeze
- Dynamic, fully re-themeable UI (dark/light, JSON-configurable color palettes)
- Settings screen: live theme switching, data source enable/disable toggles
- Profile/Analytics tab: genre preference breakdown charts from your swipe history
- One-time onboarding welcome screen for first-time launch

## Tech stack
- **Python 3.11**
- **PySide6** (Qt) — desktop UI, no web/JS involved
- **SQLAlchemy** — ORM over a local SQLite database
- **matplotlib** — analytics charts, embedded in the Qt UI
- **IGDB API** (via Twitch OAuth) — primary game data source

## Project structure
```
game-tindr/
├── main.py                 # entry point
├── config/                 # settings loader, config.json (gitignored) / config.example.json
├── core/                   # database models, DB session, game repository, queue service, analytics
├── sources/                # pluggable game data source classes (IGDB now, more later)
├── ui/                      # PySide6 views: main window, swipe card, settings, profile, onboarding, themes
├── utils/                   # shared logging and HTTP client helpers
├── requirements.txt
```

## Setup
1. Clone the repo and create a virtual environment:
   ```
   python -m venv .venv
   source .venv/Scripts/activate   # Windows (git-bash)
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get IGDB API credentials (free): register an app at
   [dev.twitch.tv/console](https://dev.twitch.tv/console) (IGDB is owned by Twitch).
4. Copy `.env.example` to `.env` and fill in your `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET`.
5. Copy `config/config.example.json` to `config/config.json` if you want to customize
   defaults (optional — the app falls back to the example file if missing).
6. Run it:
   ```
   python main.py
   ```

## How it works, briefly
- **Data sources** (`sources/`) each implement a common `GameDataSource` interface, so
  adding a new source (Steam, RAWG, etc. — planned) never requires touching existing code.
- **`GameQueueService`** manages what game you see next, pulling from a persistent queue
  and refilling from active sources in a background thread when running low — so the app
  never freezes waiting on a network call.
- **Swipes** are recorded as `SwipeRecord` rows, which are the training data for future
  recommendation logic (planned) and the current basis for the Profile tab's analytics.
- **Theming** is fully data-driven: `ui/themes/*.json` files hold color palettes, applied
  onto a single shared QSS template — no per-widget hardcoded styling.

## What's next
See `prompt.md` for the full roadmap. Remaining phases: recommendation engine (content-based,
then trainable ML), additional data sources, packaging into a standalone executable.

## License
Personal project, private repository.
