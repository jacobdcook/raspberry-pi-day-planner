#!/bin/bash

echo "🖥️ Installing Desktop Shortcut for Raspberry Pi Day Planner"
echo "=========================================================="

# Get the current directory
CURRENT_DIR=$(pwd)
echo "📁 Current directory: $CURRENT_DIR"

# Create the desktop shortcut with Trusted=true
echo "🔧 Creating desktop shortcut..."
cat > "Raspberry Pi Day Planner.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Raspberry Pi Day Planner
Comment=Start the day planner simulation
Exec=bash -c "cd $CURRENT_DIR && ./run_simulation.sh"
Icon=applications-development
Terminal=true
Categories=Utility;Development;
StartupNotify=true
Trusted=true
EOF

# Make the shortcut executable
chmod +x "Raspberry Pi Day Planner.desktop"

# Copy to desktop
echo "📋 Copying to desktop..."
cp "Raspberry Pi Day Planner.desktop" ~/Desktop/

# Make desktop version executable
chmod +x ~/Desktop/"Raspberry Pi Day Planner.desktop"

# Force it to be trusted (no popup)
echo "🔐 Making shortcut trusted..."
gio set ~/Desktop/"Raspberry Pi Day Planner.desktop" metadata::trusted true

echo "✅ Desktop shortcut installed and trusted!"
echo "🎮 You can now double-click 'Raspberry Pi Day Planner' on your desktop (no popup!)"
echo "📁 Or run: ./run_simulation.sh from the terminal"
