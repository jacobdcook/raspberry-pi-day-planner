#!/usr/bin/env python3
"""
Remove ElevenLabs and use only espeak for reliable voice
"""

def fix_simulation():
    print("🔧 Removing ElevenLabs and using only espeak...")
    
    try:
        # Read the file
        with open('pi_simulation.py', 'r') as f:
            content = f.read()
        
        # Remove the ElevenLabs import entirely
        old_import = '''try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
    print("✅ ElevenLabs client imported successfully")
except ImportError as e:
    ELEVENLABS_AVAILABLE = False
    ElevenLabs = None
    print(f"⚠️ ElevenLabs not available: {e}")'''
        
        new_import = '''# ElevenLabs removed - using only espeak for reliable voice
ELEVENLABS_AVAILABLE = False
ElevenLabs = None
print("🤖 Using espeak robot voice only")'''
        
        # Replace the import section
        if old_import in content:
            content = content.replace(old_import, new_import)
            print("✅ Removed ElevenLabs import")
        else:
            print("⚠️ ElevenLabs import not found")
        
        # Replace the speak_message method to use only espeak
        old_speak_method = '''def speak_message(self, message):
        """Speak a message using available voice options."""
        print(f"🎤 Attempting to speak: '{message}'")
        
        # Try ElevenLabs first if available
        if ELEVENLABS_AVAILABLE and self.api_key:
            try:
                print(f"🔧 Trying ElevenLabs with voice: {self.voice_id}")
                client = ElevenLabs(api_key=self.api_key)
                audio_generator = client.text_to_speech.convert(
                    text=message,
                    voice_id=self.voice_id
                )
                audio = b''.join(audio_generator)
                
                if audio:
                    print(f"✅ ElevenLabs audio generated ({len(audio)} bytes)")
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                        temp_file.write(audio)
                        temp_file_path = temp_file.name
                    
                    # Try to convert MP3 to WAV using ffmpeg
                    try:
                        wav_path = temp_file_path.replace('.mp3', '.wav')
                        result = subprocess.run(['ffmpeg', '-i', temp_file_path, '-acodec', 'pcm_s16le', 
                                      '-ar', '44100', '-ac', '2', wav_path, '-y'], 
                                     capture_output=True, timeout=10)
                        
                        if result.returncode == 0 and os.path.exists(wav_path):
                            print(f"✅ MP3 to WAV conversion successful")
                            pygame.mixer.init()
                            pygame.mixer.music.load(wav_path)
                            pygame.mixer.music.play()
                            
                            # Clean up files after delay
                            def cleanup():
                                time.sleep(5)
                                try:
                                    os.unlink(temp_file_path)
                                    os.unlink(wav_path)
                                except:
                                    pass
                            
                            threading.Thread(target=cleanup, daemon=True).start()
                            print(f"🔊 ElevenLabs voice: {message}")
                            return
                    except Exception as e:
                        print(f"❌ ffmpeg conversion failed: {e}")
                    
                    # Clean up temp file
                    def cleanup():
                        time.sleep(5)
                        try:
                            os.unlink(temp_file_path)
                        except:
                            pass
                    threading.Thread(target=cleanup, daemon=True).start()
                    
            except Exception as e:
                print(f"❌ ElevenLabs failed: {e}")
        
        # Fallback to espeak (simple robot voice)
        try:
            print("🤖 Using espeak fallback voice...")
            # Use espeak to generate WAV file directly
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                wav_path = temp_file.name
            
            # Run espeak command
            result = subprocess.run([
                'espeak', '-w', wav_path, '-s', '150', '-p', '50', '-v', 'en-us', message
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(wav_path):
                print(f"✅ espeak audio generated")
                pygame.mixer.init()
                pygame.mixer.music.load(wav_path)
                pygame.mixer.music.play()
                
                # Clean up file after delay
                def cleanup():
                    time.sleep(5)
                    try:
                        os.unlink(wav_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
                print(f"🤖 Robot voice: {message}")
                return
            else:
                print(f"❌ espeak failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ espeak failed: {e}")
        
        # Final fallback to WAV sound
        print("⚠️ All voice options failed, using WAV fallback")
        self.play_sound("alert")'''
        
        new_speak_method = '''def speak_message(self, message):
        """Speak a message using espeak robot voice."""
        print(f"🎤 Speaking: '{message}'")
        
        try:
            print("🤖 Using espeak robot voice...")
            # Use espeak to generate WAV file directly
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                wav_path = temp_file.name
            
            # Run espeak command
            result = subprocess.run([
                'espeak', '-w', wav_path, '-s', '150', '-p', '50', '-v', 'en-us', message
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(wav_path):
                print(f"✅ espeak audio generated")
                pygame.mixer.init()
                pygame.mixer.music.load(wav_path)
                pygame.mixer.music.play()
                
                # Clean up file after delay
                def cleanup():
                    time.sleep(5)
                    try:
                        os.unlink(wav_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
                print(f"🤖 Robot voice: {message}")
                return
            else:
                print(f"❌ espeak failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ espeak failed: {e}")
        
        # Final fallback to WAV sound
        print("⚠️ espeak failed, using WAV fallback")
        self.play_sound("alert")'''
        
        # Replace the speak_message method
        if old_speak_method in content:
            content = content.replace(old_speak_method, new_speak_method)
            print("✅ Updated speak_message method to use only espeak")
        else:
            print("❌ Could not find speak_message method")
            return False
        
        # Also remove ElevenLabs setup in __init__
        old_setup = '''        # Setup ElevenLabs
        if ELEVENLABS_AVAILABLE:
            try:
                # Try to load from config file first
                try:
                    from elevenlabs_config import ELEVENLABS_API_KEY
                    self.api_key = ELEVENLABS_API_KEY
                    print("✅ ElevenLabs configured from config file")
                except ImportError:
                    # Use the key directly (for testing)
                    self.api_key = "sk_c326ebc4e6330a123b315239f3b69c850c675025793f3a92"
                    print("✅ ElevenLabs configured with test key")
            except Exception as e:
                print(f"⚠️ ElevenLabs setup failed: {e}")
        else:
            print("⚠️ ElevenLabs not available - voice features disabled")'''
        
        new_setup = '''        # ElevenLabs removed - using espeak only
        print("🤖 Using espeak robot voice (ElevenLabs removed)")'''
        
        if old_setup in content:
            content = content.replace(old_setup, new_setup)
            print("✅ Removed ElevenLabs setup")
        
        # Write the updated content
        with open('pi_simulation.py', 'w') as f:
            f.write(content)
        
        print("✅ pi_simulation.py updated successfully!")
        print("🤖 Now uses only espeak robot voice - no lag, no ElevenLabs!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix simulation: {e}")
        return False

if __name__ == "__main__":
    fix_simulation()
