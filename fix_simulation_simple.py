#!/usr/bin/env python3
"""
Simple fix for pi_simulation.py to use old ElevenLabs API
"""

def fix_simulation():
    print("🔧 Fixing pi_simulation.py for old ElevenLabs API...")
    
    try:
        # Read the file
        with open('pi_simulation.py', 'r') as f:
            content = f.read()
        
        # Find and replace the import section
        old_import = '''try:
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
        
        new_import = '''try:
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
        
        # Replace the import section
        if old_import in content:
            content = content.replace(old_import, new_import)
            print("✅ Updated import section")
        else:
            print("⚠️ Import section not found")
        
        # Also fix the speak_message method to use old API
        old_speak = '''            if generate and set_api_key:
                # Use old API
                audio = generate(text=message, voice=self.voice_id)
            else:
                # Use new Client API
                from elevenlabs import Client
                client = Client(api_key=self.api_key)
                audio = client.generate(text=message, voice=self.voice_id)'''
        
        new_speak = '''            # Use old API
            audio = generate(text=message, voice=self.voice_id)'''
        
        if old_speak in content:
            content = content.replace(old_speak, new_speak)
            print("✅ Updated speak_message method")
        
        # Write the updated content
        with open('pi_simulation.py', 'w') as f:
            f.write(content)
        
        print("✅ pi_simulation.py updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix simulation: {e}")
        return False

if __name__ == "__main__":
    fix_simulation()
