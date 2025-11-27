# INMP441 I2S Microphone Setup Guide

This guide provides detailed instructions for setting up the INMP441 24-bit I2S omnidirectional microphone on your Raspberry Pi for the AI Gunshot Detection System.

> **Related Documentation:**
> - [Main README](README.md) - Project overview and quick start
> - [GPIO Pin Assignments](GPIO_PIN_ASSIGNMENTS.md) - Complete pin mapping and conflict prevention

## Hardware Connections

Connect the INMP441 to your Raspberry Pi as follows:

| INMP441 Pin | Raspberry Pi Pin | GPIO Number | Description |
|-------------|------------------|-------------|-------------|
| VDD         | Pin 1 (3.3V)     | -           | Power (3.3V) |
| GND         | Pin 6 (GND)      | -           | Ground |
| WS (LRCL)   | Pin 35           | GPIO 19     | Word Select (Left/Right Clock) |
| SCK (BCLK)  | Pin 12           | GPIO 18     | Bit Clock |
| SD          | Pin 38           | GPIO 20     | Serial Data |

**Important:** The LED alert uses **GPIO 26 (Pin 37)**, not GPIO 18, to avoid conflict with the I2S Bit Clock signal.

**Important:** Make sure to use 3.3V for VDD, not 5V, as the INMP441 is a 3.3V device.

## Software Configuration

### 1. Enable I2S Interface

Edit the Raspberry Pi configuration:

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **I2S** → **Enable**

Alternatively, you can enable I2S by editing the config file:

**For Raspberry Pi OS (Bullseye and earlier):**
```bash
sudo nano /boot/config.txt
```

**For Raspberry Pi OS (Bookworm and later):**
```bash
sudo nano /boot/firmware/config.txt
```

Add or uncomment this line:
```
dtparam=i2s=on
```

> **Note:** The INMP441 does not require a device tree overlay. Simply enabling I2S is sufficient. The `dtoverlay=adau7002-simple` is for different microphone modules, not the INMP441.

Reboot your Raspberry Pi:
```bash
sudo reboot
```

### 2. Install Required Packages

The system uses `sounddevice` which interfaces with ALSA. Make sure ALSA utilities are installed:

```bash
sudo apt-get update
sudo apt-get install -y alsa-utils python3-pip
```

### 3. Verify I2S Device

After rebooting, check if the I2S device is recognized:

```bash
arecord -l
```

You should see your I2S device listed. Common names include:
- `seeed-2mic-voicecard`
- `I2S` or similar

You can also check with:

```bash
aplay -l
```

### 4. Test Audio Recording

Test the microphone with:

```bash
arecord -D hw:1,0 -f S16_LE -r 16000 -c 2 -d 5 test.wav
```

**Parameters explained:**
- `-D hw:1,0` → I2S device (check `arecord -l` for your device number)
- `-f S16_LE` → 16-bit samples (INMP441 supports 16-bit)
- `-r 16000` → 16 kHz sample rate (required by YAMNet)
- `-c 2` → Stereo channels (I2S device requires 2 channels, converted to mono by software)
- `-d 5` → Record for 5 seconds

After recording, play it back to verify:

```bash
aplay test.wav
```

> **Important:** The I2S device requires **2 channels (stereo)** for recording, even though the INMP441 is a mono microphone. The detection software automatically converts stereo to mono for YAMNet processing.

> **Note:** If `hw:1,0` doesn't work, check your device number with `arecord -l` and use the appropriate `hw:X,Y` value.

### 5. Configure in the Project

The audio detection system will auto-detect I2S devices. If you need to specify a particular device:

1. Edit `yamnet_audio_classification/config.py`
2. Set `I2S_DEVICE_NAME` to match your device name from `arecord -l`
3. Or leave it as `None` for auto-detection

Example:
```python
I2S_DEVICE_NAME = "seeed-2mic-voicecard"  # If your device has this name
```

## Troubleshooting

### Device Not Found

If the I2S device is not detected:

1. **Check wiring** - Verify all connections match the [GPIO Pin Assignments](GPIO_PIN_ASSIGNMENTS.md)
2. **Verify I2S is enabled** - Check `/boot/config.txt` (or `/boot/firmware/config.txt` on newer OS) has `dtparam=i2s=on` 
3. **Reboot required** - I2S changes require a reboot: `sudo reboot`
4. **Check device list** - Run `arecord -l` to see all available audio devices
5. **Try USB fallback** - Set `USE_I2S = False` in `config.py` to use USB microphone

### No Audio Input

If you get no audio:

1. **Check volume levels:**
   ```bash
   alsamixer
   ```
   Press `F6` to select your I2S device, then adjust volume with arrow keys

2. **Test with arecord:**
   ```bash
   arecord -D hw:1,0 -f S16_LE -r 16000 -c 2 -d 5 test.wav
   ```
   Replace `hw:1,0` with your actual device from `arecord -l`
   
   > **Note:** Use `-c 2` (stereo) as the I2S device requires 2 channels

3. **Check permissions:**
   ```bash
   sudo usermod -a -G audio $USER
   ```
   Then log out and log back in (or reboot)

4. **Verify wiring** - Double-check all connections against the [GPIO Pin Assignments](GPIO_PIN_ASSIGNMENTS.md)

### Low Quality Audio

For better audio quality:

1. Ensure proper power supply (3.3V, stable)
2. Keep wires short to reduce interference
3. Use proper grounding
4. Check that sample rate matches (16kHz for YAMNet)

## Alternative: Using USB Microphone

If you prefer to use a USB microphone instead:

1. Edit `yamnet_audio_classification/config.py`
2. Set `USE_I2S = False`
3. The system will automatically use PyAudio with USB devices

## Additional Resources

- [Main README](README.md) - Project overview and quick start guide
- [GPIO Pin Assignments](GPIO_PIN_ASSIGNMENTS.md) - Complete pin mapping reference
- [Raspberry Pi I2S Documentation](https://www.raspberrypi.org/documentation/configuration/audio-config.md)
- [INMP441 Datasheet](https://www.invensense.com/products/digital/inmp441/)
- [ALSA Documentation](https://www.alsa-project.org/wiki/Documentation)

---

## Quick Reference

**I2S Pin Connections:**
- VDD → 3.3V (Pin 1)
- GND → GND (Pin 6)
- WS (LRCL) → GPIO 19 (Pin 35)
- SCK (BCLK) → GPIO 18 (Pin 12)
- SD → GPIO 20 (Pin 38)

**LED Connection:**
- LED → GPIO 26 (Pin 37) with 470Ω resistor

**Audio Configuration:**
- I2S device requires **2 channels (stereo)** input
- Detection software converts stereo to mono for YAMNet
- Sample rate: 16kHz (required by YAMNet)
- Detection threshold: 0.2 (20% confidence)

See [GPIO_PIN_ASSIGNMENTS.md](GPIO_PIN_ASSIGNMENTS.md) for complete wiring diagram.

---

## Audio Output (WM8960 Audio HAT)

This system uses a **WM8960 Audio HAT** for audio output to play alarm sounds when gunshot detection occurs. The WM8960 Audio HAT connects to the Raspberry Pi GPIO header and provides a low-power speaker output.

**Installation:**

1. Insert the WM8960 Audio HAT onto the Raspberry Pi GPIO header
2. Connect your external speaker to the WM8960 Audio HAT
3. Install the driver:
   ```bash
   git clone https://github.com/waveshare/WM8960-Audio-HAT
   cd WM8960-Audio-HAT
   sudo ./install.sh
   sudo reboot
   ```

4. After rebooting, verify installation:
   ```bash
   sudo dkms status
   ```

**Note:** The alarm sound will automatically play through the WM8960 Audio HAT when `ENABLE_SOUND_ALERT = True` in `config.py`. The WM8960 Audio HAT does not conflict with the INMP441 I2S microphone as they use different I2S channels.

---
