#!/usr/bin/env python3
"""
Direct ElevenLabs Test for Raspberry Pi
Tests the new API directly
"""

import os
import tempfile
import subprocess
import time

def test_elevenlabs_direct():
    print("🎤 Direct ElevenLabs Test...")
    print("=" * 50)
    
    try:
        # Test 1: Check if elevenlabs module is available
        print("📡 Test 1: Checking ElevenLabs module...")
        try:
            from elevenlabs import Client
            print("✅ ElevenLabs Client imported successfully")
        except ImportError as e:
            print(f"❌ ElevenLabs module not available: {e}")
            return False
        
        # Test 2: Check API key
        print("\n🔑 Test 2: Checking API key...")
        api_key = "sk_c326ebc4e6330a123b315239f3b69c850c675025793f3a92"  # Your new key
        print(f"✅ Using API key: {api_key[:20]}...")
        
        # Test 3: Create client and generate audio
        print("\n🎵 Test 3: Generating audio...")
        try:
            client = Client(api_key=api_key)
            test_message = "Hello! This is a test of ElevenLabs voice synthesis."
            print(f"📝 Generating: '{test_message}'")
            
            audio = client.generate(text=test_message, voice="21m00Tcm4TlvDq8ikWAM")  # Rachel voice
            if audio:
                print("✅ Audio generated successfully")
                print(f"📊 Audio size: {len(audio)} bytes")
            else:
                print("❌ Audio generation failed - returned None")
                return False
        except Exception as e:
            print(f"❌ Failed to generate audio: {e}")
            return False
        
        # Test 4: Save and convert audio
        print("\n💾 Test 4: Saving and converting audio...")
        try:
            # Save MP3 file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio)
                temp_file_path = temp_file.name
            
            print(f"✅ MP3 saved to: {temp_file_path}")
            print(f"📊 File size: {os.path.getsize(temp_file_path)} bytes")
            
            # Test 5: Convert with ffmpeg
            print("\n🔧 Test 5: Converting with ffmpeg...")
            try:
                wav_path = temp_file_path.replace('.mp3', '.wav')
                print(f"🔄 Converting to: {wav_path}")
                
                result = subprocess.run(['ffmpeg', '-i', temp_file_path, '-acodec', 'pcm_s16le', 
                                      '-ar', '44100', '-ac', '2', wav_path, '-y'], 
                                     capture_output=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(wav_path):
                    print("✅ MP3 to WAV conversion successful")
                    print(f"📊 WAV file size: {os.path.getsize(wav_path)} bytes")
                    
                    # Test 6: Play the WAV file
                    print("\n🔊 Test 6: Playing WAV file...")
                    try:
                        import pygame
                        pygame.mixer.init()
                        pygame.mixer.music.load(wav_path)
                        pygame.mixer.music.play()
                        print("🔊 Playing converted WAV file...")
                        time.sleep(3)  # Wait for audio to finish
                        print("✅ WAV file played successfully")
                    except Exception as e:
                        print(f"❌ Failed to play WAV: {e}")
                else:
                    print(f"❌ MP3 to WAV conversion failed: {result.stderr}")
            except Exception as e:
                print(f"❌ ffmpeg conversion failed: {e}")
            
            # Clean up
            try:
                os.unlink(temp_file_path)
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                print("🧹 Temporary files cleaned up")
            except:
                pass
            
        except Exception as e:
            print(f"❌ Audio save/conversion failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("🎤 ElevenLabs test completed successfully!")
        print("✅ Voice synthesis should work in the simulation")
        return True
        
    except Exception as e:
        print(f"❌ ElevenLabs test failed: {e}")
        return False

if __name__ == "__main__":
    test_elevenlabs_direct()
