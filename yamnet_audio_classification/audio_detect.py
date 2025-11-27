"""
Real-time audio detection system using YAMNet for sound classification.
Supports INMP441 I2S microphone and USB microphones.
"""
import os
import sys
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
import matplotlib.pyplot as plt
import pygame
import RPi.GPIO as GPIO
from datetime import datetime
import threading
import config

# Try to import sounddevice for I2S support, fallback to pyaudio
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    import pyaudio

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(config.LED_PIN, GPIO.OUT)
GPIO.output(config.LED_PIN, GPIO.LOW)

# Load YAMNet Model
print("Loading YAMNet model...")
try:
    model = hub.load(config.YAMNET_MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Make sure the yamnet_model directory exists and contains the model files.")
    sys.exit(1)

# Load Class Labels from local file
print("Loading class labels...")
class_names = []
try:
    if os.path.exists(config.CLASS_MAP_PATH):
        with open(config.CLASS_MAP_PATH, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_names.append(row['display_name'])
        print(f"Loaded {len(class_names)} class labels from local file.")
    else:
        # Fallback to downloading if local file doesn't exist
        print("Local class map not found, downloading...")
        labels_path = tf.keras.utils.get_file(
            'yamnet_class_map.csv',
            'https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv'
        )
        with open(labels_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_names.append(row['display_name'])
        print(f"Downloaded and loaded {len(class_names)} class labels.")
except Exception as e:
    print(f"Error loading class labels: {e}")
    sys.exit(1)

# Audio Input Setup
print("Setting up audio input...")
audio_stream = None
p = None
device_id = None
USE_SOUNDDEVICE = False

if config.USE_I2S and SOUNDDEVICE_AVAILABLE:
    # Use sounddevice for I2S microphone (INMP441)
    try:
        # List available audio devices
        devices = sd.query_devices()
        print("\nAvailable audio devices:")
        for i, device in enumerate(devices):
            print(f"  {i}: {device['name']} ({device['max_input_channels']} input channels)")
        
        # Find I2S device if specified
        if config.I2S_DEVICE_NAME:
            for i, device in enumerate(devices):
                if config.I2S_DEVICE_NAME.lower() in device['name'].lower():
                    device_id = i
                    print(f"\nUsing I2S device: {device['name']} (index {i})")
                    break
        
        if device_id is None:
            # Use default input device
            device_id = sd.default.device[0]
            print(f"\nUsing default input device: {devices[device_id]['name']} (index {device_id})")
        
        # Create sounddevice stream
        def audio_callback(indata, frames, time, status):
            """Callback for audio input"""
            if status:
                print(f"Audio status: {status}")
            # Store audio data in a queue or process directly
            # For now, we'll use blocking read instead
        
        print(f"Audio configured: {config.AUDIO_SAMPLE_RATE}Hz, {config.AUDIO_CHANNELS} channel(s)")
        print(f"Note: I2S audio will be converted from stereo to mono for YAMNet processing")
        USE_SOUNDDEVICE = True
        
    except Exception as e:
        print(f"Error setting up sounddevice: {e}")
        print("Falling back to PyAudio...")
        USE_SOUNDDEVICE = False
        SOUNDDEVICE_AVAILABLE = False
        device_id = None

if not USE_SOUNDDEVICE:
    # Use PyAudio for USB microphone
    try:
        p = pyaudio.PyAudio()
        print("\nAvailable PyAudio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  {i}: {info['name']} ({info['maxInputChannels']} input channels)")
        
        audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=config.AUDIO_CHANNELS,
            rate=config.AUDIO_SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.AUDIO_CHUNK_SIZE
        )
        print(f"Audio configured: {config.AUDIO_SAMPLE_RATE}Hz, {config.AUDIO_CHANNELS} channel(s)")
        if config.AUDIO_CHANNELS == 2:
            print(f"Note: USB audio will be converted from stereo to mono for YAMNet processing")
    except Exception as e:
        print(f"Error setting up PyAudio: {e}")
        sys.exit(1)

# Matplotlib Setup
if config.ENABLE_PLOT:
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 1)

# Sound Setup
alarm_sound = None
alarm_playing = False
if config.ENABLE_SOUND_ALERT:
    try:
        pygame.mixer.init()
        if os.path.exists(config.ALARM_SOUND_PATH):
            alarm_sound = pygame.mixer.Sound(config.ALARM_SOUND_PATH)
            print(f"Alarm sound loaded: {config.ALARM_SOUND_PATH}")
        else:
            print(f"Warning: Alarm sound file not found at {config.ALARM_SOUND_PATH}")
            print("Sound alerts will be disabled.")
            config.ENABLE_SOUND_ALERT = False
    except Exception as e:
        print(f"Error loading alarm sound: {e}")
        config.ENABLE_SOUND_ALERT = False

# Logging Setup
def log_event(event_type, confidence):
    """Log detection event to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Detected: {event_type} (confidence: {confidence:.2%})\n"
    
    try:
        with open(config.LOG_FILE, "a") as log:
            log.write(log_entry)
        print(f"✓ Logged: {event_type}")
    except Exception as e:
        print(f"✗ Failed to log event: {e}")

# LED Control
led_timer = None

# Cleanup Function
def cleanup():
    """Clean up resources and GPIO before exiting"""
    print("Cleaning up...")
    try:
        GPIO.output(config.LED_PIN, GPIO.LOW)
        GPIO.cleanup()
    except:
        pass
    
    try:
        if 'audio_stream' in globals() and audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
    except:
        pass
    
    try:
        if 'p' in globals() and p:
            p.terminate()
    except:
        pass
    
    try:
        if config.ENABLE_PLOT:
            plt.close()
    except:
        pass
    
    try:
        if config.ENABLE_SOUND_ALERT:
            pygame.mixer.quit()
    except:
        pass
    
    print("Cleanup complete. Goodbye!")

# Detection Loop
print("\n" + "="*60)
print("Starting audio detection...")
print("Press Ctrl+C to stop.")
print("="*60 + "\n")

try:
    while True:
        # Read audio data
        if USE_SOUNDDEVICE:
            # Read audio using sounddevice (I2S)
            audio_data = sd.rec(
                frames=config.AUDIO_CHUNK_SIZE,
                samplerate=config.AUDIO_SAMPLE_RATE,
                channels=config.AUDIO_CHANNELS,
                dtype='int16',
                device=device_id
            )
            sd.wait()  # Wait until recording is finished
            
            # Convert stereo to mono for YAMNet (YAMNet expects mono input)
            if config.AUDIO_CHANNELS == 2:
                # Take the mean of both channels to convert stereo to mono
                waveform = np.mean(audio_data, axis=1).astype(np.float32) / 32768.0
            else:
                # Already mono
                waveform = audio_data.flatten().astype(np.float32) / 32768.0
        else:
            # Read audio using PyAudio (USB)
            data = audio_stream.read(config.AUDIO_CHUNK_SIZE, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)
            
            # Handle stereo to mono conversion for USB microphones too
            if config.AUDIO_CHANNELS == 2:
                # Reshape and convert stereo to mono
                audio_array = audio_array.reshape(-1, 2)
                waveform = np.mean(audio_array, axis=1).astype(np.float32) / 32768.0
            else:
                # Already mono
                waveform = audio_array.astype(np.float32) / 32768.0
        
        # Run inference
        try:
            scores, embeddings, spectrogram = model(waveform)
        except Exception as e:
            print(f"Error during inference: {e}")
            continue

        # Get top 5 predictions
        mean_scores = np.mean(scores, axis=0)
        top5_idx = np.argsort(mean_scores)[-5:][::-1]
        top5_scores = mean_scores[top5_idx]
        top5_labels = [class_names[i] for i in top5_idx]
        
        # Debug output: Print top predictions
        print(f"\n--- Audio Detection Debug ---")
        print(f"Audio input shape: {waveform.shape}, Max amplitude: {np.max(np.abs(waveform)):.3f}")
        print(f"Top 5 predictions:")
        for i, (label, score) in enumerate(zip(top5_labels, top5_scores)):
            marker = "🎯" if any(keyword.lower() in label.lower() for keyword in config.SUSPICIOUS_KEYWORDS) else "  "
            print(f"  {marker} {i+1}. {label}: {score:.3f} ({score:.1%})")
        print(f"Detection threshold: {config.DETECTION_THRESHOLD} ({config.DETECTION_THRESHOLD:.1%})")
        
        # Check for detection in debug output
        detection_found = False
        for label, score in zip(top5_labels, top5_scores):
            for keyword in config.SUSPICIOUS_KEYWORDS:
                if keyword.lower() in label.lower() and score > config.DETECTION_THRESHOLD:
                    detection_found = True
                    print(f"🚨 DETECTION FOUND! {label} - {score:.1%} confidence (keyword: {keyword})")
                    break
            if detection_found:
                break
        
        if not detection_found:
            print("   No target sounds detected in this sample")
        
        print("-" * 50)

        # Update Plot
        if config.ENABLE_PLOT:
            try:
                ax.clear()
                ax.barh(top5_labels, top5_scores)
                ax.set_xlim(0, 1)
                ax.set_xlabel("Confidence")
                ax.set_title("Top 5 Sound Classifications")
                plt.pause(0.01)
            except Exception as e:
                print(f"Plotting error: {e}")

        # Detection Logic
        detected_something = False
        detected_type = None
        detected_confidence = 0.0

        # Debug: Print what we're checking
        print(f"DEBUG: Checking keywords: {config.SUSPICIOUS_KEYWORDS}")
        print(f"DEBUG: Threshold: {config.DETECTION_THRESHOLD}")
        
        for label, score in zip(top5_labels, top5_scores):
            print(f"DEBUG: Checking '{label}' with score {score:.3f}")
            for keyword in config.SUSPICIOUS_KEYWORDS:
                if keyword.lower() in label.lower():
                    print(f"DEBUG: Found keyword '{keyword}' in '{label}'")
                    if score > config.DETECTION_THRESHOLD:
                        print(f"DEBUG: Score {score:.3f} > threshold {config.DETECTION_THRESHOLD} - DETECTION!")
                        detected_something = True
                        if score > detected_confidence:
                            detected_type = label
                            detected_confidence = score
                        break
                    else:
                        print(f"DEBUG: Score {score:.3f} <= threshold {config.DETECTION_THRESHOLD} - no detection")
            if detected_something:
                break

        # Trigger alerts
        if detected_something:
            # LED Alert - Turn on for 5 seconds
            if config.ENABLE_LED_ALERT:
                GPIO.output(config.LED_PIN, GPIO.HIGH)
                # Start timer to turn off LED after 5 seconds
                if led_timer is None or not led_timer.is_alive():
                    led_timer = threading.Timer(
                        config.LED_ALERT_DURATION,
                        lambda: GPIO.output(config.LED_PIN, GPIO.LOW)
                    )
                    led_timer.start()
            
            # Sound Alert
            if config.ENABLE_SOUND_ALERT and alarm_sound and not alarm_playing:
                try:
                    alarm_sound.play()
                    alarm_playing = True
                except Exception as e:
                    print(f"Error playing alarm: {e}")
            
            # Logging
            log_event(detected_type, detected_confidence)
            
            # Print detection info
            print(f"⚠ ALERT: {detected_type} detected (confidence: {detected_confidence:.2%})")
            
            # Pause detection and show user menu
            print("\n" + "="*60)
            print("🚨 DETECTION TRIGGERED - SYSTEM PAUSED")
            print("="*60)
            
            while True:
                print("\nChoose an option:")
                print("1. Continue monitoring")
                print("2. Exit program")
                
                try:
                    choice = input("\nEnter your choice (1 or 2): ").strip()
                    
                    if choice == "1":
                        print("\n" + "="*60)
                        print("🔄 Resuming audio detection...")
                        print("Press Ctrl+C to stop.")
                        print("="*60)
                        break
                    elif choice == "2":
                        print("\n👋 Exiting program...")
                        cleanup()
                        sys.exit(0)
                    else:
                        print("❌ Invalid choice. Please enter 1 or 2.")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Exiting program...")
                    cleanup()
                    sys.exit(0)
                except Exception as e:
                    print(f"❌ Input error: {e}. Please try again.")
        else:
            # Turn off sound alert if no detection
            if config.ENABLE_SOUND_ALERT and alarm_playing:
                try:
                    alarm_sound.stop()
                    alarm_playing = False
                except Exception as e:
                    print(f"Error stopping alarm: {e}")

except KeyboardInterrupt:
    print("\n\nStopping detection...")

except Exception as e:
    print(f"\n\nUnexpected error: {e}")
    import traceback
    traceback.print_exc()

finally:
    cleanup()
