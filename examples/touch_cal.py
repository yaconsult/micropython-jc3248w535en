"""
touch_cal.py — On-screen touch calibration / coordinate display.

Shows a target cross in each corner one at a time.
Tap it; the raw and mapped coordinates appear on screen.
Reuses `d` from main.py if available.
"""

import time

try:
    d
except NameError:
    from display import Display
    d = Display(brightness=80)

W, H = d.width, d.height
R = 16   # target cross radius


def draw_cross(x, y, color):
    d.fb.line(x - R, y, x + R, y, color)
    d.fb.line(x, y - R, x, y + R, color)
    d.fb.rect(x - 3, y - 3, 6, 6, color, True)


def show_prompt(msg1, msg2=''):
    d.fb.fill(d.BLACK)
    d.fb.text(msg1, (W - len(msg1)*8)//2, H//2 - 10, d.WHITE)
    if msg2:
        d.fb.text(msg2, (W - len(msg2)*8)//2, H//2 + 8, d.color(180,180,180))
    d.show()


def wait_tap(target_x, target_y, label):
    """Draw a target cross, wait for finger down then up, return raw point."""
    d.fb.fill(d.BLACK)
    draw_cross(target_x, target_y, d.YELLOW)
    d.fb.text('Tap the +', (W - 72)//2, H//2, d.color(180, 180, 180))
    d.fb.text(label, (W - len(label)*8)//2, H//2 + 16, d.color(100,100,200))
    d.show()

    # Make sure screen is not already being touched
    while d.board.read_touch() != []:
        time.sleep_ms(20)
    time.sleep_ms(100)

    # Wait for finger down — must stay down for at least 80ms
    while True:
        if d.board.read_touch() != []:
            time.sleep_ms(80)
            pt = d.board.read_touch()
            if pt:
                break
        time.sleep_ms(20)

    # Wait for full release before returning
    while d.board.read_touch() != []:
        time.sleep_ms(20)
    time.sleep_ms(150)  # debounce after release

    return pt[0]


def show_result(label, raw, mapped):
    d.fb.fill(d.BLACK)
    d.fb.text(label, 10, 20, d.YELLOW)
    d.fb.text('raw:    {},{}'.format(raw[0], raw[1]), 10, 50, d.WHITE)
    d.fb.text('mapped: {},{}'.format(mapped[0], mapped[1]), 10, 70, d.WHITE)
    d.fb.text('Tap anywhere', 10, 110, d.color(150,150,150))
    d.fb.text('to continue', 10, 125, d.color(150,150,150))
    d.show()
    while d.board.read_touch() == []:
        time.sleep_ms(20)
    while d.board.read_touch() != []:
        time.sleep_ms(20)


PAD = R + 4
corners = [
    (PAD,     PAD,     'TOP-LEFT'),
    (W-PAD,   PAD,     'TOP-RIGHT'),
    (W-PAD,   H-PAD,   'BOTTOM-RIGHT'),
    (PAD,     H-PAD,   'BOTTOM-LEFT'),
    (W//2,    H//2,    'CENTER'),
]

show_prompt('Touch Calibration', 'Tap each + cross')
time.sleep_ms(500)

results = []
for (tx, ty, label) in corners:
    raw = wait_tap(tx, ty, label)
    if raw:
        rx, ry = raw[0], raw[1]
        mx = min(max(rx, 0), W - 1)
        my = min(max(H - 1 - ry, 0), H - 1)
        results.append((label, tx, ty, rx, ry, mx, my))
        show_result(label, (rx, ry), (mx, my))

# Save to file
with open('cal_results.txt', 'w') as f:
    f.write('label,target_x,target_y,raw_x,raw_y,mapped_x,mapped_y\n')
    for r in results:
        f.write('{},{},{},{},{},{},{}\n'.format(*r))

show_prompt('Done!', 'Results in cal_results.txt')
