#!/usr/bin/env python3
"""
Check what's currently in pi_simulation.py
"""

def check_simulation():
    print("🔍 Checking pi_simulation.py content...")
    
    try:
        with open('pi_simulation.py', 'r') as f:
            content = f.read()
        
        # Look for ElevenLabs import
        print("\n📋 Looking for ElevenLabs imports...")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'elevenlabs' in line.lower():
                print(f"Line {i+1}: {line.strip()}")
        
        # Look for speak_message method
        print("\n🎤 Looking for speak_message method...")
        if 'def speak_message' in content:
            start = content.find('def speak_message')
            end = content.find('\n\n', start)
            if end == -1:
                end = len(content)
            method = content[start:end]
            print("Found speak_message method:")
            print(method)
        else:
            print("❌ speak_message method not found")
        
        # Look for setup section
        print("\n🔧 Looking for ElevenLabs setup...")
        if 'Setup ElevenLabs' in content:
            start = content.find('        # Setup ElevenLabs')
            end = content.find('\n        else:', start)
            if end == -1:
                end = content.find('\n        print', start)
            if end == -1:
                end = len(content)
            setup = content[start:end]
            print("Found setup section:")
            print(setup)
        else:
            print("❌ ElevenLabs setup not found")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    check_simulation()
