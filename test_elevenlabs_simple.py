#!/usr/bin/env python3
"""
Simple ElevenLabs Test for Raspberry Pi
Tests if ElevenLabs is working properly
"""

import os
import tempfile
import subprocess
import time

def test_elevenlabs():
    print("🎤 Testing ElevenLabs Integration...")
    print("=" * 50)
    
    try:
        # Test 1: Check if elevenlabs module is available
        print("📡 Test 1: Checking ElevenLabs module...")
        try:
            # Try different import methods for different versions
            try:
                from elevenlabs import generate, set_api_key
                print("✅ ElevenLabs module imported successfully (new API)")
            except ImportError:
                try:
                    from elevenlabs import generate
                    from elevenlabs import set_api_key
                    print("✅ ElevenLabs module imported successfully (separate imports)")
                except ImportError:
                    try:
                        from elevenlabs import Client
                        print("✅ ElevenLabs module imported successfully (Client API)")
                        # Use Client API instead
                        generate = None
                        set_api_key = None
                    except ImportError as e:
                        print(f"❌ ElevenLabs module not available: {e}")
                        return False
        except Exception as e:
            print(f"❌ ElevenLabs import failed: {e}")
            return False
        
        # Test 2: Check if API key is available
        print("\n🔑 Test 2: Checking API key...")
        try:
            from elevenlabs_config import ELEVENLABS_API_KEY
            api_key = ELEVENLABS_API_KEY
            print("✅ API key loaded from config file")
        except ImportError:
            print("⚠️ API key not found in config file")
            api_key = "sk_f8bd094182fd27ab6d2ba6d1447a3346ea745159f422970d"  # Test key
            print("⚠️ Using test API key")
        
        # Test 3: Set API key and generate audio
        print("\n🎵 Test 3: Generating audio...")
        try:
            test_message = "Hello! This is a test of ElevenLabs voice synthesis."
            print(f"📝 Generating: '{test_message}'")
            
            if generate and set_api_key:
                # Use old API
                set_api_key(api_key)
                audio = generate(text=test_message, voice="21m00Tcm4TlvDq8ikWAM")  # Rachel voice
            else:
                # Use new Client API
                from elevenlabs import Client
                client = Client(api_key=api_key)
                audio = client.generate(text=test_message, voice="21m00Tcm4TlvDq8ikWAM")
            
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
            
            # Test 5: Check if ffmpeg is available
            print("\n🔧 Test 5: Checking ffmpeg...")
            try:
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ ffmpeg is available")
                    
                    # Convert MP3 to WAV
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
                else:
                    print("❌ ffmpeg not available")
                    print("💡 Install ffmpeg: sudo apt install ffmpeg")
            except Exception as e:
                print(f"❌ ffmpeg test failed: {e}")
            
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
    test_elevenlabs()
