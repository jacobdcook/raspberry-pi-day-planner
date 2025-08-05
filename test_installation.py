#!/usr/bin/env python3
"""
Test Installation Script

This script tests all components of the Raspberry Pi Day Planner to ensure
everything is working correctly after installation.

Author: Raspberry Pi Day Planner
License: MIT
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing module imports...")
    
    try:
        import yaml
        print("✓ PyYAML imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyYAML: {e}")
        return False
    
    try:
        import pygame
        print("✓ Pygame imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Pygame: {e}")
        return False
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✓ APScheduler imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import APScheduler: {e}")
        return False
    
    try:
        from dateutil import rrule
        print("✓ python-dateutil imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import python-dateutil: {e}")
        return False
    
    try:
        import pytz
        print("✓ pytz imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pytz: {e}")
        return False
    
    try:
        import tkinter
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import tkinter: {e}")
        return False
    
    try:
        import sqlite3
        print("✓ sqlite3 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import sqlite3: {e}")
        return False
    
    return True

def test_project_modules():
    """Test that all project modules can be imported."""
    print("\nTesting project modules...")
    
    try:
        from modules.loader import ScheduleLoader
        print("✓ ScheduleLoader imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ScheduleLoader: {e}")
        return False
    
    try:
        from modules.scheduler import TaskScheduler
        print("✓ TaskScheduler imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import TaskScheduler: {e}")
        return False
    
    try:
        from modules.display import DisplayManager
        print("✓ DisplayManager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import DisplayManager: {e}")
        return False
    
    try:
        from modules.audio import AudioManager
        print("✓ AudioManager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AudioManager: {e}")
        return False
    
    try:
        from modules.logger import EventLogger
        print("✓ EventLogger imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import EventLogger: {e}")
        return False
    
    try:
        from modules.utils import setup_logging, format_time_delta
        print("✓ Utils imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Utils: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from modules.loader import ScheduleLoader
        loader = ScheduleLoader()
        schedule = loader.load_schedule()
        print(f"✓ Configuration loaded successfully ({len(schedule)} tasks)")
        return True
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def test_audio_system():
    """Test audio system initialization."""
    print("\nTesting audio system...")
    
    try:
        from modules.audio import AudioManager
        audio_manager = AudioManager()
        print("✓ Audio manager initialized successfully")
        
        # Test volume control
        audio_manager.set_volume(0.5)
        volume = audio_manager.get_volume()
        print(f"✓ Volume control working (current: {volume})")
        
        audio_manager.close()
        return True
    except Exception as e:
        print(f"✗ Failed to initialize audio system: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from modules.logger import EventLogger
        logger = EventLogger()
        
        # Test database info
        info = logger.get_database_info()
        print(f"✓ Database initialized successfully")
        print(f"  - Database path: {info.get('database_path', 'Unknown')}")
        print(f"  - File size: {info.get('file_size_mb', 0)} MB")
        print(f"  - Total events: {info.get('total_events', 0)}")
        
        logger.close()
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        return False

def test_file_structure():
    """Test that all required files and directories exist."""
    print("\nTesting file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "config/schedule.yaml",
        "modules/loader.py",
        "modules/scheduler.py",
        "modules/display.py",
        "modules/audio.py",
        "modules/logger.py",
        "modules/utils.py"
    ]
    
    required_dirs = [
        "config",
        "modules",
        "data",
        "logs",
        "sounds"
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
            all_good = False
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ (missing)")
            all_good = False
    
    return all_good

def test_system_info():
    """Test system information utilities."""
    print("\nTesting system utilities...")
    
    try:
        from modules.utils import get_system_info, is_raspberry_pi
        from modules.utils import check_disk_space
        
        # Test system info
        sys_info = get_system_info()
        print(f"✓ System info retrieved")
        print(f"  - Platform: {sys_info.get('platform', 'Unknown')}")
        print(f"  - Python: {sys_info.get('python_version', 'Unknown')}")
        
        # Test Raspberry Pi detection
        is_pi = is_raspberry_pi()
        print(f"  - Raspberry Pi: {'Yes' if is_pi else 'No'}")
        
        # Test disk space
        disk_info = check_disk_space(".")
        print(f"  - Free space: {disk_info.get('free_gb', 0)} GB")
        
        return True
    except Exception as e:
        print(f"✗ Failed to get system info: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Raspberry Pi Day Planner - Installation Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("Project Modules", test_project_modules),
        ("Configuration", test_configuration),
        ("Audio System", test_audio_system),
        ("Database", test_database),
        ("File Structure", test_file_structure),
        ("System Utilities", test_system_info)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} passed\n")
            else:
                print(f"✗ {test_name} failed\n")
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}\n")
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed! Installation is successful.")
        print("\nYou can now:")
        print("1. Start the service: sudo systemctl start raspberry-pi-day-planner")
        print("2. Run manually: python main.py")
        print("3. Check logs: sudo journalctl -u raspberry-pi-day-planner -f")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check file permissions and ownership")
        print("3. Verify Python version (3.8+ required)")
        print("4. Check the README.md for detailed installation instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 