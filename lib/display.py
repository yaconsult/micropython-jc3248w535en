"""
display.py — High-level display interface for JC3248W535EN

Combines Board (LCD + touch), Backlight, and RGB565Buffer into a single
convenient object.

Usage:
    from display import Display
    d = Display()           # init board, backlight on at 80%
    d.fill(d.RED)           # fill framebuffer red and flush
    d.text('Hello!', 10, 10, d.WHITE)
    d.show()                # flush framebuffer to screen
    d.backlight.set(50)     # dim to 50%
    pts = d.touch()         # [(x, y, strength)] or []
"""

from esp_panel import Board
from backlight import Backlight
from framebuf_rgb565 import RGB565Buffer


class Display:
    # Colour shortcuts delegated from RGB565Buffer
    BLACK   = RGB565Buffer.BLACK
    WHITE   = RGB565Buffer.WHITE
    RED     = RGB565Buffer.RED
    GREEN   = RGB565Buffer.GREEN
    BLUE    = RGB565Buffer.BLUE
    YELLOW  = RGB565Buffer.YELLOW
    CYAN    = RGB565Buffer.CYAN
    MAGENTA = RGB565Buffer.MAGENTA

    def __init__(self, brightness=80):
        self._board = Board()
        self._board.init()
        self._board.begin()

        # Panel is 320x480 in firmware. Physical orientation is landscape (480 wide x 320 tall).
        # TODO: fix MADCTL in firmware for portrait mode (needs reflash).
        self.width  = self._board.get_width()    # 320
        self.height = self._board.get_height()   # 480

        self.backlight = Backlight()
        self.backlight.set(brightness)

        self.fb = RGB565Buffer(self.width, self.height)

    # ── Drawing (delegate to framebuffer) ────────────────────────────────────

    def fill(self, color):
        self.fb.fill(color)
        self.show()

    def pixel(self, x, y, color):
        self.fb.pixel(x, y, color)

    def line(self, x1, y1, x2, y2, color):
        self.fb.line(x1, y1, x2, y2, color)

    def rect(self, x, y, w, h, color, fill=False):
        self.fb.rect(x, y, w, h, color, fill)

    def text(self, s, x, y, color=WHITE):
        self.fb.text(s, x, y, color)

    def color(self, r, g, b):
        return RGB565Buffer.color(r, g, b)

    # ── Display update ────────────────────────────────────────────────────────

    def show(self):
        """Flush framebuffer to display."""
        self.fb.flush(self._board)

    def show_region(self, x, y, w, h):
        """Flush only a rectangular region."""
        self.fb.flush_region(self._board, x, y, w, h)

    # ── Touch ─────────────────────────────────────────────────────────────────

    def touch(self):
        """Return list of (x, y, strength) touch points, or [].
        Raw touch X,Y map directly to display X,Y on this board."""
        raw = self._board.read_touch()
        result = []
        for pt in raw:
            x = min(max(pt[0], 0), self.width - 1)
            y = min(max(pt[1], 0), self.height - 1)
            result.append((x, y, pt[2]))
        return result

    # ── Raw board access ──────────────────────────────────────────────────────

    @property
    def board(self):
        return self._board
