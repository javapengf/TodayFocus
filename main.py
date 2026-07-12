import sys
import json
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from pynput import keyboard as pynput_kb

from data_manager import DataManager
from main_window import MainWindow
from mini_bar import MiniBar
from tray_manager import TrayManager

CONFIG_FILE = Path(__file__).parent / "config.json"


class FocusApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("TodayFocus")
        self.app.setQuitOnLastWindowClosed(False)

        qss_file = Path(__file__).parent / "style.qss"
        if qss_file.exists():
            self.app.setStyleSheet(qss_file.read_text(encoding="utf-8"))

        self.config = self._load_config()
        self.dm = DataManager()

        self.main_win = MainWindow(self.dm)
        self.mini_bar = MiniBar(self.config)
        self.tray = TrayManager(self.app)

        self.main_win.switch_to_mini.connect(self._show_mini_hide_main)
        self.mini_bar.switch_to_main.connect(self._show_main_hide_mini)
        self.tray.restore_requested.connect(self._show_main_hide_mini)

        self._setup_hotkey()

        self.mini_bar.show()
        self.main_win.hide()

        self._date_check_timer = QTimer()
        self._date_check_timer.timeout.connect(self._midnight_check)
        self._date_check_timer.start(60000)

    def _load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "shortcut": "Ctrl+Alt+F",
            "window_position": {"x": 800, "y": 300},
            "mini_bar_position": "top_right",
        }

    # ── Global hotkey ─────────────────────────────

    def _setup_hotkey(self):
        hotkey_str = self.config.get("shortcut", "Ctrl+Alt+F")
        combo = hotkey_str.lower().replace("ctrl", "<ctrl>").replace("alt", "<alt>")

        def on_activate():
            QTimer.singleShot(0, self._toggle_visibility)

        self._hotkey_listener = pynput_kb.HotKey(
            pynput_kb.HotKey.parse(combo), on_activate
        )
        self._listener = pynput_kb.Listener(
            on_press=self._for_canonical(self._hotkey_listener.press),
            on_release=self._for_canonical(self._hotkey_listener.release),
        )
        self._listener.start()

    def _for_canonical(self, func):
        def wrapper(key):
            return func(self._listener.canonical(key))
        return wrapper

    # ── Visibility toggle ─────────────────────────

    def _toggle_visibility(self):
        if self.main_win.isVisible():
            self._show_mini_hide_main()
        else:
            self._show_main_hide_mini()

    def _show_mini_hide_main(self):
        self.main_win.hide()
        self.mini_bar.show()
        total, done = self.dm.get_stats()
        self.mini_bar.update_count(total, done)

    def _show_main_hide_mini(self):
        self.mini_bar.hide()
        self.main_win._load_tasks()
        self.main_win.show()
        self.main_win.activateWindow()
        self.main_win.raise_()

    # ── Midnight reset ────────────────────────────

    def _midnight_check(self):
        self.dm._check_daily_reset()
        if self.main_win.isVisible():
            self.main_win._load_tasks()
        total, done = self.dm.get_stats()
        self.mini_bar.update_count(total, done)

    # ── Run ────────────────────────────────────────

    def run(self):
        wp = self.config.get("window_position", {})
        if wp.get("x") is not None:
            self.main_win.move(wp["x"], wp["y"])

        rc = self.app.exec()

        self.config["window_position"] = {
            "x": self.main_win.x(),
            "y": self.main_win.y(),
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

        self._listener.stop()
        sys.exit(rc)


if __name__ == "__main__":
    FocusApp().run()
