# Plan: Dark Mode Fix + System Theme Follow + Shake Reminder + UI Polish

## Wave 1: Theme Infrastructure ✅
- [x] Rewrite ThemeManager with color token system (_LIGHT/_DARK palettes)
- [x] Add theme_applied signal for broadcasting theme changes
- [x] Add "auto" mode support (detect system theme via QStyleHints)
- [x] Add connect_system_theme_watcher() for real-time system changes
- [x] Expand CSS overrides to cover Container, Sidebar, Pages, ScrollBar, etc.
- [x] Update AppConfig: theme accepts "auto", add shake_reminder_enabled

## Wave 2: Widget/Page Theme Fixes (parallel delegation)
- [ ] MainWindow: apply_theme(), Container objectName-based styling, _toggle_maximize fix
- [ ] TitleBar: apply_theme(), all colors from tokens
- [ ] Sidebar: apply_theme(), paintEvent tokens, emoji→QPainter icons, branding fix
- [ ] CircularProgress: apply_theme(), responsive text size
- [ ] DashboardPage: apply_theme(), recent list cleanup fix, all colors from tokens
- [ ] HistoryPage: StatsCard/chart/toggle themed, apply_theme()
- [ ] SettingsPage: apply_theme(), "Auto (System)" option, shake toggle, blockSignals fix
- [ ] ToastReminder: apply_theme(), paintEvent tokens

## Wave 3: New Features
- [x] ScreenShakeWidget: fullscreen overlay with shake animation
- [ ] System theme watcher integration in main.py

## Wave 4: main.py Integration
- [ ] Wire new signals: shake_changed, system theme watcher
- [ ] Add ScreenShakeReminder to reminder flow
- [ ] Theme auto mode startup logic
- [ ] Pass shake_reminder_enabled to load_settings

## Wave 5: Verification
- [ ] Smoke test (--smoke-test)
- [ ] Visual verification notes
