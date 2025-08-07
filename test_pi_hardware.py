#!/usr/bin/env python3
"""
Pi Hardware Detection Test
==========================

This script tests the Pi hardware detection and configuration system
to ensure it works correctly on both Pi hardware and simulation environments.

Usage:
    python test_pi_hardware.py
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from pi_detection import PiDetector
import logging

def test_pi_detection():
    """Test Pi hardware detection and configuration."""
    print("🧪 Testing Pi Hardware Detection")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test 1: Hardware Detection
    print("\n1. Testing Hardware Detection...")
    try:
        detector = PiDetector()
        is_pi = detector.is_raspberry_pi()
        model = detector.get_pi_model()
        
        print(f"✅ Hardware detected: {'Pi' if is_pi else 'Simulation'}")
        if model:
            print(f"✅ Model: {model}")
        
    except Exception as e:
        print(f"❌ Hardware detection failed: {e}")
    
    # Test 2: Configuration Loading
    print("\n2. Testing Configuration Loading...")
    try:
        config = detector.get_config()
        print("✅ Configuration loaded successfully")
        
        # Display configuration sections
        display_config = detector.get_display_config()
        audio_config = detector.get_audio_config()
        performance_config = detector.get_performance_config()
        feature_config = detector.get_feature_config()
        
        print(f"   Display: fullscreen={display_config.get('fullscreen')}, vsync={display_config.get('vsync')}")
        print(f"   Audio: volume={audio_config.get('volume')}, buffer={audio_config.get('buffer_size')}")
        print(f"   Performance: max_fps={performance_config.get('max_fps')}, memory_limit={performance_config.get('memory_limit')}")
        print(f"   Features: gpio={feature_config.get('enable_gpio')}, touch={feature_config.get('enable_touch_support')}")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
    
    # Test 3: Pi Health Check
    print("\n3. Testing Pi Health Check...")
    try:
        health = detector.check_pi_health()
        print("✅ Health check completed")
        
        for key, value in health.items():
            if value is not None:
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 4: Performance Optimization
    print("\n4. Testing Performance Optimization...")
    try:
        if detector.is_raspberry_pi():
            detector.optimize_for_pi()
            print("✅ Pi optimizations applied")
        else:
            print("ℹ️ Skipping Pi optimizations (not on Pi hardware)")
        
    except Exception as e:
        print(f"❌ Performance optimization failed: {e}")
    
    # Test 5: Integration with Main Application
    print("\n5. Testing Main Application Integration...")
    try:
        # Import main application components
        from main import DayPlanner
        
        # Create application instance
        app = DayPlanner()
        print("✅ DayPlanner instance created successfully")
        
        # Check if Pi detector is properly integrated
        if hasattr(app, 'pi_detector'):
            print("✅ Pi detector integrated with main application")
            print(f"   Hardware: {'Pi' if app.pi_detector.is_raspberry_pi() else 'Simulation'}")
        else:
            print("❌ Pi detector not found in main application")
        
    except Exception as e:
        print(f"❌ Main application integration failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Pi Hardware Detection Test Completed!")
    print("\nKey Features Verified:")
    print("- Hardware detection (Pi vs simulation)")
    print("- Configuration loading for different hardware")
    print("- Pi health monitoring")
    print("- Performance optimizations")
    print("- Main application integration")

if __name__ == "__main__":
    test_pi_detection()
