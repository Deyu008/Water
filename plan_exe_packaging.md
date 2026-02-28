# EXE Packaging Plan (Windows)

- [x] Step 1: Check toolchain availability (wine/xvfb/pyinstaller) - note: installed wine64 + wine32 + xvfb; pyinstaller available
- [x] Step 2: Prepare PyInstaller spec/build command with required data files - note: configured `--add-data app/resources` + `--collect-all qt_material`
- [x] Step 3: Build Windows `.exe` artifact - note: generated onedir/onefile and portable zip under `dist_win/`
- [x] Step 4: Verify artifact type and provide run instructions - note: `file` confirmed PE32+ x86-64 for Windows
- [x] Step 5: Rebuild onefile EXE after latest main/theme/shake updates - note: refreshed `dist_win/WaterReminder_onefile.exe` (Feb 28 04:01 UTC)

## Change Log
- 2026-02-28: Start Windows EXE packaging workflow
- 2026-02-28: Installed Wine toolchain and Windows embeddable Python environment
- 2026-02-28: Built `dist_win/WaterReminder_onefile.exe` and `dist_win/WaterReminder/WaterReminder.exe`
- 2026-02-28: Added portable archive `dist_win/WaterReminder_portable_win64.zip`
- 2026-02-28: Rebuilt `dist_win/WaterReminder_onefile.exe` after Wave 4/5 integration and smoke-test pass
