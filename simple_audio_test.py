#!/usr/bin/env python3
"""
Simple Audio Test for Raspberry Pi (No numpy required)
Tests basic audio functionality
"""

import pygame
import time
import os
import subprocess

def simple_audio_test():
    print("🔊 Simple Audio Test for Raspberry Pi")
    print("=" * 50)
    
    try:
        # Initialize pygame mixer
        print("📡 Initializing pygame mixer...")
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        print("✅ Pygame mixer initialized successfully")
        
        # Test 1: Try to play existing WAV files
        print("\n🎵 Test 1: Testing WAV file playback...")
        wav_files = [
            "sounds/alert.wav",
            "sounds/completion.wav", 
            "sounds/error.wav",
            "sounds/snooze.wav"
        ]
        
        found_wav = False
        for wav_file in wav_files:
            if os.path.exists(wav_file):
                try:
                    pygame.mixer.music.load(wav_file)
                    pygame.mixer.music.play()
                    print(f"🔊 Playing {wav_file}...")
                    found_wav = True
                    time.sleep(2)  # Wait for audio to finish
                    break
                except Exception as e:
                    print(f"❌ Failed to play {wav_file}: {e}")
            else:
                print(f"⚠️ {wav_file} not found")
        
        if not found_wav:
            print("⚠️ No WAV files found to test")
        
        # Test 2: System audio test with speaker-test
        print("\n🎵 Test 2: Testing system audio...")
        try:
            print("🔊 Running speaker-test (should hear pink noise)...")
            result = subprocess.run(['speaker-test', '-t', 'wav', '-c', '2', '-l', '1'], 
                                  timeout=10, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ speaker-test completed successfully")
            else:
                print(f"⚠️ speaker-test failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("✅ speaker-test ran (timeout is normal)")
        except Exception as e:
            print(f"⚠️ speaker-test failed: {e}")
        
        # Test 3: Check audio devices
        print("\n🔍 Test 3: Checking audio devices...")
        try:
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 Available ALSA audio devices:")
                print(result.stdout)
            else:
                print("❌ Failed to list ALSA devices")
        except Exception as e:
            print(f"⚠️ Could not check ALSA devices: {e}")
        
        # Test 4: Check volume levels
        print("\n🔊 Test 4: Checking volume levels...")
        try:
            result = subprocess.run(['amixer', 'get', 'Master'], capture_output=True, text=True)
            if result.returncode == 0:
                print("📊 Current volume levels:")
                print(result.stdout)
            else:
                print("❌ Failed to get volume levels")
        except Exception as e:
            print(f"⚠️ Could not check volume: {e}")
        
        # Test 5: Quick volume test
        print("\n🔊 Test 5: Quick volume test...")
        try:
            # Set volume to 50% and test
            subprocess.run(['amixer', 'set', 'Master', '50%'], capture_output=True)
            print("✅ Volume set to 50%")
            
            # Test with aplay if available
            result = subprocess.run(['aplay', '--version'], capture_output=True)
            if result.returncode == 0:
                print("🔊 Testing with aplay...")
                # Create a simple test tone using sox if available
                try:
                    subprocess.run(['sox', '-n', '-r', '44100', '-c', '2', 'test_tone.wav', 
                                  'synth', '1', 'sine', '440'], capture_output=True)
                    if os.path.exists('test_tone.wav'):
                        subprocess.run(['aplay', 'test_tone.wav'], capture_output=True)
                        os.remove('test_tone.wav')
                        print("✅ aplay test completed")
                except:
                    print("⚠️ sox not available for tone generation")
        except Exception as e:
            print(f"⚠️ Volume test failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎵 Audio test completed!")
        print("📝 If you didn't hear anything:")
        print("   1. Check if speakers are connected and powered")
        print("   2. Run: amixer set Master 100%")
        print("   3. Run: speaker-test -t wav -c 2")
        print("   4. Check HDMI audio: amixer set HDMI 100%")
        print("   5. Run: sudo raspi-config > System Options > Audio")
        
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
    simple_audio_test()
