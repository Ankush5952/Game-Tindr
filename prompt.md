# Game Tindr — Project Roadmap & AI Collaboration Guide

## 0. Purpose of this document
This file is the instruction manual for an AI assistant (Claude, GPT, etc.) helping build this
project. Read this in full before writing or suggesting any code. It defines the rules of
engagement, the tech stack, the architecture, and the phase-by-phase build order.

## 1. Ground rules for the AI (non-negotiable)
1. **Guide, don't build.** Do NOT write/edit project files unless the user explicitly says so
   in that message (e.g. "go ahead and create that file"). Default mode is: explain, then hand
   over code in chat for the user to type/paste themselves.
2. **Explain the "what" and the "why" before the "how".** Every suggestion must cover:
   - What we're building right now
   - Why it's needed at this point in the roadmap (not later, not never)
   - The code itself, with inline comments explaining non-obvious lines
3. **Ask before adding scope.** The AI may (and should) suggest improvements, extra features,
   or better libraries — but must get explicit user approval before it becomes part of the
   active plan. Suggestions go in the "Proposed Additions" log (§7) until approved.
4. **Beginner-friendly.** Assume the user knows Python/C++ syntax but NOT practical library
   usage or project structure conventions. Don't assume familiarity with design patterns,
   package managers, or tooling — explain those the first time they come up.
5. **No throwaway/hardcoded shortcuts.** Favor OOP and config-driven design over hardcoding,
   even in early phases, SPECIFICALLY so later features never require deleting or rewriting
   earlier code (see §3 Design Principles). "Simple" does not mean "hardcoded" — see §3.
6. **No placeholder bloat either.** Don't pre-build empty stubs for features we haven't reached.
   Structure the code so adding a feature later is additive (new file/class), not a rewrite —
   but only build what the current phase needs.
7. **Every phase ends with something runnable.** The user should be able to `python main.py`
   (or similar) and see/do something new after each phase, then commit to GitHub.

## 2. Project summary
**Game Tindr** is a personal desktop app that:
- Pulls game data from multiple sources (IGDB, Steam Store API, RAWG, etc.) and merges them
  into a unified game pool for discovery
- Presents games one at a time in a swipeable card UI (right = interested, left = not interested)
- Learns the user's taste from swipe history using a recommendation model that goes beyond
  simple genre/tag matching
- Has a Profile/Analytics tab showing visual breakdowns (e.g. "Action: 48%, Fantasy: 12%")
  of liked/disliped genres and tags, computed from the user's own swipe history
- Lets the user toggle which data sources are active
- Supports UI themes

**Cold start options** (what a new user sees before any swipes exist):
1. **Account login seeding:** User logs into Steam/itch.io/etc., app fetches their owned/played
   games and uses those as initial positive signals to bootstrap recommendations.
2. **Random assessment:** User skips login and swipes through a random sample of popular/diverse
   games to build initial preferences from scratch.

This is a personal/fun learning project (not production software), developed solo by the user
with AI guidance, committed regularly to a private GitHub repo. If a data source doesn't offer
a usable browsing/discovery API, we skip it — no scraping or TOS-violating workarounds.

## 3. Tech stack & why

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.x | User already knows the syntax |
| UI framework | **PySide6** (Qt for Python) | Real desktop app, not a web app — no HTML/CSS/JS needed. Theming via QSS (a CSS-like stylesheet, but simpler and scoped to widgets). Supports custom widgets + animations, which is exactly what a swipe-card needs. Huge docs/community, free for personal use. |
| Database | **SQLite** via **SQLAlchemy** (ORM) | No server to install/manage; SQLAlchemy lets you work with Python classes instead of raw SQL, which fits OOP better and is beginner-friendlier than hand-written SQL. |
| Config/secrets | Local `.env` file (via `python-dotenv`) + `config.json` for non-secret settings | API keys are NEVER written into source code, from the very first data source we build. `.env` is gitignored; `config.json` is gitignored but `config.example.json` (with defaults, no secrets) is committed. |
| Data source integrations | One class per source, all implementing a shared abstract base class (`GameDataSource`) | Adding a new source later = adding one new file that fills in the interface. Existing sources and core app code are never touched. |
| Game discovery sources | **IGDB** (primary — Twitch's game DB, huge catalog, free API), **Steam Store API** (browsing/search, not user accounts), **RAWG** (another game DB, free tier) | Multiple sources merged into one game pool. Sources without browsing APIs are skipped, not scraped. |
| Charts (Profile tab) | **matplotlib** (embedded in PySide6) or **PySide6 QtCharts** | Both are Python-native, no web charting libraries needed. |
| ML / recommendation engine | **scikit-learn** to start (simple, well-documented), can grow into embeddings/other approaches later | Avoids jumping straight into heavy deep-learning tooling before we even have data. |
| Packaging (later phase) | **PyInstaller** | Turns the finished app into a standalone .exe, no "web app" deployment needed. |

### Design principles that prevent future rework
- **Data source plugin pattern:** `GameDataSource` abstract base class defines `fetch_games()`,
  `get_source_name()`, etc. IGDB/Steam/RAWG are subclasses. The core app only ever talks to
  the abstract interface, never a specific source — so adding/removing/toggling sources
  never touches core code.
- **Config-driven source toggles:** which sources are "on" lives in `config.json`, read by
  a `SourceRegistry` at startup. Turning a source on/off is a settings-UI checkbox, not a
  code change.
- **No hardcoded credentials, ever:** the credential-loading pattern (`.env` + a `Settings`
  class) is built in Phase 1 alongside the very first data source, so there is never a
  "hardcoded keys we now need to remove" moment.
- **Data model classes, not dicts everywhere:** `Game`, `Genre`, `Tag`, `SwipeRecord`, `User`,
  `QueuedGame` are real classes (SQLAlchemy models double as this), so adding a new field
  later means adding one attribute to one class, not hunting through dict-key strings.
- **UI built from reusable, styled widgets:** the theme system (QSS) is introduced with the
  very first UI screen (Phase 3), not bolted on after multiple screens already exist with
  inline styling.
- **Session state persistence:** Games shown but not yet swiped are tracked (`QueuedGame`
  model with a "seen" flag). Closing the app mid-session doesn't lose progress — unswiped
  cards reappear on next launch.
- **Graceful error handling:** API failures, network errors, and corrupt data never crash
  silently. Every fallible operation surfaces a user-visible message (toast/status bar)
  and logs details for debugging. "Fail loudly and recoverably" is the rule.

## 4. Project structure (target shape — built up gradually, not all at once)
```
game-tindr/
├── main.py                    # entry point, launches the app
├── config/
│   ├── settings.py            # loads .env + config.json into a Settings object
│   ├── config.json            # gitignored — user's actual settings
│   └── config.example.json    # committed — defaults, shows available options
├── core/
│   ├── models.py              # SQLAlchemy models: Game, Genre, Tag, User, SwipeRecord, QueuedGame
│   └── database.py            # DB engine/session setup
├── sources/
│   ├── base_source.py         # abstract GameDataSource class
│   ├── igdb_source.py         # primary discovery source
│   ├── steam_source.py        # Steam Store browsing API
│   ├── rawg_source.py         # RAWG game database
│   └── registry.py            # SourceRegistry — knows which sources exist & are enabled
├── ml/
│   └── recommender.py         # recommendation engine (starts simple, grows over phases)
├── ui/
│   ├── main_window.py
│   ├── swipe_card_widget.py
│   ├── settings_view.py
│   ├── profile_view.py
│   ├── onboarding_view.py     # cold start: login or random assessment choice
│   └── themes/
│       ├── dark.qss
│       └── light.qss
├── utils/
│   ├── logger.py              # logging setup (file + console)
│   └── http_client.py         # shared HTTP client with retry logic, error handling
├── .env                       # gitignored — real API keys live here
├── .env.example               # committed — shows what keys are needed, no real values
├── .gitignore
├── requirements.txt
└── prompt.md                  # this file
```

## 5. Phased roadmap

Each phase = one focused chunk of work with a clear "done" state and a git commit.

**Phase 0 — Environment setup**
- Install Python venv, PySide6, SQLAlchemy, python-dotenv
- Initialize git repo, create `.gitignore`, `requirements.txt`
- Confirm `python main.py` runs an empty PySide6 window
- Why first: nothing else works without a working environment; catching setup issues early is cheap.

**Phase 1 — Core data models + config/secrets pattern + utils**
- Define `Game`, `Genre`, `Tag`, `User`, `SwipeRecord`, `QueuedGame` as SQLAlchemy models
- Build `Settings` class that loads `.env` (secrets) + `config.json` (preferences)
- Create `utils/logger.py` (file + console logging) and `utils/http_client.py` (shared
  requests wrapper with retry logic and error handling)
- Why now: every later phase (sources, UI, ML) needs somewhere to read/write data,
  credentials, and make HTTP calls. Doing this first means no phase after this ever
  hardcodes anything or reinvents error handling.

**Phase 2 — First data source: IGDB**
- Build abstract `GameDataSource` base class
- Implement `IGDBSource` (IGDB has a well-documented API with huge game catalog, free for
  personal use via Twitch OAuth) — best source to start with for game discovery
- Build `SourceRegistry` that reads `config.json` to know which sources are active
- Why IGDB first, and why the registry now: IGDB has the largest catalog and cleanest API,
  making it ideal to prove the pattern works. Building the registry now (with only 1 source)
  means adding source #2 later is trivial and doesn't touch this code.

**Phase 3 — UI shell + theme system**
- Main window with navigation (Swipe / Profile / Settings tabs)
- QSS theme loader, at least one theme (dark) working end-to-end
- Why now, not later: introducing theming after 3 screens already have inline styles means
  redoing those screens. Doing it with screen #1 means every future screen is theme-ready.

**Phase 4 — Swipe card mechanic**
- Custom swipeable card widget (drag gesture, animate off-screen, emit left/right signal)
- Wire swipes to write `SwipeRecord` rows to the database; track unswiped cards via
  `QueuedGame` so session state persists across app restarts
- Why now: this is the core interaction loop; once it exists we have real user data to build
  everything else (analytics, ML) on top of.
- NOTE: Qt animations (QPropertyAnimation) are non-trivial — expect this phase to take
  longer than others. Break into sub-steps: static card first, then drag, then animation.

**Phase 5 — Onboarding / cold start**
- Build `onboarding_view.py`: two paths — "Login to seed preferences" vs "Start random
  assessment"
- Login path: connect to Steam/itch.io user account API to fetch owned games, mark them as
  implicit positive signals
- Random path: fetch a diverse sample of popular games from IGDB, present for swiping
- Why now: without this, a new user has no games to swipe on and recommendations have no
  starting point.

**Phase 6 — Settings: source on/off toggles**
- Settings UI reads/writes `config.json` via `SourceRegistry`
- Why now: with 1 source and the swipe loop working, this is a small, safe feature to
  validate the config-driven pattern before more sources exist.

**Phase 7 — Profile / Analytics tab**
- Query `SwipeRecord` history, compute % breakdowns per genre/tag for liked vs disliked
- Render as charts (matplotlib or QtCharts) inside the PySide6 UI
- Why now: we need real swipe data (from Phase 4) before analytics means anything.

**Phase 8 — Recommendation engine v1 (content-based)**
- Build a simple weighted genre/tag preference vector from swipe history
- Score not-yet-swiped games by similarity to that vector, surface top matches
- Why v1 is simple: establishes the recommendation "slot" in the architecture (a
  `Recommender` class the UI calls) before adding real ML — later versions swap the
  internals, not the interface.

**Phase 9 — Recommendation engine v2 (trainable ML model)**
- Use scikit-learn to train a model (e.g. logistic regression / gradient boosting) on
  engineered features from swipe history, replacing/augmenting the v1 heuristic
- Add retraining trigger (e.g. every N new swipes) — the "closed loop"
- Why after v1: you need a working baseline and real data volume before ML tuning is useful.

**Phase 10 — Additional data sources**
- Add Steam Store API, RAWG sources (one at a time), each just a new `GameDataSource`
  subclass + registry entry
- Merge games from multiple sources into unified pool, deduplicate by name/platform
- Why now: the plugin pattern from Phase 2 is proven; this phase should feel mechanical.
- NOTE: only sources with usable browsing/discovery APIs are added. If a source doesn't
  have one, skip it — no scraping.

**Phase 11 — Packaging & polish**
- PyInstaller build into a standalone executable
- UI polish, more themes, README writeup

## 6. Coding conventions to keep things maintainable
- One class per file where reasonable; one clear responsibility per class
- Type hints on function signatures (helps catch mistakes early, good habit to build)
- Docstrings explaining *why* a class/method exists, not just what it does
- Commit after every phase (or sub-step within a phase) with a clear message
- Never commit `.env` or real API keys — only `.env.example`

## 7. Proposed additions log (needs user approval before entering the roadmap)
_(AI: log ideas here as you think of them during development, with a one-line pitch. Do not
implement until the user approves and this entry is moved into §5.)_

- (empty — nothing proposed yet)

## 8. Open questions to resolve with the user before/at relevant phases
- Exact visual style/theme preferences (colors, layout) — resolve at Phase 3
- Which account login APIs (Steam, itch.io, etc.) to support for cold-start seeding —
  resolve at Phase 5

## 9. Future possibilities (parked, not in active roadmap)
These ideas require resources or complexity beyond a personal project scope, but are recorded
here in case circumstances change:

- **Cross-user data for recommendations:** training on aggregated public data (Steam reviews,
  tags from other users) to improve cold-start recommendations. Would require either a large
  dataset or your own user base — not feasible for a solo personal project currently.
- **Mobile app version:** would require learning a new framework (Kivy for Python mobile, or
  a full rewrite in Flutter/React Native). PySide6 is desktop-only.
