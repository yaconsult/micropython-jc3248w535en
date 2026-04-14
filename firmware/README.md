# Pre-built firmware

Ready-to-flash MicroPython firmware for the **JC3248W535EN** board.

| File | Flash address |
|------|--------------|
| `bootloader.bin` | `0x0` |
| `partition-table.bin` | `0x8000` |
| `micropython.bin` | `0x10000` |

Built from:
- MicroPython `v1.29.0-preview` (`ESP32_GENERIC_S3 SPIRAM_OCT` variant)
- ESP-IDF v5.4.2
- ESP32_Display_Panel with JC3248W535EN patches

---

## Flash — automatic (Linux/macOS)

```bash
pip install esptool      # if not already installed
bash flash.sh            # uses /dev/ttyACM0 by default
bash flash.sh /dev/ttyUSB0   # specify a different port
```

## Flash — manual bootloader entry

If auto-reset fails:

1. Hold the **BOOT** button
2. Unplug the USB cable
3. Plug the USB cable back in
4. Release **BOOT**
5. Run:

```bash
bash flash.sh /dev/ttyACM0 --no-reset
```

## Flash — Windows / manual esptool

```
pip install esptool

esptool --chip esp32s3 --port COM3 -b 460800 --before default_reset --after hard_reset ^
  write_flash --flash_mode dio --flash_size 16MB --flash_freq 80m ^
  0x0 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
```

Replace `COM3` with your actual port (check Device Manager).

---

## First use

After flashing, unplug and replug USB. Connect to the REPL:

```bash
python3 -m mpremote connect /dev/ttyACM0
# or
screen /dev/ttyACM0 115200
```

```python
from esp_panel import Board

b = Board()
b.init()
b.begin()

# Solid red screen
buf = bytearray([0xF8, 0x00] * (320 * 480))
b.draw_bitmap(0, 0, 320, 480, buf)

# Read touch coordinates
print(b.read_touch())   # tap the screen
```

See the top-level [MICROPYTHON_JC3248W535EN.md](../MICROPYTHON_JC3248W535EN.md)
for the full API reference.
