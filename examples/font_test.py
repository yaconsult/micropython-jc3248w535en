"""
font_test.py — Test Liberation Sans bitmap fonts via writer.py

    mpremote run examples/font_test.py
"""

from display import Display
from writer import Writer
import fonts.sans16 as sans16
import fonts.sans24 as sans24
import fonts.sans32 as sans32

d = Display(brightness=80)
d.fb.fill(d.BLACK)

wri16 = Writer(d.fb, sans16, verbose=False)
wri24 = Writer(d.fb, sans24, verbose=False)
wri32 = Writer(d.fb, sans32, verbose=False)

Writer.set_textpos(d.fb, 10, 10)
wri16.setcolor(d.color(180, 180, 180), d.BLACK)
wri16.printstring('Sans 16px - Hello World!\n')

Writer.set_textpos(d.fb, 40, 10)
wri24.setcolor(d.WHITE, d.BLACK)
wri24.printstring('Sans 24px - Hello!\n')

Writer.set_textpos(d.fb, 80, 10)
wri32.setcolor(d.YELLOW, d.BLACK)
wri32.printstring('Sans 32px\n')

Writer.set_textpos(d.fb, 130, 10)
wri16.setcolor(d.CYAN, d.BLACK)
wri16.printstring('Temperature: 23.4 C\n')
wri16.printstring('Humidity:    61 %\n')
wri16.printstring('Pressure:  1013 hPa\n')

d.show()
