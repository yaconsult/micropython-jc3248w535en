"""
touch_draw.py — Draw dots where you tap; tap the CLEAR button to reset.

    mpremote run examples/touch_draw.py
"""

import time
from display import Display

d = Display(brightness=80)

BTN_X, BTN_Y, BTN_W, BTN_H = d.width - 100, d.height - 40, 90, 30
DOT_R = 6
DOT_COLOR  = d.YELLOW
TEXT_COLOR = d.WHITE
BTN_COLOR  = d.color(60, 60, 200)


def draw_ui():
    d.fb.fill(d.BLACK)
    d.fb.rect(BTN_X, BTN_Y, BTN_W, BTN_H, BTN_COLOR, True)
    d.fb.text('CLEAR', BTN_X + 16, BTN_Y + 11, TEXT_COLOR)
    d.fb.text('Touch anywhere', 10, 10, d.color(180, 180, 180))
    d.show()


def draw_dot(x, y):
    for dy in range(-DOT_R, DOT_R + 1):
        for dx in range(-DOT_R, DOT_R + 1):
            if dx * dx + dy * dy <= DOT_R * DOT_R:
                d.fb.pixel(x + dx, y + dy, DOT_COLOR)
    # Show coords at top of screen
    d.fb.rect(0, 20, 160, 10, d.BLACK, True)
    d.fb.text('{},{}'.format(x, y), 0, 20, d.color(200, 200, 0))
    d.show()


def in_button(x, y):
    return BTN_X <= x <= BTN_X + BTN_W and BTN_Y <= y <= BTN_Y + BTN_H


draw_ui()
last_pts = []

while True:
    pts = d.touch()
    if pts and pts != last_pts:
        x, y, _ = pts[0]
        if in_button(x, y):
            draw_ui()
        else:
            draw_dot(x, y)
    last_pts = pts
    time.sleep_ms(30)
