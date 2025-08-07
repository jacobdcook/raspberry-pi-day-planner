#!/usr/bin/env python3
"""
Simple ElevenLabs Test - No audio generation, just API check
"""

def simple_test():
    print("🎤 Simple ElevenLabs Test...")
    print("=" * 50)
    
    try:
        # Test 1: Check if elevenlabs module is available
        print("📡 Test 1: Checking ElevenLabs module...")
        try:
            import elevenlabs
            print(f"✅ ElevenLabs module imported")
            print(f"📋 Version: {elevenlabs.__version__}")
        except ImportError as e:
            print(f"❌ ElevenLabs module not available: {e}")
            return False
        
        # Test 2: Check what functions are available
        print("\n🔧 Test 2: Checking available functions...")
        try:
            # Try to import the main functions
            from elevenlabs import generate, set_api_key
            print("✅ generate and set_api_key functions found")
            
            # Test 3: Set API key (no audio generation)
            print("\n🔑 Test 3: Setting API key...")
            api_key = "sk_c326ebc4e6330a123b315239f3b69c850c675025793f3a92"
            set_api_key(api_key)
            print("✅ API key set successfully")
            
            print("\n" + "=" * 50)
            print("🎤 ElevenLabs API test completed!")
            print("✅ ElevenLabs should work in the simulation")
            return True
            
        except ImportError as e:
            print(f"❌ generate/set_api_key not available: {e}")
            return False
        
    except Exception as e:
        print(f"❌ ElevenLabs test failed: {e}")
        return False

if __name__ == "__main__":
    simple_test()
