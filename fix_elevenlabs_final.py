#!/usr/bin/env python3
"""
Final fix for pi_simulation.py to use ElevenLabs client API
"""

def fix_simulation():
    print("🔧 Fixing pi_simulation.py for ElevenLabs client API...")
    
    try:
        # Read the file
        with open('pi_simulation.py', 'r') as f:
            content = f.read()
        
        # Find and replace the import section
        old_import = '''try:
    from elevenlabs import generate, set_api_key
    ELEVENLABS_AVAILABLE = True
    print("✅ ElevenLabs imported successfully")
except ImportError as e:
    ELEVENLABS_AVAILABLE = False
    def generate(*args, **kwargs):
        return None
    def set_api_key(*args, **kwargs):
        pass
    print(f"⚠️ ElevenLabs not available: {e}")'''
        
        new_import = '''try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
    print("✅ ElevenLabs client imported successfully")
except ImportError as e:
    ELEVENLABS_AVAILABLE = False
    ElevenLabs = None
    print(f"⚠️ ElevenLabs not available: {e}")'''
        
        # Replace the import section
        if old_import in content:
            content = content.replace(old_import, new_import)
            print("✅ Updated import section")
        else:
            print("⚠️ Import section not found")
        
        # Fix the speak_message method to use client API
        old_speak = '''            # Use old API
            audio = generate(text=message, voice=self.voice_id)'''
        
        new_speak = '''            # Use client API
            client = ElevenLabs(api_key=self.api_key)
            audio = client.text_to_speech.convert(
                text=message,
                voice_id=self.voice_id
            )'''
        
        if old_speak in content:
            content = content.replace(old_speak, new_speak)
            print("✅ Updated speak_message method")
        
        # Also fix the setup section in __init__
        old_setup = '''        # Setup ElevenLabs
        if ELEVENLABS_AVAILABLE:
            try:
                # Try to load from config file first
                try:
                    from elevenlabs_config import ELEVENLABS_API_KEY
                    set_api_key(ELEVENLABS_API_KEY)
                    print("✅ ElevenLabs configured from config file")
                except ImportError:
                    # Use the key directly (for testing)
                    set_api_key("sk_f8bd094182fd27ab6d2ba6d1447a3346ea745159f422970d")
                    print("✅ ElevenLabs configured with test key")
            except Exception as e:
                print(f"⚠️ ElevenLabs setup failed: {e}")
        else:
            print("⚠️ ElevenLabs not available - voice features disabled")'''
        
        new_setup = '''        # Setup ElevenLabs
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
        
        if old_setup in content:
            content = content.replace(old_setup, new_setup)
            print("✅ Updated ElevenLabs setup")
        
        # Write the updated content
        with open('pi_simulation.py', 'w') as f:
            f.write(content)
        
        print("✅ pi_simulation.py updated successfully!")
        print("🎤 Now using ElevenLabs client API")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix simulation: {e}")
        return False

if __name__ == "__main__":
    fix_simulation()
