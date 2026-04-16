"""
multitouch_test.py — Test multi-touch (up to 5 points) on AXS15231B.

Usage:
    >>> exec(open('examples/multitouch_test.py').read())

Touch the screen with multiple fingers during the 10-second window.
"""

from display import Display
import time

d = Display(brightness=80)
d.fb.fill(d.BLACK)
d.show()

print('Touch screen with multiple fingers. Running for 10 seconds...')
start = time.ticks_ms()
max_points = 0

while time.ticks_diff(time.ticks_ms(), start) < 10000:
    pts = d.touch()
    if len(pts) > max_points:
        max_points = len(pts)
        print('New max:', len(pts), pts)
    time.sleep_ms(50)

print('Done. Max simultaneous touch points:', max_points)
