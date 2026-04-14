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

    @staticmethod
    def color(r, g, b):
        """Pack 8-bit R,G,B into RGB565 in the byte order draw_bitmap expects."""
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def flush(self, board):
        """Push the entire framebuffer to the display."""
        board.draw_bitmap(0, 0, self.width, self.height, self._buf)

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
        board.draw_bitmap(x, y, w, h, region)
