"""
framebuf_rgb565.py — RGB565 framebuffer for JC3248W535EN

Wraps MicroPython's built-in framebuf.FrameBuffer (RGB565 format) with
helpers to push regions or the full buffer to the display via draw_bitmap.

The underlying bytearray lives in PSRAM (automatically allocated there on
ESP32-S3 Octal-SPIRAM builds when the buffer is large enough).

Usage:
    from framebuf_rgb565 import RGB565Buffer
    fb = RGB565Buffer(320, 480)
    fb.fill(fb.color(255, 0, 0))        # red
    fb.text('Hello', 10, 10, fb.WHITE)
    fb.flush(board)                      # push full frame to display

    # Partial update
    fb.rect(50, 50, 100, 40, fb.color(0, 255, 0), True)
    fb.flush_region(board, 50, 50, 100, 40)
"""

import framebuf


class _Palette(framebuf.FrameBuffer):
    """2-pixel RGB565 palette used by writer.py for color glyph blitting."""
    def __init__(self):
        # Pre-initialize with black/white to ensure valid buffer state
        self._buf = bytearray([0x00, 0x00, 0xff, 0xff])  # black, white
        super().__init__(self._buf, 2, 1, framebuf.RGB565)

    def fg(self, color):
        self.pixel(1, 0, color)

    def bg(self, color):
        self.pixel(0, 0, color)


class RGB565Buffer(framebuf.FrameBuffer):
    # Common colour constants (RGB565 big-endian, pre-swapped for draw_bitmap)
    BLACK   = 0x0000
    WHITE   = 0xFFFF
    RED     = 0xF800
    GREEN   = 0x07E0
    BLUE    = 0x001F
    YELLOW  = 0xFFE0
    CYAN    = 0x07FF
    MAGENTA = 0xF81F

    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 2 bytes per pixel; on SPIRAM builds this lands in PSRAM
        self._buf = bytearray(width * height * 2)
        super().__init__(self._buf, width, height, framebuf.RGB565)
        # 2-pixel palette buffer required by writer.py for color blit
        self.palette = _Palette()

    @staticmethod
    def color(r, g, b):
        """Pack 8-bit R,G,B into RGB565 in the byte order draw_bitmap expects."""
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def flush(self, board):
        """Push the entire framebuffer to the display (no rotation)."""
        board.draw_bitmap(0, 0, self.width, self.height, self._buf)

    def flush_rotated(self, board, panel_w, panel_h):
        """Rotate framebuffer 90° CW and push to display.

        Framebuffer (self): width=panel_h (e.g.480), height=panel_w (e.g.320) — portrait view.
        Physical panel:     width=panel_w (e.g.320), height=panel_h (e.g.480) — landscape.

        90° CW rotation:  dst_row = src_col,  dst_col = (fb_height-1 - src_row)
        dst index = (src_x * panel_h + (fb_h - 1 - src_y)) * 2
        """
        fb_w = self.width    # portrait width  = panel_h (480)
        fb_h = self.height   # portrait height = panel_w (320)
        # 90° CW rotation: each src row becomes a dst column (right to left)
        # dst row dst_x (0..fb_w-1) = src column src_x (=dst_x), reversed vertically
        # dst[dst_x, :] = src[:, src_x] reversed  →  dst stride = panel_w = fb_h
        out = bytearray(fb_w * fb_h * 2)
        for src_x in range(fb_w):
            # Extract column src_x from src (fb_h pixels), reversed
            dst_row = src_x          # this column becomes dst row src_x
            dst_base = dst_row * panel_w * 2   # start of dst row in bytes
            for src_y in range(fb_h):
                src_i = (src_y * fb_w + src_x) * 2
                dst_i = dst_base + (fb_h - 1 - src_y) * 2
                out[dst_i]     = self._buf[src_i]
                out[dst_i + 1] = self._buf[src_i + 1]
        board.draw_bitmap(0, 0, panel_w, panel_h, out)

    def flush_region(self, board, x, y, w, h):
        """Push a rectangular region to the display (minimal data transfer)."""
        stride = self.width * 2
        row_bytes = w * 2
        # Build a contiguous sub-buffer for the region
        region = bytearray(row_bytes * h)
        for row in range(h):
            src_start = (y + row) * stride + x * 2
            dst_start = row * row_bytes
            region[dst_start:dst_start + row_bytes] = \
                self._buf[src_start:src_start + row_bytes]
        board.draw_bitmap(x, y, w, h, region)  # region coords in board-native space
