# GPIO Pin Assignments

This document outlines all GPIO pin assignments for the AI Gunshot Detection System to prevent conflicts and ensure proper hardware configuration.

> **Related Documentation:**
> - [Main README](README.md) - Project overview and quick start
> - [I2S Setup Guide](I2S_SETUP.md) - Detailed I2S microphone setup instructions

## Pin Assignment Summary

| Component | GPIO Pin | Physical Pin | Function | Notes |
|-----------|----------|--------------|----------|-------|
| **I2S Microphone (INMP441)** |
| SCK (BCLK) | GPIO 18 | Pin 12 | Bit Clock | I2S serial clock |
| WS (LRCL) | GPIO 19 | Pin 35 | Word Select | Left/Right clock |
| SD | GPIO 20 | Pin 38 | Serial Data | Audio data |
| **LED Alert** |
| LED | GPIO 26 | Pin 37 | Output | Alert indicator |

## Important Notes

### ✅ Conflict Resolution
- **Original Issue:** LED was configured on GPIO 18, which conflicts with I2S SCK (BCLK)
- **Previous Solution:** LED moved to GPIO 21 to avoid conflict
- **Current Configuration:** LED now on GPIO 26 (Pin 37)
- **Status:** ✅ **RESOLVED** - No GPIO conflicts

### I2S Pin Requirements
The I2S interface requires these specific GPIO pins:
- **GPIO 18** - Bit Clock (BCLK/SCK) - **DO NOT USE FOR OTHER PURPOSES**
- **GPIO 19** - Word Select (WS/LRCL) - **DO NOT USE FOR OTHER PURPOSES**
- **GPIO 20** - Serial Data (SD) - **DO NOT USE FOR OTHER PURPOSES**

### LED Pin
- **GPIO 26** - LED output (with 470Ω resistor) on Pin 37
- Can be changed in `yamnet_audio_classification/config.py` if needed
- Alternative pins: GPIO 22, 23, 24, 25 (if GPIO 26 is unavailable)

## Wiring Diagram

```
Raspberry Pi GPIO Header:

    3.3V  [1]  [2]  5V
   GPIO2  [3]  [4]  5V
   GPIO3  [5]  [6]  GND  ← INMP441 GND
   GPIO4  [7]  [8]  GPIO14
     GND  [9] [10]  GPIO15
  GPIO17 [11] [12]  GPIO18  ← INMP441 SCK (BCLK) ⚠️ I2S ONLY
  GPIO27 [13] [14]  GND
  GPIO22 [15] [16]  GPIO23
    3.3V [17] [18]  GPIO24
  GPIO10 [19] [20]  GND
   GPIO9 [21] [22]  GPIO25
  GPIO11 [23] [24]  GPIO8
     GND [25] [26]  GPIO7
   GPIO0 [27] [28]  GPIO1
   GPIO5 [29] [30]  GND
   GPIO6 [31] [32]  GPIO12
  GPIO13 [33] [34]  GND
  GPIO19 [35] [36]  GPIO16  ← INMP441 WS (LRCL) ⚠️ I2S ONLY
  GPIO26 [37] [38]  GPIO20  ← INMP441 SD ⚠️ I2S ONLY
     ↑
  LED Alert ✅
     GND [39] [40]  GPIO21
```

## Code Configuration

The GPIO pin assignments are configured in:
- **LED Pin:** `yamnet_audio_classification/config.py` → `LED_PIN = 26`
- **I2S Pins:** Hardware-defined (cannot be changed in software)

## Verification Checklist

- [x] LED configured on GPIO 26 (Pin 37, not GPIO 18)
- [x] I2S SCK on GPIO 18 (hardware requirement)
- [x] I2S WS on GPIO 19 (hardware requirement)
- [x] I2S SD on GPIO 20 (hardware requirement)
- [x] No GPIO conflicts
- [x] Documentation updated

## Troubleshooting

If you experience issues:

1. **LED not working:**
   - Verify LED is connected to GPIO 26 (Pin 37)
   - Check 470Ω resistor is in series
   - Verify LED polarity (long leg to GPIO, short leg through resistor to GND)

2. **I2S microphone not working:**
   - Verify I2S is enabled: `sudo raspi-config` → Interface Options → I2S
   - Check all three I2S pins are correctly wired
   - Ensure no other devices are using GPIO 18, 19, or 20

3. **GPIO conflicts:**
   - Never use GPIO 18, 19, or 20 for other purposes when using I2S
   - Check `config.py` to ensure LED_PIN is not set to 18, 19, or 20

