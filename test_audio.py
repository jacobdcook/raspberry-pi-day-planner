#!/usr/bin/env python3
"""
Simple Audio Test for Raspberry Pi
Tests if audio is working with pygame mixer
"""

import pygame
import time
import os

def test_audio():
    print("🔊 Testing Raspberry Pi Audio...")
    print("=" * 50)
    
    try:
        # Initialize pygame mixer
        print("📡 Initializing pygame mixer...")
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        print("✅ Pygame mixer initialized successfully")
        
        # Test 1: Generate a simple beep sound
        print("\n🎵 Test 1: Generating beep sound...")
        sample_rate = 44100
        duration = 1.0  # 1 second
        frequency = 440  # A4 note
        
        # Generate sine wave
        import numpy as np
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit integer
        tone = (tone * 32767).astype(np.int16)
        
        # Play the tone
        pygame.mixer.music.load(tone)
        pygame.mixer.music.play()
        print("🔊 Playing 440Hz tone for 1 second...")
        time.sleep(1.5)  # Wait for audio to finish
        
        # Test 2: Try to load and play a WAV file if it exists
        print("\n🎵 Test 2: Testing WAV file playback...")
        wav_files = [
            "sounds/alert.wav",
            "sounds/completion.wav", 
            "sounds/error.wav",
            "sounds/snooze.wav"
        ]
        
        for wav_file in wav_files:
            if os.path.exists(wav_file):
                try:
                    pygame.mixer.music.load(wav_file)
                    pygame.mixer.music.play()
                    print(f"🔊 Playing {wav_file}...")
                    time.sleep(2)  # Wait for audio to finish
                    break
                except Exception as e:
                    print(f"❌ Failed to play {wav_file}: {e}")
            else:
                print(f"⚠️ {wav_file} not found")
        
        # Test 3: System audio test
        print("\n🎵 Test 3: Testing system audio...")
        try:
            # Try using aplay (Linux audio player)
            import subprocess
            result = subprocess.run(['aplay', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ aplay is available")
                
                # Try to play a test tone with aplay
                print("🔊 Testing with aplay...")
                subprocess.run(['aplay', '-q', '-t', 'wav', '-f', 'S16_LE', '-r', '44100', '-c', '2'], 
                             input=tone.tobytes(), timeout=5)
                print("✅ aplay test completed")
            else:
                print("⚠️ aplay not available")
        except Exception as e:
            print(f"⚠️ aplay test failed: {e}")
        
        # Test 4: Check audio devices
        print("\n🔍 Test 4: Checking audio devices...")
        try:
            # Check ALSA devices
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 Available ALSA audio devices:")
                print(result.stdout)
            else:
                print("❌ Failed to list ALSA devices")
        except Exception as e:
            print(f"⚠️ Could not check ALSA devices: {e}")
        
        # Test 5: Check volume levels
        print("\n🔊 Test 5: Checking volume levels...")
        try:
            # Check current volume
            result = subprocess.run(['amixer', 'get', 'Master'], capture_output=True, text=True)
            if result.returncode == 0:
                print("📊 Current volume levels:")
                print(result.stdout)
            else:
                print("❌ Failed to get volume levels")
        except Exception as e:
            print(f"⚠️ Could not check volume: {e}")
        
        print("\n" + "=" * 50)
        print("🎵 Audio test completed!")
        print("📝 If you didn't hear anything:")
        print("   1. Check if speakers are connected and powered")
        print("   2. Check volume levels with: amixer get Master")
        print("   3. Test with: speaker-test -t wav -c 2")
        print("   4. Check HDMI audio: amixer set HDMI 100%")
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Run: sudo raspi-config")
        print("   2. Go to System Options > Audio")
        print("   3. Select 'Force 3.5mm jack' or 'Force HDMI'")
        print("   4. Reboot: sudo reboot")
    
    finally:
        pygame.mixer.quit()
        print("\n✅ Audio test finished")

if __name__ == "__main__":
    test_audio()
