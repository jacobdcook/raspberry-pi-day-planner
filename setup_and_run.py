#!/usr/bin/env python3
"""
Setup and run script for Raspberry Pi Day Planner
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and show progress."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("🚀 Raspberry Pi Day Planner Setup")
    print("=" * 50)
    
    # Step 1: Check if virtual environment exists
    if not os.path.exists("dayplanner_env"):
        print("📦 Creating virtual environment...")
        if not run_command("python3 -m venv dayplanner_env", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Step 2: Activate virtual environment and install requirements
    print("📦 Installing requirements...")
    activate_cmd = "source dayplanner_env/bin/activate && pip install -r requirements.txt"
    if not run_command(activate_cmd, "Installing requirements"):
        return False
    
    # Step 3: Apply voice fixes
    print("🔧 Applying voice fixes...")
    if os.path.exists("fix_voice_fallback.py"):
        activate_and_fix = "source dayplanner_env/bin/activate && python3 fix_voice_fallback.py"
        run_command(activate_and_fix, "Applying voice fallback fix")
    
    # Step 4: Run the simulation
    print("🎮 Starting simulation...")
    print("=" * 50)
    print("🤖 The simulation will start in 3 seconds...")
    print("📋 Controls:")
    print("   - SPACE: Test voice")
    print("   - A: Test WAV sounds")
    print("   - T: Toggle theme")
    print("   - F11: Toggle fullscreen")
    print("   - ESC: Quit")
    print("=" * 50)
    
    time.sleep(3)
    
    # Run the simulation
    run_cmd = "source dayplanner_env/bin/activate && python3 pi_simulation.py"
    print("🎮 Launching simulation...")
    os.system(run_cmd)

if __name__ == "__main__":
    main()
