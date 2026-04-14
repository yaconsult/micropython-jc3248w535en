#!/usr/bin/env bash
# setup.sh — Clone and patch all dependencies to build MicroPython
#             for the JC3248W535EN board.
#
# Run once from the directory where you want your repos to live:
#   mkdir ~/Repos && cd ~/Repos
#   bash /path/to/this/setup.sh
#
# Requirements: git, ESP-IDF v5.4.2 already installed and on PATH

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_DIR="${1:-$PWD}"

echo "==> Setting up in: $REPOS_DIR"

# ── ESP32_Display_Panel ──────────────────────────────────────────────────────
if [ ! -d "$REPOS_DIR/ESP32_Display_Panel" ]; then
    git clone https://github.com/esp-arduino-libs/ESP32_Display_Panel.git \
        "$REPOS_DIR/ESP32_Display_Panel"
fi
echo "==> Applying ESP32_Display_Panel patch..."
git -C "$REPOS_DIR/ESP32_Display_Panel" apply --check "$SCRIPT_DIR/ESP32_Display_Panel.patch" \
    && git -C "$REPOS_DIR/ESP32_Display_Panel" am "$SCRIPT_DIR/ESP32_Display_Panel.patch" \
    || echo "    (patch may already be applied — skipping)"

# ── esp-lib-utils ────────────────────────────────────────────────────────────
if [ ! -d "$REPOS_DIR/esp-lib-utils" ]; then
    git clone https://github.com/esp-arduino-libs/esp-lib-utils.git \
        "$REPOS_DIR/esp-lib-utils"
fi

# ── ESP32_IO_Expander ────────────────────────────────────────────────────────
if [ ! -d "$REPOS_DIR/ESP32_IO_Expander" ]; then
    git clone https://github.com/esp-arduino-libs/ESP32_IO_Expander.git \
        "$REPOS_DIR/ESP32_IO_Expander"
fi

# ── MicroPython ──────────────────────────────────────────────────────────────
if [ ! -d "$REPOS_DIR/micropython" ]; then
    git clone https://github.com/micropython/micropython.git \
        "$REPOS_DIR/micropython"
    git -C "$REPOS_DIR/micropython" submodule update --init --depth 1
fi
echo "==> Applying micropython patch..."
git -C "$REPOS_DIR/micropython" apply "$SCRIPT_DIR/micropython.patch" \
    || echo "    (patch may already be applied — skipping)"

# ── USER_C_MODULES cmake ─────────────────────────────────────────────────────
cp "$SCRIPT_DIR/micropython_esp_panel.cmake" "$REPOS_DIR/"

echo ""
echo "==> Done.  To build:"
echo ""
echo "    source /path/to/esp-idf/export.sh"
echo "    make BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT \\"
echo "         USER_C_MODULES=$REPOS_DIR/micropython_esp_panel.cmake \\"
echo "         -C $REPOS_DIR/micropython/ports/esp32"
echo ""
echo "    See MICROPYTHON_JC3248W535EN.md for full flash instructions."
