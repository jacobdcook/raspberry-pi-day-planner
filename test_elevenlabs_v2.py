#!/usr/bin/env python3
"""
Test ElevenLabs v2.9.1 API
"""

def test_elevenlabs_v2():
    print("🎤 Testing ElevenLabs v2.9.1...")
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
        
        # Test 2: Check what's available in the module
        print("\n🔧 Test 2: Checking available functions...")
        print(f"📋 Available functions: {[f for f in dir(elevenlabs) if not f.startswith('_')]}")
        
        # Test 3: Try to import from text_to_speech module
        print("\n🎵 Test 3: Trying text_to_speech module...")
        try:
            from elevenlabs import text_to_speech
            print("✅ text_to_speech module found")
            
            # Test 4: Try to import from voices module
            print("\n🎤 Test 4: Trying voices module...")
            try:
                from elevenlabs import voices
                print("✅ voices module found")
                
                # Test 5: Try to import from client module
                print("\n🔧 Test 5: Trying client module...")
                try:
                    from elevenlabs import client
                    print("✅ client module found")
                    
                    # Test 6: Try to create a client
                    print("\n🔑 Test 6: Creating client...")
                    api_key = "sk_c326ebc4e6330a123b315239f3b69c850c675025793f3a92"
                    
                    # Try different ways to create client
                    try:
                        from elevenlabs import ElevenLabs
                        client = ElevenLabs(api_key=api_key)
                        print("✅ ElevenLabs client created successfully")
                    except Exception as e:
                        print(f"❌ Failed to create ElevenLabs client: {e}")
                        
                        # Try alternative method
                        try:
                            from elevenlabs import AsyncElevenLabs
                            client = AsyncElevenLabs(api_key=api_key)
                            print("✅ AsyncElevenLabs client created successfully")
                        except Exception as e2:
                            print(f"❌ Failed to create AsyncElevenLabs client: {e2}")
                            return False
                    
                    print("\n" + "=" * 50)
                    print("🎤 ElevenLabs v2.9.1 test completed!")
                    print("✅ ElevenLabs should work in the simulation")
                    return True
                    
                except ImportError as e:
                    print(f"❌ client module not available: {e}")
                    return False
                    
            except ImportError as e:
                print(f"❌ voices module not available: {e}")
                return False
                
        except ImportError as e:
            print(f"❌ text_to_speech module not available: {e}")
            return False
        
    except Exception as e:
        print(f"❌ ElevenLabs test failed: {e}")
        return False

if __name__ == "__main__":
    test_elevenlabs_v2()
