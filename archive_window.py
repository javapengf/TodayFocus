from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard, QCursor


ARCHIVE_TITLE_HEIGHT = 40


class ArchiveWindow(QFrame):
    def __init__(self, data_manager):
        super().__init__()
        self.dm = data_manager
        self._drag_pos = None
        self.setObjectName("archiveFrame")
        self.setFixedSize(380, 480)
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

        scroll = QScrollArea()
        scroll.setObjectName("archiveScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.content = QWidget()
        self.content.setObjectName("archiveContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(4, 8, 4, 8)
        self.content_layout.setSpacing(2)
        self.content_layout.addStretch()

        scroll.setWidget(self.content)
        layout.addWidget(scroll)

    def _create_title_bar(self):
        bar = QFrame()
        bar.setObjectName("archiveTitleBar")
        bar.setFixedHeight(ARCHIVE_TITLE_HEIGHT)
        hbox = QHBoxLayout(bar)
        hbox.setContentsMargins(12, 0, 8, 0)

        title = QLabel("History")
        title.setObjectName("archiveTitleLabel")
        hbox.addWidget(title)

        hbox.addStretch()

        copy_btn = QPushButton("⧉")
        copy_btn.setObjectName("archiveCopyBtn")
        copy_btn.setFixedSize(28, 28)
        copy_btn.setToolTip("Copy all")
        copy_btn.clicked.connect(self._copy_all)
        hbox.addWidget(copy_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("archiveCloseBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Close")
        close_btn.clicked.connect(self.hide)
        hbox.addWidget(close_btn)

        return bar

    # ── Drag ──────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < ARCHIVE_TITLE_HEIGHT:
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    # ── Copy all ──────────────────────────────────

    def _copy_all(self):
        archive = self.dm.get_archive()
        if not archive:
            return
        lines = []
        for entry in reversed(archive):
            lines.append(f"## {entry['date']}")
            for item in entry.get("items", []):
                lines.append(f"- {item['text']}")
            lines.append("")
        text = "\n".join(lines).rstrip()
        QApplication.clipboard().setText(text)

    # ── Rendering ─────────────────────────────────

    def show(self):
        self._load_archive()
        super().show()
        self.activateWindow()
        self.raise_()

    def _load_archive(self):
        # clear old widgets
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        archive = self.dm.get_archive()
        if not archive:
            label = QLabel("No history yet.")
            label.setObjectName("archiveEmpty")
            self.content_layout.insertWidget(0, label)
            return

        for entry in reversed(archive):
            date_label = QLabel(entry["date"])
            date_label.setObjectName("archiveDateLabel")
            self.content_layout.insertWidget(
                self.content_layout.count() - 1, date_label
            )

            for item_data in entry.get("items", []):
                item_widget = ArchiveItemWidget(item_data)
                self.content_layout.insertWidget(
                    self.content_layout.count() - 1, item_widget
                )

            # spacer between days
            spacer = QFrame()
            spacer.setFixedHeight(8)
            self.content_layout.insertWidget(
                self.content_layout.count() - 1, spacer
            )


class ArchiveItemWidget(QFrame):
    def __init__(self, item_data):
        super().__init__()
        self.setObjectName("archiveItem")
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(12, 4, 12, 4)

        check = QLabel("✓" if item_data.get("completed") else "·")
        check.setObjectName("archiveCheck")
        if item_data.get("completed"):
            check.setProperty("done", True)
        check.setFixedWidth(20)
        hbox.addWidget(check)

        text_label = QLabel(item_data.get("text", ""))
        text_label.setObjectName("archiveText")
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if item_data.get("completed"):
            text_label.setProperty("done", True)
        hbox.addWidget(text_label)

        if item_data.get("priority") == "high":
            dot = QLabel("!")
            dot.setObjectName("archivePriorityDot")
            hbox.addWidget(dot)

        self._text = item_data.get("text", "")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self._copy_text)
        menu.exec(QCursor.pos())

    def _copy_text(self):
        QApplication.clipboard().setText(self._text)
