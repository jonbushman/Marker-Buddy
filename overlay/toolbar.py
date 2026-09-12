from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

PRESET_COLORS = ["#ff3b30", "#34c759", "#007aff", "#ffcc00", "#ffffff", "#000000"]


class Toolbar(QWidget):
    """Small always-on-top control panel. Kept as its own window so it never
    shows up in the OBS Window Capture source pointed at the draw surface."""

    colorChanged = Signal(QColor)
    widthChanged = Signal(int)
    eraserToggled = Signal(bool)
    undoRequested = Signal()
    clearRequested = Signal()
    clickThroughToggled = Signal(bool)
    screenChanged = Signal(int)
    quitRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Buddy - Controls")
        # Qt.Tool puts this window in a higher OS window layer than the
        # draw surface's plain WindowStaysOnTopHint (which it needs to keep
        # for OBS Window Capture visibility - see canvas.py). Without this,
        # both windows share one "always on top" layer and whichever was
        # clicked most recently wins the top spot; since the draw surface
        # is full-screen, clicking it to draw would win and permanently
        # bury Controls underneath with no way to click it again. A
        # distinct, higher layer means Controls is always reachable
        # regardless of click order. Tool windows are also hidden from
        # the taskbar/dock/Alt-Tab, which is fine here since Controls
        # isn't meant to be an OBS capture target anyway.
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setFixedWidth(230)

        layout = QVBoxLayout(self)

        screens = QGuiApplication.screens()
        if len(screens) > 1:
            layout.addWidget(QLabel("Overlay screen"))
            self.screen_combo = QComboBox()
            for i, s in enumerate(screens):
                geo = s.geometry()
                self.screen_combo.addItem(f"{i + 1}: {s.name()} ({geo.width()}x{geo.height()})")
            self.screen_combo.currentIndexChanged.connect(self.screenChanged.emit)
            layout.addWidget(self.screen_combo)

        layout.addWidget(QLabel("Color"))
        color_grid = QGridLayout()
        for i, hex_color in enumerate(PRESET_COLORS):
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(
                f"background-color:{hex_color}; border: 1px solid #888; border-radius: 4px;"
            )
            btn.clicked.connect(lambda _checked=False, c=hex_color: self.colorChanged.emit(QColor(c)))
            color_grid.addWidget(btn, i // 3, i % 3)
        custom_btn = QPushButton("Custom...")
        custom_btn.clicked.connect(self._pick_custom_color)
        color_grid.addWidget(custom_btn, len(PRESET_COLORS) // 3 + 1, 0, 1, 3)
        layout.addLayout(color_grid)

        layout.addWidget(QLabel("Brush size"))
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(1, 40)
        self.width_slider.setValue(6)
        self.width_slider.valueChanged.connect(self.widthChanged.emit)
        layout.addWidget(self.width_slider)

        self.eraser_btn = QPushButton("Eraser")
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.toggled.connect(self.eraserToggled.emit)
        layout.addWidget(self.eraser_btn)

        row = QHBoxLayout()
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undoRequested.emit)
        clear_btn = QPushButton("Clear all")
        clear_btn.clicked.connect(self.clearRequested.emit)
        row.addWidget(undo_btn)
        row.addWidget(clear_btn)
        layout.addLayout(row)

        layout.addWidget(self._divider())

        self.draw_mode_btn = QPushButton("Draw Mode: ON")
        self.draw_mode_btn.setCheckable(True)
        self.draw_mode_btn.toggled.connect(self._on_draw_mode_toggled)
        layout.addWidget(self.draw_mode_btn)

        self.status_label = QLabel("Strokes: 0")
        layout.addWidget(self.status_label)

        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self.quitRequested.emit)
        layout.addWidget(quit_btn)

        layout.addStretch()

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def _pick_custom_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.colorChanged.emit(color)

    def _on_draw_mode_toggled(self, checked: bool):
        click_through = checked  # checked means click-through is enabled
        self.draw_mode_btn.setText(
            "Draw Mode: OFF (click-through)" if click_through else "Draw Mode: ON"
        )
        self.clickThroughToggled.emit(click_through)

    def set_stroke_count(self, count: int):
        self.status_label.setText(f"Strokes: {count}")
