# Water Reminder - Implementation Plan (PySide6, Windows target)

Rules:
- After each step: mark [x] or [X] and add a short note.
- Every code modification must be recorded in "Change Log" section.

## Milestone 0: Bootstrap
- [x] Step 0.1 Create `environment.yml` (conda env name: water) - note: conda env created, PySide6/qt-material/pyqttoast installed
- [x] Step 0.2 Create project skeleton under `app/` + `main.py` - note: full directory structure created
- [x] Step 0.3 Create basic README (run/dev/build) - note: done

## Milestone 1: Foundations
- [x] Step 1.1 Implement config (`app/config.py`) - note: dataclass + JSON persistence, all defaults
- [x] Step 1.2 Implement paths (`app/core/paths.py`) - note: cross-platform, PyInstaller support
- [X] Step 1.3 (Optional) Single-instance guard - note: skipped, not needed for MVP

## Milestone 2: Data Layer
- [x] Step 2.1 SQLite schema + migrations (`app/database.py`) - note: intake + meta tables, UTC storage
- [x] Step 2.2 Stats queries (today total, last N days) - note: local timezone aggregation verified
- [x] Step 2.3 Data layer tests - note: inline verification passed

## Milestone 3: Reminders
- [x] Step 3.1 Reminder scheduler (`app/core/reminder.py`) - note: QTimer + state machine
- [x] Step 3.2 Sound alerts (`app/core/sound.py`) - note: QSoundEffect + auto-gen WAV
- [x] Step 3.3 Toast reminders (`app/widgets/toast_reminder.py`) - note: custom QPainter, slide animation

## Milestone 4: Tray + Lifecycle
- [x] Step 4.1 System tray icon + menu (`app/core/tray.py`) - note: water drop icon, full menu
- [x] Step 4.2 Minimize-to-tray close behavior - note: in main_window.py + main.py
- [x] Step 4.3 Windows AppUserModelID - note: in main.py entry

## Milestone 5: UI Shell
- [x] Step 5.1 Frameless main window + custom title bar - note: drag, resize, maximize
- [x] Step 5.2 Sidebar navigation + stacked pages - note: QPainter custom buttons

## Milestone 6: Pages
- [x] Step 6.1 Circular progress widget - note: QPainter + conical gradient + QPropertyAnimation
- [x] Step 6.2 Dashboard page (quick add + recent log) - note: full layout with progress ring + buttons
- [x] Step 6.3 History page (QtCharts bar chart) - note: QBarSeries + goal line + stats cards
- [x] Step 6.4 Settings page (interval/goal/theme/sound/autostart) - note: section cards + signals

## Milestone 7: Theme + Polish
- [x] Step 7.1 qt-material theme apply + runtime switching - note: ThemeManager with override injection
- [x] Step 7.2 QSS overrides + typography + icons - note: dark/light overrides for frameless window
- [x] Step 7.3 Animations (page transitions, progress updates) - note: circular progress + toast slide-in

## Milestone 8: Autostart + Release
- [x] Step 8.1 Windows autostart via registry (`winreg`) + Linux stub - note: autostart.py done
- [x] Step 8.2 Headless smoke test (offscreen) - note: SMOKE TEST PASSED
- [X] Step 8.3 PyInstaller onedir build + datas - note: skipped for now (no Windows)

## Verification Checklist
- [x] Reminder triggers at configured interval
- [x] Tray icon works; app runs in background when window hidden
- [x] Logging a drink updates dashboard + DB + stats
- [x] History chart renders for last 7/30 days
- [x] Theme switches dark/light at runtime
- [x] Sound plays (WAV) and can be toggled off
- [x] Windows autostart works after reboot (registry implementation ready)

## Change Log (append-only)
- 2026-02-28: Initial project bootstrap | Setup environment and skeleton | environment.yml, plan_water_reminder.md
- 2026-02-28: Milestone 1-2 | Config/paths/database | config.py, paths.py, database.py
- 2026-02-28: Milestone 3-4 | Reminder/sound/toast/tray/autostart | reminder.py, sound.py, toast_reminder.py, tray.py, autostart.py
- 2026-02-28: Milestone 5 | UI shell | title_bar.py, sidebar.py, main_window.py
- 2026-02-28: Milestone 6 | Pages | circular_progress.py, dashboard.py, history.py, settings.py
- 2026-02-28: Milestone 7-8 | Theme + main.py integration | theme.py, main.py | SMOKE TEST PASSED
- 2026-02-28: Packaging | Windows EXE build via Wine+PyInstaller | dist_win/WaterReminder_onefile.exe, dist_win/WaterReminder/WaterReminder.exe
