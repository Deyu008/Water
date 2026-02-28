# Water Reminder 💧

高端饮水提醒桌面程序 — PySide6 + Material Design

## 快速开始

```bash
# 创建 conda 环境
conda env create -f environment.yml
conda activate water

# 运行
python main.py
```

## 功能
- 定时提醒喝水（可自定义间隔）
- 每日饮水量追踪 + 圆环进度
- 饮水历史统计图表
- 系统托盘后台运行
- 深色/浅色主题切换
- 提醒音效
- 开机自启动（Windows）

## 开发
```bash
conda activate water
# 在 Linux 上无显示器时用 offscreen 模式测试
QT_QPA_PLATFORM=offscreen python main.py
# 运行测试
pytest tests/
```

## Windows 打包
```bash
pyinstaller main.spec
```
