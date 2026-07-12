from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import QPoint, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

SCREEN_EDGE_MARGIN = 4
VISIBLE_EDGE = 50


class MiniBar(QWidget):
    switch_to_main = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._hovered = False
        self._screen_geom = None
        self.setObjectName("miniBar")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 44)
        self._init_ui()
        self._init_position()

    def _init_ui(self):
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(8, 2, 8, 2)

        icon_label = QLabel("F")
        icon_label.setObjectName("miniIcon")
        icon_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hbox.addWidget(icon_label)

        self.count_label = QLabel("0 / 0")
        self.count_label.setObjectName("miniCount")
        self.count_label.setFont(QFont("Segoe UI", 12))
        hbox.addWidget(self.count_label)

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

    # ── Click to expand ───────────────────────────

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.switch_to_main.emit()
        super().mouseReleaseEvent(event)

    # ── Update ────────────────────────────────────

    def update_count(self, total, done):
        self.count_label.setText(f"{done}/{total}")
