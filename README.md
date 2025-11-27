# Raspberry Pi AI Shot Spotter

An AI-powered real-time **gunshot detection system** using YAMNet on Raspberry Pi, capable of:

- Detecting **gunshot sounds** in real-time using Google's YAMNet model
- Supporting **INMP441 24-bit I2S omnidirectional microphone** for high-quality audio capture
- Activating a **warning LED** for 5 seconds when gunshot is detected
- Logging detection events locally for traceability

## 📋 Table of Contents

- [About YAMNet and AudioSet](#about-yamnet-and-audioset)
- [How It Works](#how-it-works)
- [Hardware Setup](#hardware-setup)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [Customization](#customization)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

---

## About YAMNet and AudioSet

This project leverages **YAMNet** (Yet Another Mobile Network), a deep learning model from Google's **TensorFlow Model Garden**, which was trained on the **AudioSet** dataset. Understanding these components helps clarify how the detection system works:

- **AudioSet** is a large-scale audio ontology dataset created by Google, containing over 2 million labeled 10-second audio clips from YouTube videos, organized into 632 hierarchical sound event classes. It serves as the training foundation for audio classification models, providing a comprehensive taxonomy of real-world sounds including gunshots, explosions, music, speech, and environmental sounds. AudioSet Ontology: [Gunshot, gunfire class](https://research.google.com/audioset/balanced_train/gunshot_gunfire.html)

- **YAMNet** is a pre-trained deep neural network model that was trained on the AudioSet dataset. It can classify audio into 521 of the AudioSet sound classes with high accuracy. YAMNet is optimized for mobile and edge devices, making it ideal for Raspberry Pi deployment. The model takes 16kHz mono audio as input and outputs predictions for multiple sound classes simultaneously. Official sources: [Kaggle Model](https://www.kaggle.com/models/google/yamnet) 

- **TensorFlow Model Garden** is a collection of state-of-the-art machine learning models, implementations, and tools maintained by the TensorFlow team. YAMNet is part of this collection, providing a standardized, well-tested implementation that can be easily integrated into applications. The Model Garden ensures consistent APIs, documentation, and best practices across different models. Official sources: [TensorFlow Models Repository](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet) Official sources: [TensorFlow Models Repository](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet)

**In this project:** We use YAMNet (from TensorFlow Model Garden) to analyze real-time audio captured by the INMP441 microphone. The model compares incoming audio against the 521 sound classes it learned from AudioSet, allowing us to detect gunshot-related sounds (such as "Gunshot, gunfire", "Explosion", "Fireworks", "Machine gun", and "Firecracker") with configurable confidence thresholds.

---

## How It Works

| Component            | Description |
|----------------------|-------------|
| `audio_detect.py`    | Main detection script using YAMNet for real-time gunshot classification |
| `config.py`          | Configuration file for easy customization (detection threshold, GPIO pins, etc.) |
| INMP441 I2S Mic      | High-quality 24-bit audio capture via I2S interface |
| GPIO LED (Pin 26)    | Visual alert indicator (turns on for 5 seconds on detection) |
| Log Files            | Detection events recorded with timestamps for analysis |

---

## Hardware Setup

- Raspberry Pi (3B+, 4, or 5 recommended)
- **INMP441 24-bit I2S Omnidirectional Microphone** (primary) or USB Microphone (fallback)
- **WM8960 Audio HAT** (for external speaker output - plays alarm.wav sound)
- LED + 470 Ohm Resistor (on GPIO pin 26)
- Breadboard + Wires

### INMP441 I2S Microphone Wiring

Connect the INMP441 to your Raspberry Pi:

| INMP441 Pin | Raspberry Pi Pin | Description |
|-------------|------------------|-------------|
| VDD         | 3.3V (Pin 1)     | Power       |
| GND         | GND (Pin 6)      | Ground      |
| WS (LRCL)   | GPIO 19 (Pin 35) | Word Select |
| SCK (BCLK)  | GPIO 18 (Pin 12) | Bit Clock   |
| SD          | GPIO 20 (Pin 38) | Serial Data |

**Important GPIO Pin Assignments:**
- **I2S Microphone:** GPIO 18 (SCK), GPIO 19 (WS), GPIO 20 (SD)
- **LED Alert:** GPIO 26 (Pin 37) - *Changed from GPIO 21 to GPIO 26*

**Note:** After wiring, you may need to configure the I2S interface in Raspberry Pi OS. The system will attempt to auto-detect the I2S device, or you can configure it manually in `config.py`.

### WM8960 Audio HAT Setup (Speaker Output)

The WM8960 Audio HAT is used to connect an external low-power speaker for playing alarm sounds when gunshot detection occurs.

**Physical Setup:**
1. Insert the WM8960 Audio HAT onto the Raspberry Pi GPIO header
2. Connect your external speaker to the WM8960 Audio HAT
3. Power on the Raspberry Pi and ensure networking is enabled

**Driver Installation:**

The WM8960 Audio HAT requires a driver to be installed. Follow these steps:

```bash
# Clone the driver repository
git clone https://github.com/waveshare/WM8960-Audio-HAT

# Navigate to the driver directory
cd WM8960-Audio-HAT

# Install the driver (requires sudo)
sudo ./install.sh

# Reboot the Raspberry Pi
sudo reboot
```

**Verify Installation:**

After rebooting, verify the driver is installed correctly:

```bash
sudo dkms status
```

You should see output similar to:
```
wm8960-soundcard, 1.0, 4.14.71+, armv6l: installed
wm8960-soundcard, 1.0, 4.14.71-v7+, armv6l: installed
```

This confirms the WM8960 Audio HAT driver is successfully installed and ready to use.

**Note:** The alarm sound (`alarm.WAV`) will automatically play through the WM8960 Audio HAT when gunshot detection occurs (if `ENABLE_SOUND_ALERT = True` in `config.py`).

---

## Project Structure

```text
AI_shot_spotter/
├── yamnet_audio_classification/
│ ├── audio_detect.py      # Main detection script
│ ├── config.py            # Configuration file
│ └── yamnet_model/        # YAMNet model files
│     ├── assets/
│     │   └── yamnet_class_map.csv
│     └── saved_model.pb
│
├── assets/
│   └── alarm.WAV          # Alarm sound file (optional)
│
├── media/
│
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md             # This file
├── I2S_SETUP.md          # Detailed I2S microphone setup guide
└── GPIO_PIN_ASSIGNMENTS.md # Complete GPIO pin mapping and conflict prevention
```
---

## Installation
## Install Git
```bash
sudo apt install git -y
git --version
```
You should see something like:
git version 2.xx.x

1. **Clone the repository**

```bash
git clone https://github.com/the-diegolaredo/AI_shot_spotter.git
cd AI_shot_spotter
```

2. **Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install WM8960 Audio HAT Driver (if using external speaker)**
   
   If you're using the WM8960 Audio HAT for speaker output, install the driver:
   ```bash
   git clone https://github.com/waveshare/WM8960-Audio-HAT
   cd WM8960-Audio-HAT
   sudo ./install.sh
   sudo reboot
   ```
   
   After rebooting, verify with: `sudo dkms status`
   
   See the [Hardware Setup](#hardware-setup) section above for detailed instructions.

5. **Configure I2S Audio (if using INMP441)**
   
   The system will attempt to auto-detect I2S devices. If you need to manually configure:
   - Edit `yamnet_audio_classification/config.py`
   - Set `I2S_DEVICE_NAME` to your specific device name if needed
   - Or set `USE_I2S = False` to use USB microphone instead

---

## Running the System

### Sound Detection (YAMNet)
```bash
cd yamnet_audio_classification
python audio_detect.py
```

The system will:
- Auto-detect and configure audio input (I2S or USB microphone)
- Display available audio devices on startup
- Plot real-time confidence of top 5 sound classes (if enabled)
- Turn on LED for 5 seconds when **gunshot** is detected
- Log detections to `audio_detection_log.txt`

**Detection Target:**
- **Gunshot** sounds (configurable threshold: 30% confidence by default)

> **Note:** The system is currently configured to detect only gunshot sounds. You can modify `SUSPICIOUS_KEYWORDS` in `config.py` to detect additional sound classes if needed.

---

## Event Logging
Detection script log alerts to:

- `audio_detection_log.txt`
  
Each log includes a timestamp and detected event.

---

## Keeping the Codebase Updated

To keep your Raspberry Pi codebase synchronized with the latest changes from GitHub, follow these steps:

### Pull the Latest Changes

Navigate to the project directory and pull the latest updates:

```bash
cd ~/AI_shot_spotter
git pull origin main
```

This will download and merge any new changes, bug fixes, or improvements that have been pushed to the repository.

### After Updating

After pulling the latest changes:

1. **If dependencies were updated**, reinstall requirements:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **If configuration files changed**, review `yamnet_audio_classification/config.py` to see if any new settings were added or defaults changed.

3. **Restart the detection system** to use the updated code:
   ```bash
   cd yamnet_audio_classification
   python audio_detect.py
   ```

### Checking for Updates

You can check if there are updates available without pulling them:

```bash
cd ~/AI_shot_spotter
git fetch origin
git status
```

This will show you if your local branch is behind the remote repository.

---

## Customization

All configuration options are in `yamnet_audio_classification/config.py`:

### Detection Settings
```python
SUSPICIOUS_KEYWORDS = [
    "Gunshot, gunfire",
    "Explosion",
    "Fireworks", 
    "Machine gun",
    "Firecracker"
]

DETECTION_THRESHOLD = 0.2  # Minimum confidence (0.0-1.0) - lowered for better sensitivity
```

### Alert Settings
```python
ENABLE_LED_ALERT = True      # Enable/disable LED alerts
ENABLE_SOUND_ALERT = True    # Enable/disable sound alerts
LED_ALERT_DURATION = 5       # Duration in seconds to keep LED on after detection
ENABLE_PLOT = True           # Enable/disable real-time plotting
```

### Audio Settings
```python
USE_I2S = True               # Use I2S microphone (INMP441) or USB
I2S_DEVICE_NAME = None       # Auto-detect or specify device name
AUDIO_SAMPLE_RATE = 16000    # YAMNet requires 16kHz
AUDIO_CHANNELS = 2           # Stereo input (I2S requirement), converted to mono for YAMNet
```

### Hardware Settings
```python
LED_PIN = 26                 # GPIO pin for LED (GPIO 26, Pin 37)
```

---

## 📚 Documentation

For detailed setup and configuration guides, see:

- **[I2S Setup Guide](I2S_SETUP.md)** - Complete instructions for setting up the INMP441 I2S microphone, including hardware wiring, software configuration, and troubleshooting
- **[GPIO Pin Assignments](GPIO_PIN_ASSIGNMENTS.md)** - Comprehensive GPIO pin mapping, conflict prevention, and wiring diagrams

---

## 🔧 Troubleshooting

### Common Issues

**LED not turning on:**
- Verify LED is connected to GPIO 26 (Pin 37) with a 470Ω resistor
- Check `config.py` to ensure `ENABLE_LED_ALERT = True`
- Verify LED polarity (long leg to GPIO, short leg through resistor to GND)

**No audio input detected:**
- If using I2S: Follow the [I2S Setup Guide](I2S_SETUP.md) to verify I2S is enabled
- Check audio device with: `arecord -l` or `aplay -l`
- Try USB microphone fallback: Set `USE_I2S = False` in `config.py`

**GPIO conflicts:**
- Review [GPIO Pin Assignments](GPIO_PIN_ASSIGNMENTS.md) to ensure no pin conflicts
- Never use GPIO 18, 19, or 20 for other purposes when using I2S

**Detection not working:**
- Verify `SUSPICIOUS_KEYWORDS` includes gunshot-related terms in `config.py`
- Check if audio input is working: `arecord -D hw:1,0 -f S16_LE -r 16000 -c 2 -d 5 test.wav`
- Adjust `DETECTION_THRESHOLD` (default 0.2) if getting too many false positives/negatives
- Look for debug output showing real-time predictions every 2 seconds
- Check log file `audio_detection_log.txt` for detection history

For more detailed troubleshooting, see the [I2S Setup Guide](I2S_SETUP.md).

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Issues

If you encounter any issues or have suggestions, please [open an issue](https://github.com/the-diegolaredo/AI_shot_spotter/issues) on GitHub.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## Credits

- YAMNet from [Google Research](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet)

  Note: YAMNet model is loaded locally from the `yamnet_model/` directory and downloaded from https://www.kaggle.com/models/google/yamnet.
- Dataset labeling using [Roboflow](https://roboflow.com/)

---
