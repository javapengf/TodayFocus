from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import QPoint, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

SCREEN_EDGE_MARGIN = 2
VISIBLE_EDGE = 15


class MiniBar(QWidget):
    switch_to_main = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._hovered = False
        self._screen_geom = None
        self._drag_offset = None
        self.setObjectName("miniBar")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(160, 36)
        self._init_ui()
        self._init_position()

    def _init_ui(self):
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(8, 2, 8, 2)

        icon_label = QLabel("F")
        icon_label.setObjectName("miniIcon")
        icon_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hbox.addWidget(icon_label)

        self.count_label = QLabel("0 tasks")
        self.count_label.setObjectName("miniCount")
        hbox.addWidget(self.count_label)

        hbox.addStretch()

        expand_btn = QPushButton("^")
        expand_btn.setObjectName("miniExpandBtn")
        expand_btn.setFixedSize(24, 24)
        expand_btn.setToolTip("Expand")
        expand_btn.clicked.connect(self.switch_to_main.emit)
        hbox.addWidget(expand_btn)

    def _init_position(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        self._screen_geom = screen.availableGeometry()
        x = self._screen_geom.right() - self.width() - SCREEN_EDGE_MARGIN
        y = SCREEN_EDGE_MARGIN
        self.move(x, y)
        self._retract()

    # ── Hover slide ───────────────────────────────

    def enterEvent(self, event):
        self._hovered = True
        self._slide_in()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        QTimer.singleShot(800, self._try_retract)
        super().leaveEvent(event)

    def _try_retract(self):
        if not self._hovered:
            self._retract()

    def _retract(self):
        target_x = self._screen_geom.right() - VISIBLE_EDGE
        self._animate_move(target_x, self.y())

    def _slide_in(self):
        target_x = self._screen_geom.right() - self.width() - SCREEN_EDGE_MARGIN
        self._animate_move(target_x, self.y())

    def _animate_move(self, target_x, target_y, duration=200):
        self._anim = QPropertyAnimation(self, b"pos")
        self._anim.setDuration(duration)
        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(QPoint(target_x, target_y))
        self._anim.start()

    # ── Click / Drag ──────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_offset is not None:
            moved = event.globalPosition().toPoint() - self.frameGeometry().topLeft() - self._drag_offset
            if abs(moved.x()) < 5 and abs(moved.y()) < 5:
                self.switch_to_main.emit()
            self._drag_offset = None
        super().mouseReleaseEvent(event)

    # ── Update ────────────────────────────────────

    def update_count(self, total, done):
        self.count_label.setText(f"{done}/{total}")
