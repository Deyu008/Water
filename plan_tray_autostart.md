# Plan: Tray + Autostart

- [x] 1) 勘察 `app/core` 现有结构与接口约束（完成：`core` 仅有 `paths.py`，可独立新增模块）
- [x] 2) 实现 `app/core/tray.py`（托盘图标、菜单、信号、双击显示、通知）（完成：菜单结构与信号按需求实现）
- [x] 3) 实现 `app/core/autostart.py`（Windows 注册表 + Linux `.desktop`）（完成：双平台启停与状态查询已实现）
- [ ] 4) 运行离屏验证脚本，确认导入与实例化正常
- [ ] 5) 对新增文件运行 LSP 诊断并清理问题
- [ ] 6) 回填计划执行结果（逐项打勾并附简短说明）
