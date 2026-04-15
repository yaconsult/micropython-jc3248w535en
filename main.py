"""
main.py — Auto-init display on boot for JC3248W535EN.

After flashing, every power-cycle or replug will:
  1. Init the board (LCD + touch)
  2. Turn on backlight at 80%
  3. Show a splash screen

The `d` object is then available in the REPL.
"""

from display import Display

d = Display(brightness=80)

d.fb.fill(d.BLACK)
cx = (d.width - 13*8) // 2
d.text('JC3248W535EN', cx, d.height//2 - 20, d.WHITE)
d.text('MicroPython', (d.width - 11*8)//2, d.height//2, d.color(180, 220, 255))
d.text('Ready.', (d.width - 6*8)//2, d.height//2 + 20, d.YELLOW)
d.show()

print('Display ready.')
print('Run: exec(open("examples/font_demo.py").read())  # for custom fonts')
