"""
main.py — Auto-init display on boot for JC3248W535EN.

After flashing, every power-cycle or replug will:
  1. Init the board (LCD + touch)
  2. Turn on backlight at 80%
  3. Show a splash screen

The `d` object is then available in the REPL.
"""

from display import Display
from writer import CWriter
import fonts.sans16 as sans16
import fonts.sans24 as sans24

d = Display(brightness=80)

d.fb.fill(d.BLACK)
wri16 = CWriter(d.fb, sans16, verbose=False)
wri24 = CWriter(d.fb, sans24, verbose=False)

CWriter.set_textpos(d.fb, 10, 10)
wri24.setcolor(d.YELLOW, d.BLACK)
wri24.printstring('JC3248W535EN')

CWriter.set_textpos(d.fb, 50, 10)
wri16.setcolor(d.color(180, 220, 255), d.BLACK)
wri16.printstring('MicroPython Ready')

d.show()
print('Display ready.')
