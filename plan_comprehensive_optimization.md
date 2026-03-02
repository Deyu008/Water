# Water Reminder 综合优化计划执行记录

## 一、Bug 修复
- [x] 1.1 配置文件原子写入 — tempfile + os.replace() 原子替换
- [x] 1.2 页面导入异常日志记录 — except 分支添加 logger.warning(exc_info=True)
- [x] 1.3 QMenu parent — QMenu 的 parent 要求 QWidget, TrayManager 是 QObject, 改为 hide() 中 deleteLater()
- [x] 1.4 MainWindow lambda → 命名方法 _on_theme_applied
- [x] 1.5 最大化状态下 resize 保护 — mousePressEvent 开头 isMaximized() 检查
- [x] 1.6 autostart 错误日志记录 — 所有 except 分支添加 logger.warning/debug
- [x] 1.7 Linux .desktop Exec 引号 — 新增 _launch_command_desktop() 方法，不加引号

## 二、暗色模式/主题打磨
- [x] 2.1 ScreenShakeReminder 主题适配 — 新增 shake_* token, apply_theme() 订阅信号
- [x] 2.2 ThemeManager._build_overrides 防御性 — c["token"] → t("token") 使用 .get()

## 三、性能优化
- [x] 3.1 Dashboard recent 列表对象复用 — 对比数量，复用已有 widget 只更新文本
- [x] 3.2 CircularProgress paintEvent 缓存 — font/fontmetrics/pen 缓存为属性, resizeEvent 失效
- [x] 3.3 Database WAL 模式和 timeout — sqlite3.connect(timeout=5.0) + PRAGMA journal_mode=WAL
- [x] 3.4 ScreenShake 预渲染 QPixmap — _get_drop_pixmap() 缓存，paintEvent 只做 drawPixmap

## 四、UI 交互优化
- [x] 4.1 ReminderEngine 休眠校正 — _compute_remaining_ms() 基于 next_due 绝对时间, _on_timeout 校验
- [x] 4.2 高 DPI resize margin — 属性 _resize_margin 基于 devicePixelRatio 动态计算
- [x] 4.3 HistoryPage Y 轴圆整 — _nice_ceil() 向上取整到 500/1000 的倍数

## 验证
- [x] SMOKE TEST PASSED (QT_QPA_PLATFORM=offscreen)

## 五、Code Review 修复 (2026-02-28)
- [x] 5.1 config.py: os.write → os.fdopen + flush + fsync 防止部分写入
- [x] 5.2 dashboard.py: _update_recent_item 补充 stylesheet 更新，主题切换后复用 widget 颜色同步
- [x] 5.3 autostart.py: .desktop Exec 用 shlex.join() 正确处理路径空格
- [x] 5.4 main.py: autostart 启用/禁用失败时不写 config，避免 UI 与系统状态不一致
- [x] 5.5 main_window.py: 移除 DPR 乘数（Qt event pos 已是逻辑坐标）+ 删除未用 QScreen import
- [x] 5.6 history.py: _nice_ceil 用 math.ceil 避免浮点取整误差
- [x] 5.7 theme.py: qcolor 用的 shake token 改为 #AARRGGBB hex 避免 Qt 6.6+ rgba alpha 解析歧义
- [x] 5.8 tray.py: deleteLater 后 self._menu = None + 加 None 检查
- [x] 5.9 screen_shake.py: QFont 缓存到 __init__ + pixmap 设 devicePixelRatio 高 DPI 清晰渲染
- [x] SMOKE TEST PASSED
