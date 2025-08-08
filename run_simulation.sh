#!/bin/bash

echo "🚀 Raspberry Pi Day Planner - One-Click Setup"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "dayplanner_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv dayplanner_env
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate environment and install requirements
echo "📦 Installing requirements..."
source dayplanner_env/bin/activate
pip install -r requirements.txt

# Apply voice fixes if available
if [ -f "fix_voice_fallback.py" ]; then
    echo "🔧 Applying voice fixes..."
    python3 fix_voice_fallback.py
fi

# Show controls
echo ""
echo "🎮 Starting simulation..."
echo "=============================================="
echo "🤖 The simulation will start in 3 seconds..."
echo "📋 Controls:"
echo "   - SPACE: Test voice"
echo "   - A: Test WAV sounds"
echo "   - T: Toggle theme"
echo "   - F11: Toggle fullscreen"
echo "   - ESC: Quit"
echo "=============================================="

sleep 3

# Run the simulation
echo "🎮 Launching simulation..."
python3 pi_simulation.py
