"""
font_demo.py — Display custom fonts via writer.py
Run this after boot (not in main.py) to avoid QSPI flash/DMA conflict.

Usage:
    >>> exec(open('examples/font_demo.py').read())
"""

from display import Display
from writer import Writer
import fonts.sans16 as sans16
import fonts.sans24 as sans24

d = Display(brightness=80)

d.fb.fill(d.BLACK)
wri16 = Writer(d.fb, sans16, verbose=False)
wri24 = Writer(d.fb, sans24, verbose=False)

Writer.set_textpos(d.fb, 10, 10)
wri24.setcolor(d.YELLOW, d.BLACK)
wri24.printstring('JC3248W535EN')

Writer.set_textpos(d.fb, 50, 10)
wri16.setcolor(d.color(180, 220, 255), d.BLACK)
wri16.printstring('MicroPython Ready')

Writer.set_textpos(d.fb, 100, 10)
wri16.setcolor(d.CYAN, d.BLACK)
wri16.printstring('Temperature: 23.4 C\n')
wri16.printstring('Humidity:      61 %\n')
wri16.printstring('Pressure:  1013 hPa')

d.show()
print('Font demo complete.')
