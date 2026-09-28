# Game Tindr

A personal desktop app that turns game discovery into a Tinder-style swiping experience.
Swipe right on games you're interested in, left on ones that aren't your taste — the app
learns your preferences from your swipe history and recommends games tailored to you.

This is a solo learning project, built with AI guidance (see `prompt.md` for the full
roadmap and design philosophy), not production software.

## Current status: Full roadmap (Phases 0-11) complete

Packaged as a standalone Windows executable — see "Building a standalone executable" below.
Phase 10 (additional data sources) was evaluated (RAWG implemented and tested end-to-end) and
deliberately declined in favor of staying single-source; see `prompt.md` Phase 10 for the
full reasoning. The plugin architecture that would support a future source remains in place.

## Features
- Fetches real game data from [IGDB](https://www.igdb.com/) (cover art, genres, tags,
  description, release year)
- Tinder-style swipeable card UI with drag gesture and fly-off animation
- Swipe history saved to a local SQLite database; queued-but-unswiped games persist across
  restarts instead of being silently discarded
- Automatic background queue refilling — new games load before you run out, with no UI freeze
- Dynamic, fully re-themeable UI (dark/light, JSON-configurable color palettes)
- Settings screen: live theme switching, data source enable/disable toggles
- Profile/Analytics tab: genre preference breakdown charts (auto-refreshing, theme-aware)
  from your swipe history
- One-time onboarding welcome screen for first-time launch
- Real recommendation engine (`RecommendationService`): a trained logistic regression model
  (scikit-learn) learns from swipe history using genre preference, tag preference, and
  description-embedding similarity (via `sentence-transformers`) as features. Falls back to a
  hand-rolled heuristic for brand new users without enough swipes to train on yet.
  Automatically retrains every 20 new swipes (the "closed loop").
- The live swipe queue is ranked by this recommendation score — higher-predicted games surface
  earlier in your swipe session, not in arbitrary/random fetch order.
- Packaged as a standalone `.exe` via PyInstaller — runs without Python/venv installed.

## Tech stack
- **Python 3.11**
- **PySide6** (Qt) — desktop UI, no web/JS involved
- **SQLAlchemy** — ORM over a local SQLite database
- **matplotlib** — analytics charts, embedded in the Qt UI
- **scikit-learn** — trained logistic regression recommender model
- **sentence-transformers** — description embeddings for semantic similarity scoring
- **PyInstaller** — standalone executable packaging
- **IGDB API** (via Twitch OAuth) — game data source

## Project structure
```
game-tindr/
├── main.py                 # entry point
├── config/                 # settings loader, config.json (gitignored) / config.example.json
├── core/                   # database models, DB session, game repository, queue service,
│                            # analytics service, embedding service, recommender heuristic,
│                            # model trainer, unified recommendation service
├── sources/                # pluggable game data source classes (IGDB active; plugin pattern
│                            # supports adding more if a genuinely better source is found)
├── ui/                      # PySide6 views: main window, swipe card, settings, profile, onboarding, themes
├── utils/                   # shared logging, HTTP client, and path-resolution helpers
│                            # (paths.py: dev vs packaged-exe path handling)
├── requirements.txt
├── recommender_model.pkl   # trained model, gitignored (generated data, not source)
└── prompt.md                # full project roadmap and AI collaboration guide
```

## Setup (running from source)
1. Clone the repo and create a virtual environment:
   ```
   python -m venv .venv
   source .venv/Scripts/activate   # Windows (git-bash)
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Note: this installs PyTorch (via `sentence-transformers`) — a genuinely large download.
   The first run will also download a small pretrained embedding model (~80MB) automatically.
3. Get IGDB API credentials (free): register an app at
   [dev.twitch.tv/console](https://dev.twitch.tv/console) (IGDB is owned by Twitch).
4. Copy `.env.example` to `.env` and fill in your `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET`.
5. Copy `config/config.example.json` to `config/config.json` if you want to customize
   defaults (optional — the app falls back to the example file if missing).
6. Run it:
   ```
   python main.py
   ```

## Building a standalone executable
```
pip install -r requirements.txt   # includes pyinstaller
pyinstaller --name GameTindr --onefile --windowed --add-data "config/config.example.json;config" --add-data "ui/themes;ui/themes" main.py
```
Then copy your `.env` file next to the built `dist/GameTindr.exe` (it isn't bundled, since it
holds your personal API credentials). The exe creates its own database, log file, config.json,
and trained model file next to itself on first run — no separate install step needed on
another machine, beyond providing a `.env` with valid IGDB credentials.

## How it works, briefly
- **Data sources** (`sources/`) each implement a common `GameDataSource` interface, so
  adding a new source never requires touching existing code — proven by plugging RAWG in and
  back out cleanly during evaluation (see `prompt.md` Phase 10).
- **`GameQueueService`** manages what game you see next, pulling from a persistent queue
  and refilling from active sources in a background thread when running low — so the app
  never freezes waiting on a network call. Newly fetched batches are ranked by recommendation
  score before being queued. Queue entries are only removed once a swipe is actually recorded,
  so closing the app mid-session never silently discards a queued game.
- **Swipes** are recorded as `SwipeRecord` rows — the training data behind the Profile tab's
  analytics and the recommendation model.
- **`RecommendationService`** is the single entry point for recommendation scoring. It uses a
  trained scikit-learn model (features: average genre weight, average tag weight, description
  embedding similarity to liked games) once enough swipe data exists, automatically retraining
  every 20 new swipes; falls back to a hand-rolled heuristic (`RecommenderService`) for very
  new users. Nothing else in the app needs to know which is active.
- **Description embeddings** (`embedding_service.py`) use a pretrained sentence-transformer
  model to convert each game's description into a vector capturing its meaning, enabling
  "similar premise, different wording" matches that plain genre/tag matching can't catch.
- **Theming** is fully data-driven: `ui/themes/*.json` files hold color palettes, applied
  onto a single shared QSS template and reused directly by matplotlib chart styling — no
  per-widget or per-chart hardcoded colors.
- **Packaging** (`utils/paths.py`) distinguishes read-only bundled resources (themes, example
  config — extracted to a temp folder by PyInstaller at runtime) from writable app data
  (database, logs, trained model, personal config — which must live next to the .exe to
  persist between launches, not in PyInstaller's temporary extraction folder).

## Known limitations (by design)
- Recommendation quality depends entirely on the solo user's own swipe history — there's no
  cross-user data (parked in `prompt.md` §9 as a future possibility, not currently feasible).
- Description similarity is computed against a single averaged "liked taste vector," which is
  a blunter signal than tag/genre-level specificity — validated as a real, believable outcome
  (not a bug) rather than something actively being tuned further right now.
- Single data source (IGDB) by deliberate choice — see Phase 10 in `prompt.md` for why a
  second source (RAWG) was built, tested, and then declined rather than kept.
- Recommendations don't yet use the game's *name* itself as a pattern signal (e.g. "if you
  like A, you'll likely like B") — parked as a future possibility requiring either
  collaborative filtering (needs many users' data) or an LLM with gaming-domain knowledge.
- Editing/undoing individual past swipes, and a clean "reset swipe history" feature, are
  parked as post-roadmap additions — both require care around the trained model (it would
  need retraining/resetting alongside any swipe-data change; see `prompt.md` §9).

## What's next
The original roadmap (`prompt.md`) is complete. Future work is tracked in `prompt.md` §9
("Future possibilities") as an open-ended backlog, not a numbered phase plan — including
swipe history editing/reset, a differentiated second data source if one is ever found, and
name/premise-pattern recommendations.

## License
Personal project, private repository.
