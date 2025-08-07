#!/usr/bin/env python3
"""
Fix for pi_simulation.py to handle ElevenLabs generator response
"""

def fix_simulation():
    print("🔧 Fixing pi_simulation.py for ElevenLabs generator...")
    
    try:
        # Read the file
        with open('pi_simulation.py', 'r') as f:
            content = f.read()
        
        # Find and replace the import section - look for the old import pattern
        old_import_pattern = '''try:
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
        if old_import_pattern in content:
            content = content.replace(old_import_pattern, new_import)
            print("✅ Updated import section")
        else:
            print("⚠️ Old import pattern not found, checking for new pattern...")
            
            # Check if it's already using the new import
            if "from elevenlabs import ElevenLabs" in content:
                print("✅ Import section already updated")
            else:
                print("❌ Could not find import section to update")
        
        # Fix the speak_message method to handle generator
        old_speak = '''            # Use client API
            client = ElevenLabs(api_key=self.api_key)
            audio = client.text_to_speech.convert(
                text=message,
                voice_id=self.voice_id
            )'''
        
        new_speak = '''            # Use client API
            client = ElevenLabs(api_key=self.api_key)
            audio_generator = client.text_to_speech.convert(
                text=message,
                voice_id=self.voice_id
            )
            # Convert generator to bytes
            audio = b''.join(audio_generator)'''
        
        if old_speak in content:
            content = content.replace(old_speak, new_speak)
            print("✅ Updated speak_message method to handle generator")
        else:
            print("⚠️ speak_message method not found or already updated")
        
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
