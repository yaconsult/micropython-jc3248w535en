# micropython-jc3248w535en

Build infrastructure for a custom **MicroPython** firmware targeting the
**Jingcai JC3248W535EN** development board (ESP32-S3, 320×480 QSPI IPS
display, AXS15231B touch controller).

This repo does **not** contain the full source trees — it contains:

| File | Purpose |
|------|---------|
| `setup.sh` | Clone all dependencies and apply patches in one step |
| `ESP32_Display_Panel.patch` | Our changes to `esp-arduino-libs/ESP32_Display_Panel` |
| `micropython.patch` | Our changes to `micropython/micropython` |
| `micropython_esp_panel.cmake` | `USER_C_MODULES` entry point for the MicroPython build |
| `MICROPYTHON_JC3248W535EN.md` | Full technical reference — lessons learned, API docs, TODO |

---

## Quick start

### Prerequisites

- Linux (tested on Ubuntu/Debian)
- [ESP-IDF v5.4.2](https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/get-started/) installed
- Python 3, git, cmake, ninja

### 1. Clone this repo and run setup

```bash
mkdir ~/Repos && cd ~/Repos
git clone https://github.com/yaconsult/micropython-jc3248w535en.git
cd ~/Repos  # dependencies will be cloned here alongside this repo
bash micropython-jc3248w535en/setup.sh
```

### 2. Build

```bash
source ~/esp-idf/export.sh   # adjust path to your ESP-IDF install

make BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT \
     USER_C_MODULES=~/Repos/micropython_esp_panel.cmake \
     -C ~/Repos/micropython/ports/esp32
```

### 3. Flash

Enter bootloader on the board: hold **BOOT**, unplug USB, plug USB, release **BOOT**.

```bash
BUILD=~/Repos/micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT

python -m esptool --chip esp32s3 --port /dev/ttyACM0 -b 460800 \
  --before no_reset --after hard_reset write_flash \
  --flash_mode dio --flash_size 16MB --flash_freq 80m \
  0x0     $BUILD/bootloader/bootloader.bin \
  0x8000  $BUILD/partition_table/partition-table.bin \
  0x10000 $BUILD/micropython.bin
```

### 4. Use

```python
from esp_panel import Board

b = Board()
b.init()
b.begin()

# Solid blue screen
buf = bytearray([0x00, 0x1F] * (320 * 480))
b.draw_bitmap(0, 0, 320, 480, buf)

# Touch
points = b.read_touch()   # [(x, y, strength)] or []
```

See **[MICROPYTHON_JC3248W535EN.md](MICROPYTHON_JC3248W535EN.md)** for the
full API reference, RGB565 colour table, and all lessons learned.

---

## What works

- ✅ Display init (vendor init sequence — critical, default library sequence corrupts display)
- ✅ `draw_bitmap` — full and partial frame updates, correct RGB565 colours
- ✅ `read_touch` — X/Y coordinates via I2C AXS15231B touch controller
- ✅ `color_bar_test`, `get_width`, `get_height`

## What remains

- ⬜ Backlight PWM control
- ⬜ Python-level framebuffer helper (using PSRAM)
- ⬜ Multi-touch verification (API supports up to 5 points)
- ⬜ Test 40 MHz QSPI if pins can bypass GPIO matrix via IOMUX

---

## Board details

| | |
|-|-|
| MCU | ESP32-S3, 16 MB flash, 8 MB Octal PSRAM |
| Display | 3.2" 320×480 IPS, AXS15231B, QSPI @ 20 MHz |
| Touch | AXS15231B I2C, address 0x3B, SCL=GPIO8, SDA=GPIO4 |
| USB | USB CDC (`/dev/ttyACM0`) |
