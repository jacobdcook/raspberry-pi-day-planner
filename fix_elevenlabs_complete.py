#!/usr/bin/env python3
"""
Complete fix for pi_simulation.py ElevenLabs integration
"""

def fix_simulation():
    print("🔧 Complete fix for pi_simulation.py...")
    
    try:
        # Read the file
        with open('pi_simulation.py', 'r') as f:
            content = f.read()
        
        # Replace the entire import section (lines 46-76)
        old_import_section = '''try:
    # Try different import methods for different versions
    try:
        from elevenlabs import generate, set_api_key
        ELEVENLABS_AVAILABLE = True
        print("✅ ElevenLabs imported (new API)")
    except ImportError:
        try:
            from elevenlabs import generate
            from elevenlabs import set_api_key
            ELEVENLABS_AVAILABLE = True
            print("✅ ElevenLabs imported (separate imports)")
        except ImportError:
            try:
                from elevenlabs import Client
                ELEVENLABS_AVAILABLE = True
                generate = None
                set_api_key = None
                print("✅ ElevenLabs imported (Client API)")
            except ImportError:
                # Fallback if elevenlabs is not available
                ELEVENLABS_AVAILABLE = False
                def generate(*args, **kwargs):
                    return None
                def set_api_key(*args, **kwargs):
                    pass
                print("⚠️ ElevenLabs not available")
except Exception as e:
    ELEVENLABS_AVAILABLE = False
    def generate(*args, **kwargs):
        return None
    def set_api_key(*args, **kwargs):
        pass
    print(f"⚠️ ElevenLabs import failed: {e}")'''
        
        new_import_section = '''try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
    print("✅ ElevenLabs client imported successfully")
except ImportError as e:
    ELEVENLABS_AVAILABLE = False
    ElevenLabs = None
    print(f"⚠️ ElevenLabs not available: {e}")'''
        
        # Replace the import section
        if old_import_section in content:
            content = content.replace(old_import_section, new_import_section)
            print("✅ Updated import section")
        else:
            print("❌ Could not find old import section")
            return False
        
        # Replace the speak_message method
        old_speak_method = '''def speak_message(self, message):
        """Speak a message using ElevenLabs voice."""
        print(f"🎤 Attempting to speak: '{message}'")
        
        if not self.voice_engine or not self.api_key:
            print("⚠️ Voice engine or API key not available, using WAV fallback")
            self.play_sound("alert")
            return
        
        try:
            # Generate audio
            print(f"🔧 Generating audio with voice: {self.voice_id}")
            
            if generate and set_api_key:
                # Use old API
                audio = generate(text=message, voice=self.voice_id)
            else:
                # Use new Client API
                from elevenlabs import Client
                client = Client(api_key=self.api_key)
                audio = client.generate(text=message, voice=self.voice_id)
            
            if audio:
                print(f"✅ Audio generated successfully ({len(audio)} bytes)")
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(audio)
                    temp_file_path = temp_file.name
                
                # Try to convert MP3 to WAV using ffmpeg if available
                try:
                    import subprocess
                    print("🔄 Attempting MP3 to WAV conversion with ffmpeg...")
                    wav_path = temp_file_path.replace('.mp3', '.wav')
                    result = subprocess.run(['ffmpeg', '-i', temp_file_path, '-acodec', 'pcm_s16le', 
                                  '-ar', '44100', '-ac', '2', wav_path, '-y'], 
                                 capture_output=True, timeout=10)
                    
                    if result.returncode == 0 and os.path.exists(wav_path):
                        print(f"✅ MP3 to WAV conversion successful")
                        # Play the converted WAV file
                        pygame.mixer.init()
                        pygame.mixer.music.load(wav_path)
                        pygame.mixer.music.play()
                        
                        # Clean up both files after a delay
                        def cleanup():
                            import time
                            time.sleep(5)  # Wait for audio to finish
                            try:
                                os.unlink(temp_file_path)
                                os.unlink(wav_path)
                            except:
                                pass
                        
                        threading.Thread(target=cleanup, daemon=True).start()
                        print(f"🔊 Voice: {message}")
                        return
                    else:
                        print(f"❌ MP3 to WAV conversion failed: {result.stderr}")
                except Exception as e:
                    print(f"❌ ffmpeg conversion failed: {e}")
                
                # If conversion failed, fallback to WAV sound
                print(f"⚠️ Could not convert MP3 to WAV, using fallback sound")
                self.play_sound("alert")
                
                # Clean up temp file
                def cleanup():
                    import time
                    time.sleep(5)
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
            else:
                print(f"❌ Failed to generate audio for: {message}")
                self.play_sound("alert")
        except Exception as e:
            print(f"❌ Error speaking message: {e}")
            self.play_sound("alert")'''
        
        new_speak_method = '''def speak_message(self, message):
        """Speak a message using ElevenLabs voice."""
        print(f"🎤 Attempting to speak: '{message}'")
        
        if not ELEVENLABS_AVAILABLE or not self.api_key:
            print("⚠️ ElevenLabs not available, using WAV fallback")
            self.play_sound("alert")
            return
        
        try:
            # Generate audio using client API
            print(f"🔧 Generating audio with voice: {self.voice_id}")
            
            client = ElevenLabs(api_key=self.api_key)
            audio_generator = client.text_to_speech.convert(
                text=message,
                voice_id=self.voice_id
            )
            # Convert generator to bytes
            audio = b''.join(audio_generator)
            
            if audio:
                print(f"✅ Audio generated successfully ({len(audio)} bytes)")
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(audio)
                    temp_file_path = temp_file.name
                
                # Try to convert MP3 to WAV using ffmpeg if available
                try:
                    import subprocess
                    print("🔄 Attempting MP3 to WAV conversion with ffmpeg...")
                    wav_path = temp_file_path.replace('.mp3', '.wav')
                    result = subprocess.run(['ffmpeg', '-i', temp_file_path, '-acodec', 'pcm_s16le', 
                                  '-ar', '44100', '-ac', '2', wav_path, '-y'], 
                                 capture_output=True, timeout=10)
                    
                    if result.returncode == 0 and os.path.exists(wav_path):
                        print(f"✅ MP3 to WAV conversion successful")
                        # Play the converted WAV file
                        pygame.mixer.init()
                        pygame.mixer.music.load(wav_path)
                        pygame.mixer.music.play()
                        
                        # Clean up both files after a delay
                        def cleanup():
                            import time
                            time.sleep(5)  # Wait for audio to finish
                            try:
                                os.unlink(temp_file_path)
                                os.unlink(wav_path)
                            except:
                                pass
                        
                        threading.Thread(target=cleanup, daemon=True).start()
                        print(f"🔊 Voice: {message}")
                        return
                    else:
                        print(f"❌ MP3 to WAV conversion failed: {result.stderr}")
                except Exception as e:
                    print(f"❌ ffmpeg conversion failed: {e}")
                
                # If conversion failed, fallback to WAV sound
                print(f"⚠️ Could not convert MP3 to WAV, using fallback sound")
                self.play_sound("alert")
                
                # Clean up temp file
                def cleanup():
                    import time
                    time.sleep(5)
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
            else:
                print(f"❌ Failed to generate audio for: {message}")
                self.play_sound("alert")
        except Exception as e:
            print(f"❌ Error speaking message: {e}")
            self.play_sound("alert")'''
        
        # Replace the speak_message method
        if old_speak_method in content:
            content = content.replace(old_speak_method, new_speak_method)
            print("✅ Updated speak_message method")
        else:
            print("❌ Could not find speak_message method")
            return False
        
        # Write the updated content
        with open('pi_simulation.py', 'w') as f:
            f.write(content)
        
        print("✅ pi_simulation.py updated successfully!")
        print("🎤 Now using ElevenLabs client API with generator handling")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix simulation: {e}")
        return False

if __name__ == "__main__":
    fix_simulation()
