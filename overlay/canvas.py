from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor
from PySide6.QtWidgets import QWidget


class OverlayCanvas(QWidget):
    """Transparent, always-on-top drawing surface.

    Add this window as a Window Capture source in OBS. Toggle click-through
    mode from the toolbar to let clicks reach whatever is underneath when
    you're not actively drawing.
    """

    strokeCountChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Buddy - Draw Surface")
        # Deliberately NOT Qt.Tool: tool windows get WS_EX_TOOLWINDOW on
        # Windows, which OBS's Window Capture enumeration skips, so the
        # surface would never show up in the source picker.
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.NoDropShadowWindowHint
            # Never let the draw surface become the active/key window: it
            # only needs mouse events, not keyboard focus. Without this, on
            # macOS re-showing this window (see set_click_through) steals
            # activation from the Controls window, which then swallows the
            # next click on the toolbar as a "wake up the window" click
            # instead of an actual button press.
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        self.pen_color = QColor("#ff3b30")
        self.pen_width = 6
        self.erasing = False

        self.strokes: list[tuple[QPainterPath, QColor, int, bool]] = []
        self._current_path: QPainterPath | None = None
        self._click_through = False

    # -- configuration ---------------------------------------------------
    def set_screen_geometry(self, geometry: QRect):
        self.setGeometry(geometry)

    def set_pen_color(self, color: QColor):
        self.pen_color = color
        self.erasing = False

    def set_pen_width(self, width: int):
        self.pen_width = width

    def set_erasing(self, erasing: bool):
        self.erasing = erasing

    def undo(self):
        if self.strokes:
            self.strokes.pop()
            self.strokeCountChanged.emit(len(self.strokes))
            self.update()

    def clear(self):
        self.strokes.clear()
        self.strokeCountChanged.emit(0)
        self.update()

    def set_click_through(self, enabled: bool):
        self._click_through = enabled
        self.setWindowFlag(Qt.WindowTransparentForInput, enabled)
        self.show()

    def is_click_through(self) -> bool:
        return self._click_through

    # -- mouse handling ----------------------------------------------------
    def mousePressEvent(self, event):
        if self._click_through or event.button() != Qt.LeftButton:
            return
        self._current_path = QPainterPath(event.position())
        self.update()

    def mouseMoveEvent(self, event):
        if self._click_through or self._current_path is None:
            return
        self._current_path.lineTo(event.position())
        self.update()

    def mouseReleaseEvent(self, event):
        if self._click_through or self._current_path is None:
            return
        self.strokes.append(
            (self._current_path, QColor(self.pen_color), self.pen_width, self.erasing)
        )
        self._current_path = None
        self.strokeCountChanged.emit(len(self.strokes))
        self.update()

    # -- painting ------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Reset to fully transparent each frame, then replay every stroke in
        # order so erase strokes correctly punch holes in earlier drawing.
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)

        def draw_path(path, color, width, erase):
            painter.setCompositionMode(
                QPainter.CompositionMode_Clear if erase else QPainter.CompositionMode_SourceOver
            )
            pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

        for path, color, width, erase in self.strokes:
            draw_path(path, color, width, erase)

        if self._current_path is not None:
            draw_path(self._current_path, self.pen_color, self.pen_width, self.erasing)

        # Windows only routes mouse clicks to pixels with non-zero alpha on a
        # layered (translucent) window - a fully transparent pixel is
        # click-through no matter what our own click-through state is. Back
        # fill any still-transparent pixels with an imperceptible alpha=1 so
        # the whole window stays clickable, without changing how it looks.
        painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

        painter.end()
