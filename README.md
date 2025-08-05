# 🧬 Raspberry Pi Day Planner

A sophisticated personal productivity system built for Raspberry Pi that combines task scheduling, health tracking, and advanced peptide protocol management. Perfect for biohackers, productivity enthusiasts, and anyone looking to optimize their daily routine.

## ✨ Features

### 📅 **Smart Scheduling System**

- **Multi-Schedule Support**: Choose between sample, personal, or specialized peptide schedules
- **Recurring Tasks**: Full iCalendar RRULE support for complex scheduling
- **Priority Management**: Color-coded priority system with audio alerts
- **Snooze & Duration**: Flexible task management with customizable snooze times

### 💉 **Peptide Protocol Management**

- **BPC-157 & TB-500 Tracking**: Specialized scheduler for peptide administration
- **Progress Monitoring**: Track completion percentages, streaks, and missed doses
- **Dose History**: Comprehensive logging of administration history
- **Upcoming Doses**: View next 7 days of scheduled doses

### 🎯 **Productivity Features**

- **Audio Alerts**: Customizable sound notifications for tasks
- **Web Interface**: Remote access via web dashboard
- **Health Metrics**: Track weight, blood pressure, and other vital signs
- **Analytics Dashboard**: Progress tracking and performance insights

### 🔒 **Privacy-First Design**

- **Git-Protected**: Personal schedules excluded from version control
- **Local Storage**: All data stored locally for maximum privacy
- **Configurable Sharing**: Choose what to share publicly

## 🚀 Quick Start

### Option 1: Windows Test Environment (No Raspberry Pi Required)

Want to test the system before buying a Raspberry Pi? Perfect for trying out features and planning your setup.

```bash
# Clone the repository
git clone https://github.com/jacobdcook/raspberry-pi-day-planner.git
cd raspberry-pi-day-planner

# Install Windows dependencies
pip install -r requirements_windows.txt

# Run the Windows test environment
python windows_test.py
```

**Windows Features:**

- 🖥️ Full GUI interface with tabs
- ⏱️ Start/stop task timers
- 📋 Task list with priority indicators
- 💉 Peptide protocol tracking
- 📊 Progress reports and accountability
- 🔄 Real-time updates

### Option 2: Pi Simulation (Visual Preview)

Want to see exactly how your Raspberry Pi will look and behave? Try our visual simulation:

```bash
# Install dependencies (includes pygame)
pip install -r requirements_windows.txt

# Run the Pi simulation
python pi_simulation.py
# or
run_pi_simulation.bat
```

**Simulation Features:**

- 🖥️ Full-screen display simulation (like Pi with monitor)
- 🔔 Task notifications with DONE/SKIP buttons
- ⏰ Idle screen showing current time and next task
- 🖱️ Mouse/touch click handling
- 🔄 Real-time updates and interactions
- 🎮 Exact Pi behavior simulation

**Controls:**
- **SPACE**: Simulate task notification
- **Mouse**: Click DONE/SKIP buttons
- **ESC**: Exit simulation

This gives you a perfect preview of your Pi experience!

### Option 3: Complete Raspberry Pi Setup

For full deployment with custom hardware integration.

#### **Step 1: Hardware Requirements**

**Essential Components:**

- Raspberry Pi 4 (4GB RAM recommended)
- MicroSD card (32GB+ Class 10)
- Power supply (5V/3A)
- HDMI cable and monitor (for initial setup)
- USB keyboard and mouse

**Optional Hardware:**

- 3.5" LCD display (for dedicated display)
- Speaker system (for audio alerts)
- LED strip (for visual notifications)
- Push buttons (for manual controls)

#### **Step 2: Raspberry Pi Setup**

```bash
# Download Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# Flash Raspberry Pi OS (64-bit) to microSD card
# Enable SSH and set WiFi credentials during imaging

# Insert microSD card and boot Raspberry Pi
# Connect via SSH: ssh pi@raspberrypi.local
```

#### **Step 3: System Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install additional dependencies
sudo apt install git screen htop -y

# Set up virtual environment
python3 -m venv dayplanner
source dayplanner/bin/activate
```

#### **Step 4: Install Day Planner**

```bash
# Clone repository
git clone https://github.com/jacobdcook/raspberry-pi-day-planner.git
cd raspberry-pi-day-planner

# Install Python dependencies
pip install -r requirements.txt

# Set up your personal schedule
cp config/schedule.yaml config/schedule_personal.yaml
# Edit config/schedule_personal.yaml with your tasks
```

#### **Step 5: Configure Your Schedule**

Create your personal schedule in `config/schedule.yaml`:

```yaml
# Example Schedule Configuration
settings:
  timezone: "America/New_York"
  display_timeout: 30
  audio_enabled: true
  web_interface_enabled: true
  web_port: 8080

# Daily Tasks
daily_tasks:
  - title: "Morning Routine"
    time: "07:00"
    notes: "Start the day with exercise and planning"
    priority: 1
    audio_alert: true
    snooze_duration: 10
    duration: 30

  - title: "Work Session"
    time: "09:00"
    notes: "Focus on important projects"
    priority: 2
    audio_alert: true
    snooze_duration: 5
    duration: 120

# Weekly Tasks
weekly_tasks:
  - title: "Weekly Review"
    day: "Sunday"
    time: "10:00"
    notes: "Review past week and plan next week"
    priority: 1
    audio_alert: true
    snooze_duration: 15
    duration: 60

# Health Metrics
health_metrics:
  - title: "Morning Weight Check"
    time: "07:30"
    metric_type: "weight"
    target_value: 70.0
    unit: "kg"
    priority: 2
    audio_alert: false
```

#### **Step 6: Advanced Raspberry Pi Configuration**

**Auto-Start Setup:**

```bash
# Create systemd service
sudo cp raspberry-pi-day-planner.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable raspberry-pi-day-planner
sudo systemctl start raspberry-pi-day-planner

# Check status
sudo systemctl status raspberry-pi-day-planner
```

**Display Configuration (Optional):**

```bash
# For dedicated LCD displays
sudo apt install python3-pil python3-pil.imagetk -y

# Configure display rotation
sudo nano /boot/config.txt
# Add: display_rotate=0 (or 90, 180, 270)

# For touch displays
sudo apt install xinput-calibrator -y
```

**Audio Setup:**

```bash
# Test audio
speaker-test -t wav -c 2

# Configure audio output
sudo raspi-config
# Navigate to: System Options > Audio > Force 3.5mm jack
```

**Network Configuration:**

```bash
# Set static IP (optional)
sudo nano /etc/dhcpcd.conf
# Add:
# interface eth0
# static ip_address=192.168.1.100/24
# static routers=192.168.1.1
# static domain_name_servers=8.8.8.8
```

#### **Step 7: Custom Hardware Integration**

**LED Strip Setup:**

```bash
# Install LED library
pip install rpi.gpio neopixel

# Test LED strip
python -c "
import board
import neopixel
pixels = neopixel.NeoPixel(board.D18, 8)
pixels.fill((255, 0, 0))  # Red
"
```

**Button Integration:**

```bash
# Test GPIO buttons
python -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print('Button ready on GPIO 17')
"
```

#### **Step 8: Web Interface Access**

```bash
# Access web dashboard
# http://raspberrypi.local:8080
# or http://YOUR_PI_IP:8080

# Enable port forwarding (if needed)
sudo ufw allow 8080
```

#### **Step 9: Monitoring & Maintenance**

```bash
# View logs
sudo journalctl -u raspberry-pi-day-planner -f

# Check system resources
htop

# Update application
cd raspberry-pi-day-planner
git pull
pip install -r requirements.txt
sudo systemctl restart raspberry-pi-day-planner
```

# Advanced Features

advanced_features:
weather_check:
enabled: true
location: "New York"
check_time: "07:00"

system_monitor:
enabled: true
check_interval: 300 # 5 minutes

````

### 4. **Run the Schedule Selector**

```bash
python schedule_selector.py
````

Choose your preferred schedule:

- **Sample Schedule**: Demo for public sharing
- **Personal Schedule**: Your actual daily routine
- **Peptide Schedule**: Specialized BPC-157 + TB-500 protocol

### 5. **Start the Main Application**

```bash
python main.py
```

## 💉 Peptide Protocol Setup

For users tracking peptide protocols (BPC-157, TB-500, etc.):

### Create Peptide Schedule

Create `config/peptide_schedule.yaml`:

```yaml
peptide_protocol:
  protocol_name: "BPC-157 + TB-500 Healing Protocol"
  protocol_duration: "2025-08-04 to 2025-10-26"
  administration_time: "12:15"
  priority: 1

  august_2025:
    "2025-08-04":
      bpc_157: "1.1 mg (0.1 mL BPC vial + 0.75 mL TB vial)"
      tb_500: "~3.1 mg [TB vial contains BPC-157 mix]"
      notes: "Protocol start - Loading dose"

    "2025-08-05":
      bpc_157: "250 mcg (5 units from BPC vial)"
      tb_500: "None"
      notes: "BPC-157 only"
```

### Use Peptide Scheduler

```python
from modules.peptide_scheduler import PeptideScheduler

# Initialize
scheduler = PeptideScheduler(config_dir="config")
scheduler.load_peptide_schedule()

# Get today's dose
today_dose = scheduler.get_today_peptide_dose()
print(f"Today's dose: {today_dose}")

# Track administration
scheduler.log_peptide_administration(today_dose, administered=True)

# View progress
progress = scheduler.get_peptide_progress()
print(f"Progress: {progress['progress_percentage']}%")
```

## 🏗️ Architecture

### **Modular Design**

```
raspberry-pi-day-planner/
├── modules/
│   ├── scheduler.py          # Main task scheduler
│   ├── peptide_scheduler.py  # Peptide protocol management
│   ├── display.py           # Display interface
│   ├── audio.py             # Audio alerts
│   ├── web_api.py           # Web interface
│   └── analytics.py         # Progress tracking
├── config/
│   ├── schedule.yaml        # Your personal schedule (gitignored)
│   ├── schedule2.yaml       # Alternative schedule (gitignored)
│   └── peptide_schedule.yaml # Peptide protocol (gitignored)
├── templates/
│   └── dashboard.html       # Web dashboard
└── main.py                  # Main application
```

### **Key Components**

#### **Task Scheduler (`modules/scheduler.py`)**

- APScheduler integration for robust task management
- iCalendar RRULE support for complex recurring tasks
- Timezone-aware scheduling
- Priority-based task execution

#### **Peptide Scheduler (`modules/peptide_scheduler.py`)**

- Specialized peptide protocol management
- Dose tracking and progress monitoring
- Integration with main scheduler
- Export capabilities for data analysis

#### **Display Manager (`modules/display.py`)**

- Raspberry Pi display interface
- Real-time task updates
- Priority color coding
- Weather and system status

## 🔧 Configuration

### **Environment Variables**

```bash
export TIMEZONE="America/New_York"
export WEB_PORT=8080
export AUDIO_ENABLED=true
```

### **Schedule File Structure**

```yaml
settings:
  timezone: "America/New_York"
  display_timeout: 30
  audio_enabled: true

daily_tasks:
  - title: "Task Name"
    time: "HH:MM"
    notes: "Task description"
    priority: 1-3
    audio_alert: true/false
    snooze_duration: minutes
    duration: minutes

weekly_tasks:
  - title: "Weekly Task"
    day: "DayName"
    time: "HH:MM"
    # ... other fields

health_metrics:
  - title: "Metric Name"
    time: "HH:MM"
    metric_type: "weight/blood_pressure/etc"
```

## 🔧 Troubleshooting

### **Windows Test Environment Issues**

1. **"No tasks loaded"**:

   - Check that `config/schedule.yaml` exists and has proper YAML syntax
   - Verify file encoding is UTF-8
   - Ensure task sections (`morning_tasks`, `afternoon_tasks`) are properly formatted

2. **"Charmap codec error"**:

   - File encoding issue - ensure files are saved as UTF-8
   - Re-save YAML files with UTF-8 encoding

3. **"Module not found"**:

   - Run `pip install -r requirements_windows.txt`
   - Ensure Python 3.7+ is installed

4. **GUI not opening**:
   - Ensure tkinter is installed (usually included with Python)
   - Try running `python -c "import tkinter; print('tkinter OK')"`

### **Raspberry Pi Setup Issues**

1. **Service not starting**:

   ```bash
   sudo journalctl -u raspberry-pi-day-planner -f
   sudo systemctl status raspberry-pi-day-planner
   ```

2. **Audio not working**:

   ```bash
   speaker-test -t wav -c 2
   sudo raspi-config  # System Options > Audio
   ```

3. **Display issues**:

   ```bash
   # Check HDMI connection
   vcgencmd get_mem gpu

   # Configure display rotation
   sudo nano /boot/config.txt
   # Add: display_rotate=0
   ```

4. **Network connectivity**:
   ```bash
   ping google.com
   curl http://localhost:8080
   sudo ufw allow 8080
   ```

### **Hardware Integration Issues**

1. **LED strip not working**:

   ```bash
   # Test GPIO
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO OK')"

   # Check power supply (LED strips need 5V)
   # Verify data pin connection
   ```

2. **Buttons not responding**:
   ```bash
   # Test button on GPIO 17
   python3 -c "
   import RPi.GPIO as GPIO
   import time
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   while True:
       if GPIO.input(17) == False:
           print('Button pressed!')
           time.sleep(0.2)
   "
   ```

### **Performance Optimization**

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# Optimize memory usage
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# Monitor resources
htop
free -h
df -h

# Check temperature
vcgencmd measure_temp
```

### **Debug Commands**

```bash
# Check Python environment
python3 -c "import yaml, tkinter, APScheduler; print('All dependencies OK')"

# Test file permissions
ls -la config/
chmod 644 config/*.yaml

# Verify schedule loading
python3 -c "
import yaml
with open('config/schedule.yaml', 'r') as f:
    data = yaml.safe_load(f)
    print('Schedule loaded successfully')
    print(f'Found {len(data.get(\"morning_tasks\", []))} morning tasks')
    print(f'Found {len(data.get(\"afternoon_tasks\", []))} afternoon tasks')
"

# Check system logs
sudo journalctl -u raspberry-pi-day-planner --since "1 hour ago"
```

## 📊 Resume Highlights

This project demonstrates:

- **Full-Stack Development**: Python backend with web interface and GUI
- **IoT Integration**: Raspberry Pi hardware control and sensor integration
- **Data Management**: YAML configuration with privacy-focused design
- **System Administration**: Linux service management and automation
- **Cross-Platform Development**: Windows testing environment with Pi deployment
- **Health Tech**: Specialized peptide protocol tracking and analytics
- **Privacy Engineering**: Git-based data protection and local storage
- **Hardware Integration**: GPIO control, LED strips, and custom displays
  target_value: value
  unit: "unit"

````

## 📊 Analytics & Progress

### **Health Tracking**

- Weight monitoring
- Blood pressure tracking
- Sleep quality metrics
- Energy level tracking

### **Productivity Metrics**

- Task completion rates
- Streak tracking
- Time management analysis
- Goal progress monitoring

### **Peptide Protocol Analytics**

- Administration compliance
- Progress percentages
- Streak tracking
- Dose history export

## 🔒 Privacy & Security

### **Data Protection**

- All schedules excluded from Git by default
- Local data storage only
- No external data sharing
- Configurable privacy settings

### **Schedule Management**

```bash
# Your personal schedules are automatically protected:
config/schedule.yaml      # ❌ Gitignored
config/schedule2.yaml     # ❌ Gitignored
config/peptide_schedule.yaml # ❌ Gitignored

# Only sample files are public:
config/sample_schedule.yaml # ✅ Public (if created)
````

## 🚀 Deployment

### **Raspberry Pi Setup**

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up as service
sudo cp raspberry-pi-day-planner.service /etc/systemd/system/
sudo systemctl enable raspberry-pi-day-planner
sudo systemctl start raspberry-pi-day-planner
```

### **Docker Deployment**

```bash
# Build and run with Docker
docker-compose up -d

# Access web interface
open http://localhost:8080
```

## 🧪 Testing

### **Run Integration Tests**

```bash
python peptide_integration.py
```

### **Test Schedule Selector**

```bash
python schedule_selector.py
```

### **Run Unit Tests**

```bash
python -m pytest tests/
```

## 📈 Performance Features

### **Optimization**

- Background task processing
- Efficient memory management
- Minimal CPU usage
- Battery-optimized for Raspberry Pi

### **Scalability**

- Modular architecture
- Plugin system for extensions
- Configurable components
- Easy customization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🎯 Resume Highlights

This project demonstrates:

- **Advanced Python Development**: Complex scheduling algorithms, modular architecture
- **IoT Integration**: Raspberry Pi hardware integration, sensor management
- **Data Privacy**: Git-based privacy protection, local data storage
- **Healthcare Technology**: Specialized peptide protocol management
- **Web Development**: Flask-based web interface, real-time updates
- **System Administration**: Service management, Docker deployment
- **Testing & Quality**: Comprehensive test suite, integration testing

Perfect for showcasing full-stack development, IoT expertise, and healthcare technology experience.

---

**Built with ❤️ for productivity enthusiasts and biohackers**
