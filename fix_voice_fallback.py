#!/usr/bin/env python3
"""
Add simple voice fallback using espeak
"""

def fix_simulation():
    print("🔧 Adding voice fallback to pi_simulation.py...")
    
    try:
        # Read the file
        with open('pi_simulation.py', 'r') as f:
            content = f.read()
        
        # Add espeak import at the top
        old_imports = '''import pygame
import sys
import os
import json
import time
import yaml
import sqlite3
import threading
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from modules.progress_db import ProgressDatabase
from modules.backlog_manager import BacklogManager
from modules.adaptive_time import AdaptiveTimeManager'''
        
        new_imports = '''import pygame
import sys
import os
import json
import time
import yaml
import sqlite3
import threading
import tempfile
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from modules.progress_db import ProgressDatabase
from modules.backlog_manager import BacklogManager
from modules.adaptive_time import AdaptiveTimeManager'''
        
        if old_imports in content:
            content = content.replace(old_imports, new_imports)
            print("✅ Added subprocess import")
        
        # Replace the speak_message method with a simpler version that has fallback
        old_speak_method = '''def speak_message(self, message):
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
        
        new_speak_method = '''def speak_message(self, message):
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
        
        # Replace the speak_message method
        if old_speak_method in content:
            content = content.replace(old_speak_method, new_speak_method)
            print("✅ Updated speak_message method with fallback")
        else:
            print("❌ Could not find speak_message method")
            return False
        
        # Write the updated content
        with open('pi_simulation.py', 'w') as f:
            f.write(content)
        
        print("✅ pi_simulation.py updated successfully!")
        print("🤖 Now has espeak fallback + ElevenLabs option")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix simulation: {e}")
        return False

if __name__ == "__main__":
    fix_simulation()
