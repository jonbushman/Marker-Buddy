# Marker Buddy

A lightweight, cross-platform (Windows/Mac) desktop tool for drawing directly
on top of your screen so OBS can capture the annotations as a separate
source — think "telestrator" for streaming.

It's two windows:

- **Draw Surface** — a transparent, borderless, always-on-top window that
  covers one monitor. This is what you add to OBS.
- **Controls** — a small toolbar with color, brush size, eraser, undo,
  clear, and a Draw Mode toggle. It's a separate window so it never shows up
  in the OBS capture of the draw surface.

## Setup

Requires Python 3.10+.

```
pip install -r requirements.txt
python main.py
```

(On Windows PowerShell, run these as two separate commands — `&&` isn't a
valid statement separator there. `;` works if you want them on one line.)

## Using it with OBS

1. In OBS, add a **Window Capture** source and select the window titled
   **"Marker Buddy - Draw Surface"** (not the Controls window).
2. On Windows, in the source's properties set **Capture Method** to
   **"BitBlt"**. The other option, "Windows 10 (1903 and up)" (the Windows
   Graphics Capture API), does not support per-window transparency and will
   show a solid black background instead of your desktop showing through.
   On Mac, Window Capture preserves transparency by default.
3. Draw with the toolbar's **Draw Mode** button switched **ON**. Toggle it
   **OFF** to make the draw surface click-through, so you can interact with
   whatever's underneath (your game, browser, slides, etc.) without closing
   the app.

If you have more than one monitor, use the **Overlay screen** dropdown in
the toolbar to pick which monitor the draw surface covers — it should match
whichever monitor OBS is capturing.

Note: the draw surface intentionally shows up in your taskbar / Alt-Tab
(rather than being a hidden "tool" window) — that's what makes it visible
to OBS's Window Capture source list in the first place.

## Controls

- **Color swatches / Custom...** — pick a marker color.
- **Brush size** — stroke width.
- **Eraser** — toggle to erase instead of draw.
- **Undo** — remove the last stroke.
- **Clear all** — wipe the canvas.
- **Draw Mode** — ON = drawing captures your mouse; OFF = clicks pass
  through to the desktop below.
- **Quit** — closes both windows.

## Known limitations

- Won't draw over games running in exclusive fullscreen — use borderless
  windowed / fullscreen-windowed mode instead, which is also what OBS
  Window Capture generally requires.
- The draw surface covers one monitor at a time (pick it from the toolbar).
- Long drawing sessions with hundreds of strokes will slow down repainting;
  use **Clear all** between segments to keep it snappy.

## Packaging a standalone build

```
pip install pyinstaller
pyinstaller --noconfirm --windowed --onefile --name MarkerBuddy main.py
```

This produces a single executable in `dist/` on Windows (`MarkerBuddy.exe`)
and a `.app` bundle on macOS (`MarkerBuddy.app`). Run the same command on
each OS you want to build for — PyInstaller doesn't cross-compile.
