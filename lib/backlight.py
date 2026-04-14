"""
backlight.py — PWM backlight control for JC3248W535EN (GPIO 1, LEDC)

Usage:
    from backlight import Backlight
    bl = Backlight()
    bl.set(75)    # 75% brightness
    bl.on()       # full brightness
    bl.off()      # off (0%)
    bl.fade(0, 100, steps=50, delay_ms=10)
"""

from machine import Pin, PWM
import time


class Backlight:
    def __init__(self, pin=1, freq=1000):
        self._pwm = PWM(Pin(pin), freq=freq, duty=0)
        self._brightness = 0

    def set(self, percent):
        """Set brightness 0–100."""
        percent = max(0, min(100, percent))
        self._brightness = percent
        self._pwm.duty(int(percent / 100 * 1023))

    def on(self):
        """Full brightness."""
        self.set(100)

    def off(self):
        """Backlight off."""
        self.set(0)

    @property
    def brightness(self):
        return self._brightness

    def fade(self, start, end, steps=50, delay_ms=10):
        """Smoothly transition brightness from start% to end%."""
        for i in range(steps + 1):
            self.set(start + (end - start) * i // steps)
            time.sleep_ms(delay_ms)
