"""
main.py — Auto-init display on boot for JC3248W535EN.

After flashing, every power-cycle or replug will:
  1. Init the board (LCD + touch)
  2. Turn on backlight at 80%
  3. Show a splash screen

The `d` object is then available in the REPL.
"""

from display import Display
import time

d = Display(brightness=80)

# Splash
d.fb.fill(d.BLACK)
d.fb.rect(0, 0, d.width, d.height, d.color(20, 20, 60), True)
d.fb.rect(10, 10, d.width-20, d.height-20, d.color(0, 80, 160), False)
cx = (d.width - 13*8) // 2
d.text('JC3248W535EN', cx, d.height//2 - 20, d.WHITE)
d.text('MicroPython', (d.width - 11*8)//2, d.height//2, d.color(180, 220, 255))
d.text('Ready.', (d.width - 6*8)//2, d.height//2 + 20, d.YELLOW)
d.show()

print('Display ready. Use `d` in the REPL.')
print('  d.fill(d.RED)')
print('  d.touch()')
