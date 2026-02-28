# AGENTS.md — Water Reminder Desktop App

## Project Overview

PySide6 desktop application for water drinking reminders with Material Design UI.
Python 3.11, conda environment (`water`), SQLite database, frameless window with custom title bar.

## Quick Start

```bash
conda activate water
python main.py                              # Run app
python main.py --smoke-test                 # Build all objects, exit without event loop
QT_QPA_PLATFORM=offscreen python main.py    # Headless (CI / no display)
```

## Build & Test Commands

```bash
# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_database.py

# Run a single test by name
pytest tests/test_database.py::test_add_intake -v

# Smoke test (validates app boots without crashing)
python main.py --smoke-test

# Windows packaging
pyinstaller WaterReminder.spec
pyinstaller WaterReminder_onefile.spec      # Single-file build
```

No linter/formatter config exists. No mypy/ruff/flake8 config. Run `pytest` for validation.

## Architecture

```
main.py              — Entry point: WaterApp orchestrator (creates objects, wires signals, runs event loop)
app/
  config.py          — AppConfig dataclass, JSON load/save with defensive parsing
  database.py        — SQLite Database class (intake table, daily totals, recent records)
  main_window.py     — Frameless QMainWindow with custom resize logic
  core/
    paths.py         — Platform-aware paths (app dir, config, db, resources)
    reminder.py      — ReminderEngine (QTimer-based, start/pause/resume/stop)
    theme.py         — ThemeManager (qt-material, light/dark with CSS overrides)
    tray.py          — TrayManager (system tray icon, quick drink menu)
    sound.py         — SoundManager (QSoundEffect, auto-generates default WAV)
    autostart.py     — AutoStartManager (Windows registry / Linux .desktop)
  pages/
    dashboard.py     — DashboardPage (circular progress, quick-add buttons, recent list)
    history.py       — HistoryPage (QChart bar chart, goal line, stats cards)
    settings.py      — SettingsPage (interval, goal, theme, sound, autostart)
  widgets/
    circular_progress.py — CircularProgress (animated ring, QPropertyAnimation)
    sidebar.py           — Sidebar + SidebarButton (custom-painted navigation)
    title_bar.py         — TitleBar + TitleBarButton (drag, min/max/close)
    toast_reminder.py    — ToastReminder (slide-in notification with drink/dismiss)
  resources/
    icons/
    sounds/
    styles/
```

**Signal wiring**: All cross-component communication uses Qt Signals/Slots, wired in `WaterApp._wire_signals()`.
**Graceful import fallback**: `main.py` wraps page imports in try/except, providing stub widgets if imports fail.

## Code Style Guidelines

### Imports

- `from __future__ import annotations` at top of core/data modules (config, database, reminder, sound, autostart, paths)
- UI modules (pages, widgets, main_window) do NOT use `from __future__ import annotations`
- Standard library first, then PySide6, then local (`app.xxx`)
- Relative imports inside `app/` package (e.g., `from .core.paths import get_config_dir`)
- Absolute imports from `main.py` (e.g., `from app.config import AppConfig`)

### Naming

- **Classes**: PascalCase (`ReminderEngine`, `SoundManager`, `DashboardPage`)
- **Methods/functions**: snake_case (`get_today_total`, `_wire_signals`)
- **Private members**: single underscore prefix (`self._enabled`, `self._timer`)
- **Constants**: UPPER_SNAKE_CASE (`APP_NAME`, `_OVERRIDES_START`)
- **Signals**: snake_case descriptive (`water_added`, `remind_triggered`, `theme_changed`)
- **Qt object names**: camelCase strings (`"historyPage"`, `"settingsPage"`, `"Container"`)

### Type Annotations

- Return types on all public/private methods in core modules: `def add_intake(...) -> int:`
- Parameter types on core module methods
- UI modules (pages, widgets) are inconsistent — some have types, most don't
- Use `X | None` union syntax (Python 3.10+), not `Optional[X]`
- Use `typing.cast()` for sqlite3.Row access and JSON parsing
- Use `list[dict]`, `dict[str, int]` (lowercase generics)

### Error Handling

- Defensive: silent `except Exception: return` for non-critical failures (autostart, window geometry save)
- Explicit `raise ValueError(...)` for invalid input in core logic (database, reminder engine)
- Try/except wrapping for page imports in `main.py` with fallback stub classes
- Input validation via explicit type coercion: `int(amount_ml)`, `bool(enabled)`, `max(1, int(n))`

### Patterns

- **Discard unused return values**: `_ = path.parent.mkdir(...)`, `_ = self.conn.execute(...)`
- **Guard clauses**: early return when objects are None — `if self.db is None: return`
- **Signal-slot wiring**: centralized in one method, not scattered
- **Stateless utility classes**: `ThemeManager`, `AutoStartManager` use `@staticmethod` only
- **QObject ownership**: pass `parent` to QObject/QWidget constructors where appropriate
- **Stylesheet strings**: inline multi-line strings in `setStyleSheet()` calls

### UI Conventions

- **Color palette**: Blue accent `#2196F3`, light bg `#FAFAFA`, borders `#E0E0E0`, muted text `#757575`
- **Font**: "Segoe UI" / "system-ui" / "sans-serif"
- **Border radius**: 10-16px for cards/containers, 22px for pill buttons
- **Custom painting**: override `paintEvent()`, use QPainter with antialiasing
- **Animations**: QPropertyAnimation with OutCubic easing, 300-800ms duration

### Database

- SQLite via `sqlite3`, stored at platform-specific app data directory
- Timestamps as Unix epoch integers (`ts_utc`), converted to local time for display
- Schema versioning via `meta` table
- All queries use parameterized statements (no string formatting)

## Dependencies

- **PySide6** >= 6.6.0 — Qt for Python (GUI, signals, multimedia)
- **qt-material** >= 2.14 — Material Design themes
- **pyqttoast** >= 1.2.0 — (available but custom ToastReminder used instead)
- **pyinstaller** >= 6.0 — Windows packaging
- **pytest** >= 7.0 — Testing

## Key Conventions for Agents

1. **Never suppress errors silently in core logic** — raise ValueError for bad input
2. **Always wire signals in `_wire_signals()`** — don't connect signals in constructors
3. **Use defensive None checks** before accessing `self.db`, `self.config`, etc.
4. **Match existing stylesheet patterns** — inline CSS strings, same color tokens
5. **Test with `--smoke-test`** after structural changes to verify boot sequence
6. **Plan files**: create `plan_<feature>.md` for each new feature, mark steps with check/X on completion
7. **Timestamps**: always UTC epoch int in database, local conversion only at display time
8. **New pages**: must define matching Signal stubs as fallback in `main.py` try/except blocks
9. **No linter config** — follow existing style by example, not by tool enforcement
10. **Conda environment** — `conda activate water` before any Python commands

## Tool usage Tips 
- Prohibited from directly asking questions to users, MUST use AskUserQuestion or functions.question tool. 
- Once you can confirm that the task is complete, MUST use AskUserQuestion or functions.question tool to make user confirm. The user may respond with feedback if they are not satisfied with the result, which you can use to make improvements and try again.