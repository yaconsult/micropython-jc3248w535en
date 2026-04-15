"""
main.py — Auto-init display on boot for JC3248W535EN.

After flashing, every power-cycle or replug will:
  1. Init the board (LCD + touch)
  2. Turn on backlight at 80%
  3. Show a splash screen

The `d` object is then available in the REPL.
"""

from display import Display
from writer import Writer
import fonts.sans24 as sans24

d = Display(brightness=80)

d.fb.fill(d.BLACK)
wri24 = Writer(d.fb, sans24, verbose=False)
Writer.set_textpos(d.fb, 10, 10)
wri24.setcolor(d.YELLOW, d.BLACK)
wri24.printstring('Hello')
d.show()

print('done')
