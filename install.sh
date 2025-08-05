#!/bin/bash

# Raspberry Pi Day Planner - Installation Script
# This script automates the installation and setup process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running on Raspberry Pi
check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        print_warning "This script is designed for Raspberry Pi. Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_error "Installation cancelled."
            exit 1
        fi
    fi
}

# Function to check Python version
check_python_version() {
    if command -v python3 &> /dev/null; then
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Python version: $python_version"
        
        # Check if version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update
    sudo apt upgrade -y
    print_success "System packages updated"
}

# Function to install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    sudo apt install -y python3-pip python3-venv python3-tk python3-dev
    print_success "System dependencies installed"
}

# Function to create virtual environment
create_virtual_environment() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Function to install Python dependencies
install_python_dependencies() {
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Python dependencies installed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p data logs sounds
    print_success "Directories created"
}

# Function to setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    # Get current directory
    current_dir=$(pwd)
    current_user=$(whoami)
    
    # Create service file with correct paths
    cat > raspberry-pi-day-planner.service << EOF
[Unit]
Description=Raspberry Pi Day Planner
After=network.target graphical-session.target
Wants=network.target

[Service]
Type=simple
User=$current_user
Group=$current_user
WorkingDirectory=$current_dir
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$current_user/.Xauthority
ExecStart=$current_dir/venv/bin/python $current_dir/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$current_dir/data
ReadWritePaths=$current_dir/logs

[Install]
WantedBy=multi-user.target
EOF
    
    # Copy service file to systemd directory
    sudo cp raspberry-pi-day-planner.service /etc/systemd/system/
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable raspberry-pi-day-planner
    
    print_success "Systemd service configured"
}

# Function to setup permissions
setup_permissions() {
    print_status "Setting up file permissions..."
    chmod +x main.py
    chmod +x install.sh
    print_success "File permissions set"
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Python imports
    source venv/bin/activate
    python3 -c "
import yaml
import pygame
import sqlite3
import tkinter
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import rrule
import pytz
print('All dependencies imported successfully')
"
    
    print_success "Installation test passed"
}

# Function to show next steps
show_next_steps() {
    echo
    print_success "Installation completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Edit the schedule configuration:"
    echo "   nano config/schedule.yaml"
    echo
    echo "2. Start the service:"
    echo "   sudo systemctl start raspberry-pi-day-planner"
    echo
    echo "3. Check service status:"
    echo "   sudo systemctl status raspberry-pi-day-planner"
    echo
    echo "4. View logs:"
    echo "   sudo journalctl -u raspberry-pi-day-planner -f"
    echo
    echo "5. For manual testing:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    echo
    echo "For more information, see README.md"
}

# Main installation function
main() {
    echo "=========================================="
    echo "Raspberry Pi Day Planner - Installation"
    echo "=========================================="
    echo
    
    # Check prerequisites
    check_raspberry_pi
    check_python_version
    
    # Installation steps
    update_system
    install_system_dependencies
    create_virtual_environment
    install_python_dependencies
    create_directories
    setup_systemd_service
    setup_permissions
    test_installation
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@" 