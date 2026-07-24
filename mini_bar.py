from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import QPoint, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPixmap, QColor, QPen, QCursor

SCREEN_EDGE_MARGIN = 4
VISIBLE_EDGE = 20


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
        self.setFixedSize(80, 40)
        self._init_ui()
        self._init_position()
        self._drag_offset = None
        self._dragging = False
        self._hover_timer = QTimer(self)
        self._hover_timer.timeout.connect(self._check_hover)
        self._hover_timer.start(100)

    def _init_ui(self):
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(6, 4, 2, 4)
        hbox.setSpacing(4)

        icon_label = QLabel()
        icon_label.setPixmap(self._create_icon(24))
        icon_label.setObjectName("miniIcon")
        hbox.addWidget(icon_label)

        self.count_label = QLabel("0/0")
        self.count_label.setObjectName("miniCount")
        self.count_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        hbox.addWidget(self.count_label)

    def _create_icon(self, size=32):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # blue circle
        painter.setBrush(QColor("#4A90D9"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        # white F
        painter.setPen(QPen(QColor("#FFFFFF")))
        font = QFont("Segoe UI", size * 5 // 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "F")
        painter.end()
        return pixmap

    def _init_position(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        self._screen_geom = screen.availableGeometry()
        self._edge = "right"  # "right", "left", "top"
        x = self._screen_geom.right() - self.width() - SCREEN_EDGE_MARGIN
        y = SCREEN_EDGE_MARGIN
        self.move(x, y)
        self._retract()

    # ── Hover slide (timer polling to avoid animation flicker) ──

    def _check_hover(self):
        pos = QCursor.pos()
        rect = self.frameGeometry()
        in_rect = rect.contains(pos)
        if in_rect and not self._hovered:
            self._hovered = True
            self._slide_in()
        elif not in_rect and self._hovered:
            self._hovered = False
            QTimer.singleShot(1000, self._try_retract)

    def _try_retract(self):
        if not self._hovered:
            self._retract()

    def _retract(self):
        if self._edge == "right":
            self._animate_move(self._screen_geom.right() - VISIBLE_EDGE, self.y())
        elif self._edge == "left":
            self._animate_move(self._screen_geom.left() - self.width() + VISIBLE_EDGE, self.y())
        elif self._edge == "top":
            self._animate_move(self.x(), self._screen_geom.top() - self.height() + VISIBLE_EDGE)

    def _slide_in(self):
        if self._edge == "right":
            self._animate_move(self._screen_geom.right() - self.width() - SCREEN_EDGE_MARGIN, self.y())
        elif self._edge == "left":
            self._animate_move(self._screen_geom.left() + SCREEN_EDGE_MARGIN, self.y())
        elif self._edge == "top":
            self._animate_move(self.x(), self._screen_geom.top() + SCREEN_EDGE_MARGIN)

    def _snap_to_edge(self):
        cx = self.x() + self.width() / 2
        cy = self.y() + self.height() / 2
        sw = self._screen_geom.width()
        sh = self._screen_geom.height()
        if cy < sh / 3:
            self._edge = "top"
            x = max(self._screen_geom.left(), min(self.x(), self._screen_geom.right() - self.width()))
            self.move(x, self._screen_geom.top() + SCREEN_EDGE_MARGIN)
        elif cx < sw / 3:
            self._edge = "left"
            self.move(self._screen_geom.left() + SCREEN_EDGE_MARGIN, self.y())
        else:
            self._edge = "right"
            self.move(self._screen_geom.right() - self.width() - SCREEN_EDGE_MARGIN, self.y())

    def _animate_move(self, target_x, target_y, duration=200):
        self._anim = QPropertyAnimation(self, b"pos")
        self._anim.setDuration(duration)
        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(QPoint(target_x, target_y))
        self._anim.start()

    # ── Mouse drag & click ────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            self._dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_offset
            if (new_pos - self.pos()).manhattanLength() > 5:
                self._dragging = True
                self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._dragging:
                self._snap_to_edge()
                self._retract()
            else:
                self.switch_to_main.emit()
        self._drag_offset = None
        self._dragging = False
        super().mouseReleaseEvent(event)

    # ── Update ────────────────────────────────────

    def update_count(self, total, done):
        self.count_label.setText(f"{done}/{total}")
