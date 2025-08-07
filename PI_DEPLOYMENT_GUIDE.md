# 🍓 Raspberry Pi Deployment Guide

Complete guide for deploying the Raspberry Pi Day Planner on actual Pi hardware.

## 📋 Prerequisites

### Hardware Requirements
- **Raspberry Pi 4** (4GB RAM recommended, 2GB minimum)
- **MicroSD card** (32GB+ Class 10)
- **Power supply** (5V/3A for Pi 4)
- **HDMI cable and monitor** (for initial setup)
- **USB keyboard and mouse** (for initial setup)
- **Ethernet cable or WiFi access**

### Optional Hardware
- **3.5" LCD display** (for dedicated display)
- **Speaker system** (for audio alerts)
- **LED strip** (for visual notifications)
- **Push buttons** (for manual controls)
- **Case/enclosure** (for protection)

## 🚀 Quick Deployment

### Step 1: Flash Raspberry Pi OS

1. **Download Raspberry Pi Imager**
   ```bash
   # Download from https://www.raspberrypi.com/software/
   ```

2. **Flash the OS**
   - Open Raspberry Pi Imager
   - Choose OS: "Raspberry Pi OS (64-bit)"
   - Choose Storage: Your microSD card
   - Click gear icon (⚙️) to configure:
     - Hostname: `dayplanner`
     - Enable SSH
     - Username: `pi`
     - Password: `your_secure_password`
     - Configure WiFi (if using wireless)
   - Click "Write" and wait

### Step 2: Initial Pi Setup

1. **Boot and Connect**
   ```bash
   # Insert microSD card and power on Pi
   # Wait for first boot (5-10 minutes)
   ```

2. **Connect via SSH** (recommended)
   ```bash
   ssh pi@raspberrypi.local
   # or ssh pi@YOUR_PI_IP_ADDRESS
   ```

3. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt autoremove -y
   ```

### Step 3: Install Dependencies

1. **Install System Packages**
   ```bash
   sudo apt install -y git python3 python3-pip python3-venv
   sudo apt install -y screen htop vim nano
   sudo apt install -y python3-pil python3-pil.imagetk
   sudo apt install -y alsa-utils pulseaudio
   ```

2. **Configure Audio**
   ```bash
   sudo raspi-config
   # Navigate to: System Options → Audio → Force 3.5mm jack
   ```

3. **Configure Display**
   ```bash
   sudo raspi-config
   # Navigate to: Display Options → Screen Blanking → Disable
   ```

### Step 4: Install Day Planner

1. **Clone Repository**
   ```bash
   cd /home/pi
   git clone https://github.com/jacobdcook/raspberry-pi-day-planner.git
   cd raspberry-pi-day-planner
   ```

2. **Set Up Python Environment**
   ```bash
   python3 -m venv dayplanner
   source dayplanner/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Test Installation**
   ```bash
   python3 test_pi_hardware.py
   ```

### Step 5: Configure Your Schedule

1. **Create Personal Schedule**
   ```bash
   cp config/schedule.yaml config/schedule_personal.yaml
   nano config/schedule.yaml
   ```

2. **Example Schedule**
   ```yaml
   settings:
     timezone: "America/New_York"
     display_timeout: 30
     audio_enabled: true
     web_interface_enabled: true
     web_port: 8080

   morning_tasks:
     - title: "Wake Up & Hydrate"
       time: "06:45"
       notes: "Drink 16 oz water with lemon"
       priority: 1
       audio_alert: true
       snooze_duration: 5
       duration: 15
   ```

### Step 6: Set Up Auto-Start

1. **Install Service**
   ```bash
   sudo cp raspberry-pi-day-planner.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable raspberry-pi-day-planner
   ```

2. **Test Service**
   ```bash
   sudo systemctl start raspberry-pi-day-planner
   sudo systemctl status raspberry-pi-day-planner
   ```

3. **View Logs**
   ```bash
   sudo journalctl -u raspberry-pi-day-planner -f
   ```

## 🔧 Pi-Specific Optimizations

### Performance Tuning

1. **Overclock Settings** (optional)
   ```bash
   sudo raspi-config
   # Navigate to: Performance Options → Overclock
   # Choose: Pi 4 2000MHz
   ```

2. **Memory Split**
   ```bash
   sudo raspi-config
   # Navigate to: Advanced Options → Memory Split
   # Set to: 256 (for 4GB Pi)
   ```

3. **GPU Memory**
   ```bash
   # Edit /boot/config.txt
   sudo nano /boot/config.txt
   # Add: gpu_mem=256
   ```

### Audio Configuration

1. **Test Audio**
   ```bash
   speaker-test -t wav -c 2
   ```

2. **Set Default Volume**
   ```bash
   amixer set Master 80%
   amixer set PCM 80%
   ```

3. **Configure ALSA**
   ```bash
   # Edit /etc/asound.conf
   sudo nano /etc/asound.conf
   ```
   ```conf
   pcm.!default {
       type hw
       card 0
   }
   ctl.!default {
       type hw
       card 0
   }
   ```

### Display Configuration

1. **Disable Screen Blanking**
   ```bash
   # Edit /boot/config.txt
   sudo nano /boot/config.txt
   # Add:
   # hdmi_blanking=0
   # hdmi_ignore_cec=1
   ```

2. **Set Resolution**
   ```bash
   # Edit /boot/config.txt
   sudo nano /boot/config.txt
   # Add: hdmi_group=1
   # Add: hdmi_mode=16  # for 1080p
   ```

## 🧪 Testing and Validation

### Hardware Detection Test
```bash
python3 test_pi_hardware.py
```

### Audio Test
```bash
python3 -c "
from modules.audio import AudioManager
from modules.pi_detection import PiDetector
detector = PiDetector()
audio = AudioManager(pi_detector=detector)
audio.play_alert()
print('Audio test completed')
"
```

### Display Test
```bash
python3 -c "
from modules.display import DisplayManager
from modules.audio import AudioManager
from modules.logger import EventLogger
from modules.pi_detection import PiDetector

detector = PiDetector()
audio = AudioManager(pi_detector=detector)
logger = EventLogger()
display = DisplayManager(audio, logger, detector)
print('Display test completed')
"
```

### Full Application Test
```bash
python3 pi_startup.py
```

## 🔍 Troubleshooting

### Common Issues

1. **No Audio**
   ```bash
   # Check audio device
   aplay -l
   
   # Test audio
   speaker-test -t wav -c 2
   
   # Check volume
   amixer get Master
   ```

2. **Display Issues**
   ```bash
   # Check display
   xrandr
   
   # Check framebuffer
   cat /proc/fb
   ```

3. **Performance Issues**
   ```bash
   # Check CPU temperature
   vcgencmd measure_temp
   
   # Check memory usage
   free -h
   
   # Check disk usage
   df -h
   ```

4. **Service Won't Start**
   ```bash
   # Check service status
   sudo systemctl status raspberry-pi-day-planner
   
   # Check logs
   sudo journalctl -u raspberry-pi-day-planner -n 50
   
   # Test manually
   cd /home/pi/raspberry-pi-day-planner
   source dayplanner/bin/activate
   python3 pi_startup.py
   ```

### Performance Monitoring

1. **System Monitor**
   ```bash
   # Install htop
   sudo apt install htop
   htop
   ```

2. **Temperature Monitor**
   ```bash
   # Create temperature script
   cat > /home/pi/temp_monitor.sh << 'EOF'
   #!/bin/bash
   while true; do
       temp=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
       echo "$(date): $temp"
       sleep 60
   done
   EOF
   chmod +x /home/pi/temp_monitor.sh
   ```

3. **Memory Monitor**
   ```bash
   # Create memory script
   cat > /home/pi/memory_monitor.sh << 'EOF'
   #!/bin/bash
   while true; do
       mem=$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
       echo "$(date): Memory usage: $mem"
       sleep 60
   done
   EOF
   chmod +x /home/pi/memory_monitor.sh
   ```

## 🔄 Updates and Maintenance

### Updating the Application
```bash
cd /home/pi/raspberry-pi-day-planner
git pull
source dayplanner/bin/activate
pip install -r requirements.txt
sudo systemctl restart raspberry-pi-day-planner
```

### Backup Configuration
```bash
# Backup schedule
cp config/schedule.yaml /home/pi/backup_schedule_$(date +%Y%m%d).yaml

# Backup data
cp -r data /home/pi/backup_data_$(date +%Y%m%d)
```

### System Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

## 📊 Monitoring and Analytics

### Web Interface
- Access: `http://YOUR_PI_IP:8080`
- Features: Task management, analytics, configuration

### Log Files
```bash
# Application logs
sudo journalctl -u raspberry-pi-day-planner -f

# System logs
sudo journalctl -f

# Audio logs
dmesg | grep -i audio
```

### Health Checks
```bash
# Run health check
python3 -c "
from modules.pi_detection import PiDetector
detector = PiDetector()
health = detector.check_pi_health()
for key, value in health.items():
    print(f'{key}: {value}')
"
```

## 🎯 Best Practices

### Performance
- Use Class 10 microSD cards
- Keep Pi in well-ventilated case
- Monitor temperature regularly
- Use wired Ethernet when possible

### Reliability
- Use UPS for power protection
- Regular backups of configuration
- Monitor disk space
- Test audio/display regularly

### Security
- Change default password
- Use SSH keys instead of passwords
- Keep system updated
- Monitor for unauthorized access

## 🆘 Support

### Getting Help
1. Check logs: `sudo journalctl -u raspberry-pi-day-planner -f`
2. Run tests: `python3 test_pi_hardware.py`
3. Check hardware: `python3 pi_startup.py`
4. Review configuration: `nano config/schedule.yaml`

### Emergency Recovery
```bash
# Stop service
sudo systemctl stop raspberry-pi-day-planner

# Run in debug mode
cd /home/pi/raspberry-pi-day-planner
source dayplanner/bin/activate
python3 main.py --debug

# Restart service
sudo systemctl start raspberry-pi-day-planner
```

---

**🎉 Congratulations!** Your Raspberry Pi Day Planner is now ready for production use.

For more information, see the main [README.md](README.md) and [RASPBERRY_PI_SETUP_GUIDE.md](RASPBERRY_PI_SETUP_GUIDE.md).
