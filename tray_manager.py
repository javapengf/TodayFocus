from PyQt6.QtWidgets import QMenu, QSystemTrayIcon
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap


def _create_tray_icon():
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#4A90D9"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 24, 24)
    painter.setPen(QColor("#FFFFFF"))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "F")
    painter.end()
    return QIcon(pixmap)


class TrayManager(QObject):
    restore_requested = pyqtSignal()
    history_requested = pyqtSignal()

    def __init__(self, app, data_manager):
        super().__init__()
        self.app = app
        self.dm = data_manager

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(_create_tray_icon())
        self.tray.setToolTip("TodayFocus")

        menu = QMenu()
        show_action = menu.addAction("Show Focus")
        show_action.triggered.connect(self.restore_requested.emit)

        history_action = menu.addAction("History")
        history_action.triggered.connect(self.history_requested.emit)

        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._quit_app)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.restore_requested.emit()

    def _quit_app(self):
        self.tray.hide()
        self.app.quit()
