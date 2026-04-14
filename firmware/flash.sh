#!/usr/bin/env bash
# flash.sh — Flash pre-built MicroPython firmware to the JC3248W535EN board.
#
# Usage:
#   bash flash.sh                      # auto-detect port, auto-reset
#   bash flash.sh /dev/ttyUSB0         # specify port
#
# Requirements: Python 3, esptool  (pip install esptool)

set -e
PORT="${1:-/dev/ttyACM0}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Flashing JC3248W535EN MicroPython firmware"
echo "    Port: $PORT"
echo ""
echo "    If flashing fails with a connection error, enter the bootloader manually:"
echo "    Hold BOOT → unplug USB → plug USB → release BOOT"
echo "    Then re-run this script with: bash flash.sh $PORT --no-reset"
echo ""

NO_RESET="${2:-}"
if [ "$NO_RESET" = "--no-reset" ]; then
    BEFORE="no_reset"
else
    BEFORE="default_reset"
fi

python3 -m esptool \
    --chip esp32s3 \
    --port "$PORT" \
    -b 460800 \
    --before "$BEFORE" \
    --after hard_reset \
    write_flash \
    --flash_mode dio \
    --flash_size 16MB \
    --flash_freq 80m \
    0x0     "$DIR/bootloader.bin" \
    0x8000  "$DIR/partition-table.bin" \
    0x10000 "$DIR/micropython.bin"

echo ""
echo "==> Flash complete. Unplug and replug USB to boot into MicroPython."
echo "    Connect with: python3 -m mpremote connect $PORT"
echo "    Or:           screen $PORT 115200"
