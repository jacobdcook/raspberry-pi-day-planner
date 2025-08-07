#!/usr/bin/env python3
"""
Fix ElevenLabs import in pi_simulation.py
"""

def fix_elevenlabs_import():
    print("🔧 Fixing ElevenLabs import in pi_simulation.py...")
    
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
    from elevenlabs import Client
    ELEVENLABS_AVAILABLE = True
    generate = None
    set_api_key = None
    print("✅ ElevenLabs Client imported successfully")
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
            print("⚠️ Import section not found, adding new import")
            # Find the line with "from backlog_manager import BacklogManager"
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'from backlog_manager import BacklogManager' in line:
                    # Insert new import after this line
                    lines.insert(i + 1, new_import)
                    content = '\n'.join(lines)
                    break
        
        # Write the updated content
        with open('pi_simulation.py', 'w') as f:
            f.write(content)
        
        print("✅ pi_simulation.py updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix ElevenLabs import: {e}")
        return False

if __name__ == "__main__":
    fix_elevenlabs_import()
