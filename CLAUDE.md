# TodayFocus 项目规范

## 项目概述

TodayFocus 是一个"今日要事"桌面浮窗应用，采用 Python + PyQt6 + pynput，零编译直接运行。

## 技术栈

- **Python 3.12+**
- **PyQt6** — GUI 框架
- **pynput** — 全局快捷键监听

## 项目结构

```
TodayFocus/
├── CLAUDE.md          # 本文件，项目规范
├── main.py            # 入口：QApplication、全局快捷键、状态切换
├── main_window.py     # 主浮窗：无边框、可拖动、任务列表
├── mini_bar.py        # 迷你悬浮条：贴边隐藏、hover 滑入
├── data_manager.py    # 数据层：JSON 持久化、CRUD、每日重置
├── tray_manager.py    # 系统托盘：右键菜单、双击恢复
├── style.qss          # Qt 样式表
├── config.json        # 应用配置
├── requirements.txt   # 依赖列表
└── run.bat            # Windows 一键启动
```

## 编码规范

- **命名**：模块 snake_case，类 PascalCase，私有方法 `_leading_underscore`
- **文件**：每个文件不超过 200 行，单一职责
- **注释**：只写 WHY，不写 WHAT。代码自解释
- **格式**：4 空格缩进，UTF-8 编码
- **导入**：标准库 → 第三方 → 本地模块，分组排列

## 架构原则

- DataManager 纯逻辑层，不依赖任何 Qt 组件
- 窗口组件通过 pyqtSignal 通信，不直接调用其他窗口方法
- pynput 线程通过 QTimer.singleShot(0, callback) 调度到 Qt 主线程
- JSON 写入使用原子模式（先写 .tmp 再 rename）

## 开发纪律

- 每写完一个模块立即验证，不累积未测试代码
- 修改前先读现有代码，不假设
- 改动后跑验证命令

## 验证命令

```bash
# 运行应用
python main.py

# 测试数据层
python -c "from data_manager import DataManager; dm = DataManager(); print(dm.get_stats())"
```
