# Plan: configuration_database_layer

- [x] 1. 检查目录与目标文件状态（确认是否需新建文件）- 已确认 3 个目标文件不存在，采用新建实现。
- [x] 2. 实现 `app/core/paths.py`（跨平台路径、目录自动创建、资源路径解析）- 已完成 Windows/Linux 路径与 `_MEIPASS` 兼容。
- [x] 3. 实现 `app/config.py`（`dataclass` + JSON 持久化 + 默认值）- 已完成默认值、`load/save`、字段过滤与容错。
- [x] 4. 实现 `app/database.py`（SQLite schema、CRUD、本地时区聚合）- 已完成表结构、索引、近期记录与本地时区日聚合。
- [x] 5. 运行静态诊断与给定验证脚本并记录结果 - `lsp_diagnostics` 清洁；内联脚本输出 `ALL TESTS PASSED`。
- [x] 6. 回写修改记录（文件级变更摘要，便于论文追踪）- 已记录如下：

## 变更记录（trace）

- `app/core/paths.py`
  - 新增跨平台数据目录解析：Windows `%APPDATA%/WaterReminder`，Linux `~/.local/share/WaterReminder`。
  - 新增 `get_config_dir/get_db_path/get_log_path/get_resource_path`，首次访问自动建目录。
  - `get_resource_path` 支持 PyInstaller `_MEIPASS` 与开发模式项目根目录。

- `app/config.py`
  - 新增 `AppConfig` 数据类与默认值：`daily_goal_ml/reminder_interval_min/theme/sound_enabled/autostart_enabled/reminder_sound/window_geometry`。
  - 新增 `load/save/get_config_path`，配置以 JSON 持久化到 `get_config_dir()/config.json`。
  - 新增强健的类型容错转换（int/bool/window_geometry），异常或坏配置回退默认值。

- `app/database.py`
  - 新增 SQLite `Database` 层，初始化 `intake/meta` 表与 `idx_intake_ts` 索引。
  - 新增 `add_intake/delete_intake/get_today_total/get_daily_totals/get_recent/close`。
  - 严格执行“存 UTC 时间戳、按本地时区聚合日数据”的边界计算逻辑。
