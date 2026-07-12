from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QVBoxLayout,
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal


TITLE_BAR_HEIGHT = 40


class MainWindow(QFrame):
    switch_to_mini = pyqtSignal()

    def __init__(self, data_manager):
        super().__init__()
        self.dm = data_manager
        self._drag_pos = None
        self.setObjectName("mainFrame")
        self.setFixedSize(380, 520)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._create_title_bar())
        layout.addWidget(self._create_input_bar())

        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        layout.addWidget(self.task_list)

        layout.addWidget(self._create_footer())
        self._load_tasks()

    def _create_title_bar(self):
        bar = QFrame()
        bar.setObjectName("titleBar")
        bar.setFixedHeight(TITLE_BAR_HEIGHT)
        hbox = QHBoxLayout(bar)
        hbox.setContentsMargins(12, 0, 8, 0)

        title = QLabel("TodayFocus")
        title.setObjectName("titleLabel")
        hbox.addWidget(title)

        hbox.addStretch()

        mini_btn = QPushButton("—")
        mini_btn.setObjectName("miniBtn")
        mini_btn.setFixedSize(28, 28)
        mini_btn.setToolTip("Hide to mini bar")
        mini_btn.clicked.connect(self.switch_to_mini.emit)
        hbox.addWidget(mini_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Hide to mini bar")
        close_btn.clicked.connect(self.switch_to_mini.emit)
        hbox.addWidget(close_btn)

        return bar

    def _create_input_bar(self):
        bar = QFrame()
        bar.setObjectName("inputBar")
        hbox = QHBoxLayout(bar)
        hbox.setContentsMargins(12, 8, 12, 8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Add a task...")
        self.input_field.setObjectName("inputField")
        self.input_field.returnPressed.connect(self._on_add_task)
        hbox.addWidget(self.input_field)

        high_btn = QPushButton("!")
        high_btn.setObjectName("highBtn")
        high_btn.setFixedSize(32, 32)
        high_btn.setToolTip("High priority")
        high_btn.clicked.connect(lambda: self._on_add_task(priority="high"))
        hbox.addWidget(high_btn)

        return bar

    def _create_footer(self):
        bar = QFrame()
        bar.setObjectName("footerBar")
        hbox = QHBoxLayout(bar)
        hbox.setContentsMargins(12, 4, 12, 4)
        self.stats_label = QLabel("0 / 0 done")
        self.stats_label.setObjectName("statsLabel")
        hbox.addWidget(self.stats_label)
        return bar

    # ── Drag ──────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < TITLE_BAR_HEIGHT:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            else:
                self._drag_pos = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    # ── Keyboard ──────────────────────────────────

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.switch_to_mini.emit()
        else:
            super().keyPressEvent(event)

    # ── Task rendering ────────────────────────────

    def _load_tasks(self):
        self.task_list.clear()
        for item in self.dm.get_items():
            self._add_task_widget(item)
        self._update_stats()

    def _add_task_widget(self, item):
        widget = TaskItemWidget(item)
        widget.toggled.connect(self._on_toggle)
        widget.deleted.connect(self._on_delete)

        list_item = QListWidgetItem()
        list_item.setSizeHint(widget.sizeHint())
        self.task_list.addItem(list_item)
        self.task_list.setItemWidget(list_item, widget)

    def _on_toggle(self, item_id):
        self.dm.toggle_complete(item_id)
        self._load_tasks()

    def _on_delete(self, item_id):
        self.dm.delete_item(item_id)
        self._load_tasks()

    def _on_add_task(self, priority="normal"):
        text = self.input_field.text().strip()
        if not text:
            return
        self.dm.add_item(text, priority)
        self.input_field.clear()
        self._load_tasks()

    def _update_stats(self):
        total, done = self.dm.get_stats()
        self.stats_label.setText(f"{done} / {total} done")


class TaskItemWidget(QFrame):
    toggled = pyqtSignal(str)
    deleted = pyqtSignal(str)

    def __init__(self, item_data):
        super().__init__()
        self.item_id = item_data["id"]
        self.setObjectName("taskItem")
        if item_data["priority"] == "high":
            self.setProperty("priority", "high")

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(8, 4, 8, 4)

        cb = QPushButton()
        cb.setObjectName("taskCheck")
        cb.setFixedSize(22, 22)
        cb.setCheckable(True)
        cb.setChecked(item_data["completed"])
        cb.clicked.connect(lambda: self.toggled.emit(self.item_id))
        hbox.addWidget(cb)

        text_label = QLabel(item_data["text"])
        text_label.setObjectName("taskText")
        if item_data["completed"]:
            text_label.setProperty("done", True)
        hbox.addWidget(text_label)

        if item_data["priority"] == "high":
            dot = QLabel("!")
            dot.setObjectName("priorityDot")
            hbox.addWidget(dot)

        del_btn = QPushButton("✕")
        del_btn.setObjectName("delBtn")
        del_btn.setFixedSize(22, 22)
        del_btn.clicked.connect(lambda: self.deleted.emit(self.item_id))
        hbox.addWidget(del_btn)
