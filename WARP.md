# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

- Setup (from README):
```bash path=null start=null
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
- Run the app:
```bash path=null start=null
python main.py
```
- Lint/typecheck: none configured in this repo.
- Tests: no test suite configured. If tests are later added, prefer project-provided commands.

Default admin login (from README): admin / admin1

## High-level architecture

- Entry point: `main.py`
  - Initializes CustomTkinter (dark mode), ttk theme, and a root `CTk` window.
  - Creates `Database` and initializes schema, status bar clock, and orchestrates view transitions:
    splash → login → admin or student dashboard.
- Configuration: `app/config.py`
  - Central colors (black & gold theme), fonts, and `APP_INFO` (title/version).
- Data layer: `app/database.py`
  - SQLite database at `data/app.db` (auto-created). Tables: Admin, Students, Batches, Attendance, Fees, Performance, Messages.
  - Provides CRUD/query helpers (e.g., `list_students`, `upsert_batch`, `mark_attendance`, `record_payment`, `get_fees`, `send_message`). Seeds default admin on first run.
- Auth controller: `app/controllers/auth.py`
  - `login(db, user_type, username, password)` dispatches to Admin vs Student lookup; returns normalized `(type, record)` on success.
- UI composition: `app/ui/*`
  - `splash.py`: transient `CTkToplevel` with progress bar and centering logic.
  - `login.py`: role switcher (admin/student), username/password form; on success calls controller.
  - `components.py`: reusable `GoldButton`, metric `Card`, and `style_treeview` for ttk tables.
  - `admin_dashboard.py`: `AdminApp` shell with sidebar and view registry. Key views expose `refresh()` and use the data layer:
    - Dashboard: shows aggregate metrics (students, batches, fees, attendance%).
    - Students: table + dialogs for add/edit/delete with CSV-friendly columns.
    - Batches: simple upsert/list/delete.
    - Attendance: mark present/absent for a date.
    - Fees: record payments and show total collected.
    - Performance: record subject marks per student.
    - Messages: send broadcast messages (persisted to `Messages`).
    - Reports & Backup: CSV export of students; DB backup to `backups/backup.db`.
    - Settings: includes Logout action.
  - `student_dashboard.py`: `StudentApp` with tabbed views (Home, Timetable placeholder, Attendance history, Marks, Fees summary, Announcements from `Messages`, Profile).
- Assets & data dirs
  - On startup, `main.py` ensures `data/` and `assets/icons/` exist. CSV exports and backups are user-initiated via the Admin Reports view.
