#!/usr/bin/env python3
"""
Simple test to check ElevenLabs import
"""

print("🔍 Testing ElevenLabs import...")

try:
    from elevenlabs import ElevenLabs
    print("✅ ElevenLabs imported successfully")
    
    # Test creating client
    api_key = "sk_c326ebc4e6330a123b315239f3b69c850c675025793f3a92"
    client = ElevenLabs(api_key=api_key)
    print("✅ Client created successfully")
    
    # Test text-to-speech
    try:
        audio = client.text_to_speech.convert(
            text="Hello, this is a test!",
            voice_id="21m00Tcm4TlvDq8ikWAM"
        )
        print(f"✅ Audio generated: {len(audio)} bytes")
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

print("�� Test completed!")
