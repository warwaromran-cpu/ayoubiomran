# Optional local project-record backend

`wooden_backend.py` is a supervised local SQLite record and validation tool. It does not draft CAD or independently verify source documents. The owner initializes a clean local database for the recipient; no database snapshot is included in this package.

Run `python backend/wooden_backend.py --help` for commands. Use `init-project`, `put`, `check`, and `summary` with project-scoped IDs. Follow `RECORDS.md` for record types and validation, and `VERIFICATION.md` for review boundaries.

Keep the database under `backend/data/` and out of Git. Never use test fixtures for real project records. Original sources and deliverables remain files referenced by structured records. Before adopting the backend, review `AGENTS.md` and ensure that the recipient's repository register and workshop profile are the active sources of truth.
