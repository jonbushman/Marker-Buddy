import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from overlay.canvas import OverlayCanvas
from overlay.toolbar import Toolbar


def main():
    app = QApplication(sys.argv)

    canvas = OverlayCanvas()
    toolbar = Toolbar()

    screens = QGuiApplication.screens()
    canvas.set_screen_geometry(screens[0].geometry())

    def on_color_changed(color):
        canvas.set_pen_color(color)
        toolbar.eraser_btn.setChecked(False)

    toolbar.colorChanged.connect(on_color_changed)
    toolbar.widthChanged.connect(canvas.set_pen_width)
    toolbar.eraserToggled.connect(canvas.set_erasing)
    toolbar.undoRequested.connect(canvas.undo)
    toolbar.clearRequested.connect(canvas.clear)
    def on_click_through_toggled(enabled):
        canvas.set_click_through(enabled)
        # set_click_through() re-shows the draw surface, which can raise it
        # above the Controls window; pull Controls back to the front so its
        # buttons stay clickable.
        toolbar.raise_()
        toolbar.activateWindow()

    toolbar.clickThroughToggled.connect(on_click_through_toggled)
    toolbar.quitRequested.connect(app.quit)
    canvas.strokeCountChanged.connect(toolbar.set_stroke_count)

    if hasattr(toolbar, "screen_combo"):
        def on_screen_change(index):
            canvas.set_screen_geometry(screens[index].geometry())

        toolbar.screenChanged.connect(on_screen_change)

    canvas.show()
    toolbar.show()
    toolbar.move(40, 40)

    # The draw surface is full-screen and shares the same "always on top"
    # layer as Controls. While Draw Mode is on, every click used to draw
    # can itself raise the draw surface above Controls (most noticeable on
    # macOS), permanently burying the toolbar underneath it with no way to
    # click it again short of quitting. Periodically pulling Controls back
    # to the front guards against that without interrupting an in-progress
    # stroke (the OS keeps routing mouse-move/release for that stroke to
    # the draw surface regardless of z-order changes elsewhere).
    keep_toolbar_on_top = QTimer()
    keep_toolbar_on_top.timeout.connect(toolbar.raise_)
    keep_toolbar_on_top.start(300)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
