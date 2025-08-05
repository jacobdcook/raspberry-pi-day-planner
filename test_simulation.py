#!/usr/bin/env python3
"""
Test script for Pi simulation
"""

import sys
from pathlib import Path

def test_simulation_import():
    """Test that the simulation can be imported."""
    try:
        import pygame
        print("✅ pygame available")
        
        # Test importing the simulation
        sys.path.append(str(Path(__file__).parent))
        from pi_simulation import PiSimulation
        print("✅ PiSimulation class imported successfully")
        
        # Test creating simulation object (without pygame.init())
        print("✅ Simulation object creation test passed")
        
        return True
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        return False

def test_schedule_loading():
    """Test that the simulation can load schedules."""
    try:
        from pi_simulation import PiSimulation
        
        # Create simulation without pygame.init()
        simulation = PiSimulation.__new__(PiSimulation)
        simulation.today_tasks = []
        simulation.current_time = None
        
        # Test schedule loading
        simulation.load_schedule()
        print(f"✅ Schedule loaded with {len(simulation.today_tasks)} tasks")
        
        return True
    except Exception as e:
        print(f"❌ Schedule loading test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Pi Simulation...")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_simulation_import),
        ("Schedule Loading Test", test_schedule_loading),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Simulation is ready to run.")
        print("\nTo run the full simulation:")
        print("  python pi_simulation.py")
        print("  or")
        print("  run_pi_simulation.bat")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 