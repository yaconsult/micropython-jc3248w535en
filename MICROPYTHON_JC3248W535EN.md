# MicroPython + ESP32_Display_Panel on the JC3248W535EN

A complete guide to building custom MicroPython firmware for the
**Jingcai JC3248W535EN** development board, integrating the
`ESP32_Display_Panel` library for QSPI display and capacitive touch support.

---

## Hardware

| Component | Details |
|-----------|---------|
| MCU | ESP32-S3, 16 MB flash, 8 MB Octal PSRAM |
| Display | 3.2" 320×480 IPS, AXS15231B controller, QSPI |
| Touch | AXS15231B capacitive touch, I2C |
| USB | USB CDC (appears as `/dev/ttyACM0` on Linux) |

### Pin assignments

| Signal | GPIO |
|--------|------|
| QSPI SCK | 47 |
| QSPI DATA0 | 21 |
| QSPI DATA1 | 48 |
| QSPI DATA2 | 40 |
| QSPI DATA3 | 39 |
| QSPI CS | 45 |
| Touch SCL (I2C0) | 8 |
| Touch SDA (I2C0) | 4 |
| Touch I2C address | 0x3B |

---

## Repository layout

```
/home/lpinard/Repos/
├── micropython/                 # MicroPython fork
├── esp-idf/                     # ESP-IDF v5.4.2
├── ESP32_Display_Panel/         # Espressif display/touch library (modified)
├── esp-lib-utils/               # Dependency of ESP32_Display_Panel
├── ESP32_IO_Expander/           # Dependency of ESP32_Display_Panel
└── micropython_esp_panel.cmake  # USER_C_MODULES entry point
```

---

## Build

```bash
source /home/lpinard/Repos/esp-idf/export.sh

make BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT \
     USER_C_MODULES=/home/lpinard/Repos/micropython_esp_panel.cmake \
     -C /home/lpinard/Repos/micropython/ports/esp32
```

Output binaries are in:
`micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT/`

---

## Flash

Enter bootloader: hold **BOOT**, unplug USB, plug USB, release **BOOT**.

```bash
source /home/lpinard/Repos/esp-idf/export.sh

BUILD=micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT

python -m esptool --chip esp32s3 --port /dev/ttyACM0 -b 460800 \
  --before no_reset --after hard_reset write_flash \
  --flash_mode dio --flash_size 16MB --flash_freq 80m \
  0x0     $BUILD/bootloader/bootloader.bin \
  0x8000  $BUILD/partition_table/partition-table.bin \
  0x10000 $BUILD/micropython.bin
```

> If the board is running MicroPython (not in bootloader), try
> `--before default_reset` — it will attempt auto-reset via DTR/RTS.
> This works most of the time but occasionally fails and requires manual
> bootloader entry.

---

## MicroPython API

```python
from esp_panel import Board

b = Board()
b.init()   # returns True on success
b.begin()  # returns True on success — initialises display + touch

# Display info
b.get_width()   # 320
b.get_height()  # 480

# Draw a solid red screen (RGB565, big-endian byte order)
buf = bytearray([0xF8, 0x00] * (320 * 480))
b.draw_bitmap(0, 0, 320, 480, buf)   # returns True

# Draw a partial region  (x, y, width, height, buf)
stripe = bytearray([0x07, 0xE0] * (320 * 30))   # green, 30 rows
b.draw_bitmap(0, 100, 320, 30, stripe)

# Color bar test (built-in)
b.color_bar_test()   # returns True, draws 16 colour bars on screen

# Touch — returns list of (x, y, strength) tuples; [] when not touching
points = b.read_touch()
# e.g. [(194, 300, 0)]  — strength is always 0 for AXS15231B

b.deinit()
```

### RGB565 colour reference (big-endian)

| Colour | Bytes |
|--------|-------|
| Red | `0xF8, 0x00` |
| Green | `0x07, 0xE0` |
| Blue | `0x00, 0x1F` |
| White | `0xFF, 0xFF` |
| Black | `0x00, 0x00` |
| Yellow | `0xFF, 0xE0` |

> **Important:** `draw_bitmap` expects standard RGB565 big-endian bytes.
> The wrapper byte-swaps internally before sending over QSPI, so you do
> **not** need to pre-swap.

---

## Key implementation decisions and hard-won lessons

### 1. Vendor init sequence is mandatory

The `ESP32_Display_Panel` library ships a default AXS15231B init sequence
that includes command `0x22` (ALL_PIXELS_OFF). Using it results in a blank
or corrupted display.

The fix: `BOARD_JC3248W535EN.h` now defines
`ESP_PANEL_BOARD_LCD_VENDOR_INIT_CMD()` with the full init sequence from
the vendor's official Arduino demo (`esp_bsp.c`). This must end with
`0x2C` (RAMWR) — not `0x29` (DISPLAY_ON).

### 2. QSPI clock: 20 MHz chosen, 40 MHz also works

The QSPI pins on this board are routed through the ESP32-S3 GPIO matrix (not
IOMUX — the IOMUX pins for SPI2 are GPIO 9/10/11/12/13/14, none of which are
used here). Per the ESP-IDF docs, the GPIO matrix is stable at 40 MHz and
below on ESP32-S3.

**40 MHz was tested and works correctly** with no pixel noise. However it
provides **no measurable fps improvement** — 100 full-frame flushes at both
20 MHz and 40 MHz take ~17 000 ms (~5.9 fps). The bottleneck is CPU time in
the chunked `draw_bitmap` loop, not bus bandwidth.

20 MHz is kept as the default for margin. Change to 40 MHz in
`BOARD_JC3248W535EN.h` if needed:
```c
#define ESP_PANEL_BOARD_LCD_QSPI_CLK_HZ  (40 * 1000 * 1000)  // safe, but no fps gain
```

### 3. draw_bitmap must send in chunks

A single `esp_lcd_panel_draw_bitmap` call with a 307 200-byte buffer
(full 320×480 RGB565 frame) blocks indefinitely waiting for the SPI DMA
completion semaphore. The driver only fires the `on_color_trans_done`
callback once per queued transaction and the transaction size is limited.

The wrapper sends 30 rows at a time (matching `colorBarTest` internally):
```cpp
int chunk_rows = 30;  // ~19 200 bytes per chunk at RGB565
```

### 4. QSPI byte order

The AXS15231B QSPI driver applies `SPI_SWAP_DATA_TX` (bit reversal within
the 16-bit word) to pixel data. The MicroPython wrapper compensates by
byte-swapping each 16-bit pixel before handing it to `drawBitmap`, so
callers can use standard big-endian RGB565.

### 5. Do not use machine.I2C on touch pins

`machine.I2C(0, scl=Pin(8), sda=Pin(4))` will conflict with the
`ESP32_Display_Panel` touch driver which owns I2C bus 0. Using it before
or after `b.begin()` leaves the bus in a state where `read_touch()` always
returns `[]`. Reboot to recover.

### 6. Configuration file skip flags

The library checks Kconfig symbols `CONFIG_ESP_PANEL_BOARD_FILE_SKIP` and
`CONFIG_ESP_PANEL_DRIVERS_FILE_SKIP`. If set (the Kconfig default when
building outside the library's own project), the `.h` config files are
ignored. Override in
`boards/ESP32_GENERIC_S3/sdkconfig.esp_panel`:

```
CONFIG_ESP_PANEL_BOARD_FILE_SKIP=n
CONFIG_ESP_PANEL_DRIVERS_FILE_SKIP=n
CONFIG_ESP_UTILS_CONF_FILE_SKIP=n
```

### 7. board.begin() must only be called once per hard boot

Calling `board.begin()` more than once corrupts the display — it re-runs the
vendor init sequence including a display-off command, leaving a blank screen.
This happens on MicroPython soft resets which re-import `main.py`.

Fix: **C++ static guard** in `mpy_support/esp_panel_mp_board.cpp`:
```cpp
static std::weak_ptr<Board> g_board_instance;  // persist Board across soft resets
static bool g_board_began = false;             // only begin() once per hard boot
```
`make_new` reuses the existing `Board` object if `weak_ptr` is still live.
`board_begin` checks `g_board_began` and skips if already done.
Static C++ variables survive MicroPython soft resets (C heap, not MP heap).

### 8. Use CWriter, not Writer, for colour displays

`writer.py` (from `micropython-font-to-py`) has two classes:

| Class | For | `setcolor()` |
|-------|-----|-------------|
| `Writer` | Monochrome only | **Ignores arguments** — always renders 0/1 |
| `CWriter` | Colour RGB565 | Correctly sets fg/bg palette colours |

`Writer.setcolor(d.YELLOW, d.BLACK)` silently does nothing. Always use `CWriter`:

```python
from writer import CWriter   # NOT Writer
wri = CWriter(d.fb, font, verbose=False)
CWriter.set_textpos(d.fb, row, col)
wri.setcolor(d.YELLOW, d.BLACK)
wri.printstring('Hello!')
```

### 9. ESP32-S3 QSPI/DMA conflict with font data in flash

Reading font glyph data via `memoryview` directly from flash while LCD DMA
is active can cause a hard fault — the CPU and LCD DMA share the QSPI bus.

Fix in `CWriter._printchar()`:
```python
buf = bytearray(self.glyph)  # copy from flash into RAM before blit
fbc = framebuf.FrameBuffer(buf, self.char_width, self.char_height, self.map)
```

### 10. Board header macro syntax

`ESP_PANEL_BOARD_LCD_VENDOR_INIT_CMD()` is expanded as:
```c
static const esp_panel_lcd_vendor_init_cmd_t lcd_vendor_init_cmds[] =
    ESP_PANEL_BOARD_LCD_VENDOR_INIT_CMD();
```
The macro must therefore expand to `{ {...}, {...}, ... }` — **outer braces
included inside the macro**.

---

## Files modified

### `ESP32_Display_Panel/` repo

| File | Change |
|------|--------|
| `src/board/supported/jingcai/BOARD_JC3248W535EN.h` | QSPI clock → 20 MHz; added full vendor init sequence; touch pins SCL=8 SDA=4 |
| `esp_panel_board_supported_conf.h` | Enabled `BOARD_JC3248W535EN` |
| `CMakeLists.txt` | Added `.` to `INCLUDE_DIRS` so conf headers are found |
| `mpy_support/esp_panel_mp_board.cpp` | Added `draw_bitmap`, `get_width`, `get_height`, `read_touch`; added `g_board_instance` weak_ptr + `g_board_began` static flag (lesson 7) |

### `micropython/` repo

| File | Change |
|------|--------|
| `ports/esp32/CMakeLists.txt` | Added `EXTRA_COMPONENT_DIRS` for ESP32_Display_Panel and dependencies |
| `ports/esp32/esp32_common.cmake` | Appended `ESP32_Display_Panel`, `esp-lib-utils`, `ESP32_IO_Expander` to `IDF_COMPONENTS` |
| `ports/esp32/main/idf_component.yml` | Listed dependencies |
| `ports/esp32/boards/ESP32_GENERIC_S3/sdkconfig.esp_panel` | FILE_SKIP overrides *(new file)* |
| `ports/esp32/boards/ESP32_GENERIC_S3/mpconfigvariant_SPIRAM_OCT.cmake` | Added `sdkconfig.esp_panel` to `SDKCONFIG_DEFAULTS` |

### `micropython_esp_panel.cmake` (standalone)

USER_C_MODULES entry point — registers `mpy_support/` sources with
MicroPython's build system.

---

## What remains to be done

- [x] **Multi-touch test** — `readPoints(5)` is called in C++ but the AXS15231B IC on this board only ever returns 1 point; hardware-limited to single touch
- [ ] **Upstream contributions** — submit board header fixes and mpy_support additions back to ESP32_Display_Panel
- [x] **Test at 40 MHz** — works (GPIO matrix is stable at ≤40 MHz on ESP32-S3); no fps gain vs 20 MHz; CPU is bottleneck

## What is done

- [x] Vendor LCD init sequence (lesson 1)
- [x] QSPI clock at 20 MHz (lesson 2)
- [x] `draw_bitmap` chunked DMA (lesson 3)
- [x] RGB565 byte order (lesson 4)
- [x] Touch I2C ownership (lesson 5)
- [x] Kconfig FILE_SKIP overrides (lesson 6)
- [x] `board.begin()` idempotent across soft resets — C++ static guard (lesson 7)
- [x] Custom fonts via `CWriter` (lesson 8)
- [x] QSPI/DMA flash conflict fix — glyph RAM copy (lesson 9)
- [x] Backlight PWM (`lib/backlight.py`)
- [x] RGB565 framebuffer in PSRAM (`lib/framebuf_rgb565.py`)
- [x] `main.py` auto-init with font splash screen
- [x] `Display` high-level wrapper (`lib/display.py`)
