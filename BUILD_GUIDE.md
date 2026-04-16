# Build Guide — MicroPython for JC3248W535EN

Complete instructions to set up the build environment, build the firmware,
flash it, and deploy the Python library files to the board.

---

## Prerequisites

### Hardware
- Jingcai JC3248W535EN development board (ESP32-S3, 3.2" 320×480 QSPI display)
- USB cable (USB-C to your host)

### Software
- Linux host (Ubuntu 22.04 / Debian tested; WSL2 works with caveats)
- Python 3.10+
- `git`, `cmake`, `ninja`, `wget`
- ESP-IDF v5.4.2

### Install ESP-IDF v5.4.2

Follow the official guide, or run:

```bash
mkdir -p ~/esp && cd ~/esp
git clone --branch v5.4.2 --depth 1 https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32s3
```

> The `install.sh` step downloads compilers and tools (~1 GB). Only needs to
> run once.

Add this line to your `~/.bashrc` (or run it in every terminal session):
```bash
alias get_idf='source ~/esp/esp-idf/export.sh'
```

---

## One-time setup

### 1. Clone this repo

```bash
mkdir -p ~/Repos && cd ~/Repos
git clone https://github.com/yaconsult/micropython-jc3248w535en.git
```

### 2. Run setup.sh

This clones all dependencies and applies our patches in one step:

```bash
cd ~/Repos
bash micropython-jc3248w535en/setup.sh
```

What `setup.sh` does:
- Clones `ESP32_Display_Panel` (Espressif display/touch driver)
- Applies `ESP32_Display_Panel.patch` (our board header + MicroPython wrapper)
- Clones `esp-lib-utils` and `ESP32_IO_Expander` (dependencies)
- Clones `micropython` and runs `submodule update`
- Applies `micropython.patch` (our ESP32 port integration)
- Copies `micropython_esp_panel.cmake` to `~/Repos/`

After `setup.sh`, your `~/Repos/` will contain:

```
~/Repos/
├── micropython-jc3248w535en/   ← our repo (source of truth)
├── ESP32_Display_Panel/        ← patched fork
├── ESP32_IO_Expander/          ← unmodified dependency
├── esp-lib-utils/              ← unmodified dependency
├── micropython/                ← patched fork
└── micropython_esp_panel.cmake ← USER_C_MODULES entry point
```

---

## Build

```bash
source ~/esp/esp-idf/export.sh   # activate ESP-IDF (adjust path if needed)

make BOARD=ESP32_GENERIC_S3 \
     BOARD_VARIANT=SPIRAM_OCT \
     USER_C_MODULES=~/Repos/micropython_esp_panel.cmake \
     -C ~/Repos/micropython/ports/esp32
```

Build output goes to:
```
~/Repos/micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT/
```

A successful build ends with:
```
bootloader  @0x000000    ~19 KB
partitions  @0x008000     ~3 KB
application @0x010000  ~1750 KB
```

> First build takes ~5-10 minutes. Incremental rebuilds (after changing only
> Python or C files in `mpy_support/`) take ~30 seconds.

---

## Flash

### Enter bootloader mode

Hold **BOOT**, unplug USB, plug USB back in, release **BOOT**.

The board will appear as `/dev/ttyACM0` (Linux) in bootloader mode.

### Flash all three binaries

```bash
BUILD=~/Repos/micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT

python3 -m esptool --chip esp32s3 --port /dev/ttyACM0 -b 460800 \
  --before no_reset --after hard_reset write_flash \
  --flash_mode dio --flash_size 16MB --flash_freq 80m \
  0x0     $BUILD/bootloader/bootloader.bin \
  0x8000  $BUILD/partition_table/partition-table.bin \
  0x10000 $BUILD/micropython.bin
```

> If the board is already running MicroPython (not in bootloader), try
> `--before default_reset` to auto-reset via DTR/RTS. This works most of the
> time, but if it times out you need to enter bootloader mode manually.

---

## Deploy Python library files

After flashing, the board runs bare MicroPython with no library files. Deploy
the `lib/` folder from this repo:

```bash
python3 -m mpremote connect /dev/ttyACM0 resume \
  cp -r ~/Repos/micropython-jc3248w535en/lib/ :
```

Deploy `main.py` and examples:

```bash
python3 -m mpremote connect /dev/ttyACM0 resume \
  cp ~/Repos/micropython-jc3248w535en/main.py :main.py + \
  mkdir :examples + \
  cp -r ~/Repos/micropython-jc3248w535en/examples/ :examples/
```

Verify what's on the board:

```bash
python3 -m mpremote connect /dev/ttyACM0 ls :
python3 -m mpremote connect /dev/ttyACM0 ls :lib/
```

---

## Verify it works

Reset the board:
```bash
python3 -m mpremote connect /dev/ttyACM0 reset
```

The display should show the splash screen:
- **"JC3248W535EN"** in yellow (sans24 font)
- **"MicroPython Ready"** in light blue (sans16 font)

Open a REPL:
```bash
python3 -m mpremote connect /dev/ttyACM0
```

Try the font demo:
```python
>>> exec(open('examples/font_demo.py').read())
```

---

## Making changes

### Modifying Python library files (`lib/`, `main.py`)

Edit locally, then push to the board with `mpremote cp`. No rebuild needed.

```bash
python3 -m mpremote connect /dev/ttyACM0 resume \
  cp ~/Repos/micropython-jc3248w535en/lib/display.py :lib/display.py
```

### Modifying the C++ MicroPython wrapper (`ESP32_Display_Panel/mpy_support/`)

These files are compiled into the firmware. After editing:
1. Rebuild (incremental — fast):
   ```bash
   source ~/esp/esp-idf/export.sh
   make BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT \
        USER_C_MODULES=~/Repos/micropython_esp_panel.cmake \
        -C ~/Repos/micropython/ports/esp32
   ```
2. Reflash (enter bootloader mode first):
   ```bash
   BUILD=~/Repos/micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT
   python3 -m esptool --chip esp32s3 --port /dev/ttyACM0 -b 460800 \
     --before no_reset --after hard_reset write_flash \
     --flash_mode dio --flash_size 16MB --flash_freq 80m \
     0x0 $BUILD/bootloader/bootloader.bin \
     0x8000 $BUILD/partition_table/partition-table.bin \
     0x10000 $BUILD/micropython.bin
   ```
3. Re-deploy Python files (the flash wipes the filesystem):
   ```bash
   python3 -m mpremote connect /dev/ttyACM0 resume \
     cp -r ~/Repos/micropython-jc3248w535en/lib/ : + \
     cp ~/Repos/micropython-jc3248w535en/main.py :main.py
   ```

### Modifying the board configuration (`BOARD_JC3248W535EN.h`)

Same as C++ changes above — requires rebuild + reflash.

Key settings in `ESP32_Display_Panel/src/board/supported/jingcai/BOARD_JC3248W535EN.h`:

| Setting | Value | Notes |
|---------|-------|-------|
| `ESP_PANEL_BOARD_LCD_QSPI_CLK_HZ` | `20 * 1000 * 1000` | 40 MHz also works but gives no fps gain |
| `ESP_PANEL_BOARD_LCD_VENDOR_INIT_CMD()` | vendor sequence | Must NOT be changed — display goes blank without it |

After modifying either repo (`ESP32_Display_Panel/` or `micropython/`),
update the patches so `setup.sh` stays in sync:

```bash
git -C ~/Repos/ESP32_Display_Panel diff origin/master HEAD -- \
  > ~/Repos/micropython-jc3248w535en/ESP32_Display_Panel.patch

git -C ~/Repos/micropython diff origin/master HEAD -- \
  > ~/Repos/micropython-jc3248w535en/micropython.patch

cd ~/Repos/micropython-jc3248w535en
git add *.patch && git commit -m "Update patches" && git push
```

---

## Adding new fonts

Fonts are generated from TTF files using
[`font_to_py.py`](https://github.com/peterhinch/micropython-font-to-py):

```bash
# Install if needed
pip3 install freetype-py

# Generate a 24px sans font (horizontally mapped, no reverse)
python3 font_to_py.py -x YourFont.ttf 24 sans24.py

# Copy to board
python3 -m mpremote connect /dev/ttyACM0 resume \
  cp sans24.py :lib/fonts/sans24.py
```

Use `CWriter` (not `Writer`) to render on this colour display:

```python
from writer import CWriter
import fonts.sans24 as sans24

wri = CWriter(d.fb, sans24, verbose=False)
CWriter.set_textpos(d.fb, row=50, col=10)
wri.setcolor(d.YELLOW, d.BLACK)
wri.printstring('Hello!')
d.show()
```

> **`Writer.setcolor()` silently ignores its arguments.** Always use `CWriter`
> for colour displays.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Blank display on boot | `board.begin()` called twice (soft reset) | Already fixed via C++ static guard — hard reset if still occurring |
| Black rectangle instead of text | Using `Writer` instead of `CWriter` | Change to `CWriter` |
| Hard fault / crash during font rendering | Glyph data read from flash during LCD DMA | Already fixed — `bytearray(self.glyph)` in `CWriter._printchar()` |
| Pixel noise | QSPI clock too high or bad connection | Confirm clock is 20 MHz in board header |
| `read_touch()` always returns `[]` | `machine.I2C` used on pins 4 or 8 | Reboot; never use `machine.I2C(0)` — touch driver owns that bus |
| `mpremote` write timeout | Board not in bootloader mode | Hold BOOT, replug USB, release BOOT |
| `could not enter raw repl` | Board still running `main.py` | Use `resume` flag: `mpremote connect ... resume exec ...` |

---

## Reference

- [`MICROPYTHON_JC3248W535EN.md`](MICROPYTHON_JC3248W535EN.md) — full technical reference, all lessons learned
- [`REPOS_INVENTORY.md`](REPOS_INVENTORY.md) — inventory of all repos in `~/Repos/`
- [micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py) — font generation and `CWriter` documentation
- [ESP-IDF v5.4.2 docs](https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/)
