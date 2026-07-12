# TodayFocus

今日要事桌面浮窗应用 — 聚焦每天最重要的任务。

## 特性

- 无边框浮窗，始终置顶
- 迷你悬浮条贴边隐藏，hover 滑入
- 全局快捷键 `Ctrl+Alt+F` 切换显示
- 任务优先级标记（重要/普通）
- 每日自动重置，昨日任务归档
- 系统托盘常驻
- Catppuccin Mocha 暗色主题

## 快速开始

### 依赖

```
pip install -r requirements.txt
```

### 运行

```
python main.py
```

或双击 `run.bat`（Windows）。

## 使用

| 操作 | 方式 |
|------|------|
| 添加任务 | 输入框 + 回车 |
| 标记重要 | 点击 `!` 按钮 |
| 完成/删除 | 复选框 / ✕ 按钮 |
| 隐藏窗口 | 关闭按钮 / ESC / `Ctrl+Alt+F` |
| 恢复窗口 | 点击悬浮条 / 双击托盘 / `Ctrl+Alt+F` |
| 退出应用 | 托盘右键 → Quit |

## 项目结构

```
├── main.py            # 入口
├── main_window.py     # 主浮窗
├── mini_bar.py        # 迷你悬浮条
├── data_manager.py    # 数据层
├── tray_manager.py    # 系统托盘
├── style.qss          # 样式表
├── config.json        # 配置
└── requirements.txt   # 依赖
```

## 技术栈

- Python 3.12+
- PyQt6 — GUI
- pynput — 全局快捷键

## License

MIT
