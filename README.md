# Ultimate Bot — Starter Pack
A starter "Ultimate Bot" for Telegram (developer + admin + safety) — ready to run locally as a foundation. 
This repo contains core modules: admin moderation, media library (user-uploaded), safety (SOS), owner tools and basic persistence (SQLite).

**Notable:** This starter avoids piracy features. It is designed to be extended. Use responsibly; secure your BOT_TOKEN and OWNER_ID.

## Quick start (local)
1. Copy `.env.example` → `.env` and fill `BOT_TOKEN` and `OWNER_ID`.
2. Create and activate virtualenv: `python -m venv .venv && . .venv/bin/activate`
3. Install deps: `pip install -r requirements.txt`
4. Run: `python main.py`
5. Add the bot to a chat (as admin for moderation features).

## Files
- `main.py` — bot entry, router wiring, polling loop
- `modules/admin.py` — moderation commands (ban, kick, mute, warn, purge, setrules)
- `modules/media.py` — upload/find/send simple media library (user-owned files)
- `modules/safety.py` — SOS / trust / escort stubs
- `modules/owner.py` — owner-only tools (stats, logs, reload stub, export)
- `db.py` — tiny sqlite wrappers for persistence
- `docker-compose.yml` — quick dev stack (optional)
- `.env.example` — env template

## Security & notes
- Keep `.env` secret. Never commit real tokens.
- OWNER_ID is a Telegram numeric user id — owner-only commands check this.
- This starter uses SQLite for ease of use. For production switch to Postgres + Redis for jobs + S3 for storage.
- See `README.md` and docstrings inside modules for extending features.

(( • ))
