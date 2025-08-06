#!/usr/bin/env python3
"""
Test script to verify ESC key functionality in the simulation.
This script will run the simulation and provide instructions for testing.
"""

import subprocess
import sys
import os

def main():
    print("🧪 Testing ESC Key Functionality")
    print("=" * 50)
    print()
    print("This test will launch the Raspberry Pi Day Planner simulation.")
    print("Please test the following ESC key behaviors:")
    print()
    print("1. From any screen (except idle): Press ESC to return to idle screen")
    print("2. From idle screen: Press ESC to show exit confirmation")
    print("3. In exit confirmation: Click 'Yes' to exit, 'No' to cancel")
    print("4. In exit confirmation: Press Enter to confirm exit (alternative to Yes button)")
    print("5. Test with completed tasks to see unsaved progress warning")
    print()
    print("Starting simulation...")
    print()
    
    try:
        # Run the simulation
        subprocess.run([sys.executable, "pi_simulation.py"], check=True)
    except KeyboardInterrupt:
        print("\n✅ Test completed by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Simulation exited with error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 