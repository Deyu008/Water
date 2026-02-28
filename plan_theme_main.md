# Plan: Theme Manager + Main Entry Wiring

- [x] 1) 通读并核对核心模块接口（config/database/reminder/sound/tray/autostart/main_window/pages/toast）（完成：已确认信号与方法签名，识别 settings 页面可能缺失）
- [x] 2) 新建并初始化本计划文件（完成：建立执行追踪与结果记录）
- [ ] 3) 实现 `app/core/theme.py`（qt-material 深浅主题 + 覆盖样式）
- [ ] 4) 实现 `main.py`（应用生命周期、全量信号连接、close-to-tray、smoke test）
- [ ] 5) 运行 LSP 诊断与离屏验证（theme/main smoke test），修复问题后回填结果

## Change Log（append-only）
- 2026-02-28: 新增计划文件 `plan_theme_main.md`，用于主题与入口集成开发追踪。
