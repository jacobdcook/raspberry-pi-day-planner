# 🍓 Complete Raspberry Pi Setup Guide

A step-by-step guide to set up your Raspberry Pi Day Planner from scratch to finish.

## 📋 Prerequisites

### Hardware Requirements

**Essential Components:**

- Raspberry Pi 4 (4GB RAM recommended)
- MicroSD card (32GB+ Class 10)
- Power supply (5V/3A)
- HDMI cable and monitor (for initial setup)
- USB keyboard and mouse
- Ethernet cable or WiFi access

**Optional Hardware:**

- 3.5" LCD display (for dedicated display)
- Speaker system (for audio alerts)
- LED strip (for visual notifications)
- Push buttons (for manual controls)
- Case/enclosure for protection

### Software Requirements

- Raspberry Pi Imager (download from raspberrypi.com)
- SSH client (PuTTY for Windows, Terminal for Mac/Linux)
- Text editor (VS Code, nano, vim)

## 🚀 Step-by-Step Setup

### Step 1: Prepare Raspberry Pi OS

1. **Download Raspberry Pi Imager**

   - Go to https://www.raspberrypi.com/software/
   - Download for your operating system

2. **Flash the OS**

   - Insert microSD card into your computer
   - Open Raspberry Pi Imager
   - Click "Choose OS" → "Raspberry Pi OS (64-bit)"
   - Click "Choose Storage" → Select your microSD card
   - Click the gear icon (⚙️) to configure:
     - Set hostname: `dayplanner`
     - Enable SSH
     - Set username: `pi`
     - Set password: `your_password`
     - Configure WiFi (if using wireless)
   - Click "Write" and wait for completion

3. **Boot Raspberry Pi**
   - Insert microSD card into Pi
   - Connect power, HDMI, keyboard, mouse
   - Wait for first boot (may take 5-10 minutes)

### Step 2: Initial Configuration

1. **Connect via SSH** (recommended)

   ```bash
   ssh pi@raspberrypi.local
   # or ssh pi@YOUR_PI_IP_ADDRESS
   ```

2. **Update System**

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt autoremove -y
   ```

3. **Install Essential Packages**

   ```bash
   sudo apt install -y git python3 python3-pip python3-venv
   sudo apt install -y screen htop vim nano
   sudo apt install -y python3-pil python3-pil.imagetk
   ```

4. **Configure System**
   ```bash
   sudo raspi-config
   ```
   - **System Options** → **Password** → Set new password
   - **System Options** → **Hostname** → Set to `dayplanner`
   - **Interface Options** → **SSH** → Enable
   - **Interface Options** → **SPI** → Enable (for displays)
   - **Localization Options** → **Timezone** → Set your timezone
   - **Advanced Options** → **Expand Filesystem** → Yes

### Step 3: Install Day Planner

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
   python3 test_installation.py
   ```

### Step 4: Configure Your Schedule

1. **Create Personal Schedule**

   ```bash
   cp config/schedule.yaml config/schedule_personal.yaml
   nano config/schedule.yaml
   ```

2. **Edit Schedule File**

   ```yaml
   # Example schedule.yaml
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

     - title: "Take Supplements"
       time: "07:00"
       notes: "Vitamin D3, Fish Oil, Probiotic"
       priority: 1
       audio_alert: true
       snooze_duration: 10
       duration: 10

   afternoon_tasks:
     - title: "Lunch & Hydration"
       time: "12:00"
       notes: "Healthy meal with water"
       priority: 2
       audio_alert: true
       snooze_duration: 30
       duration: 30
   ```

### Step 5: Set Up Auto-Start

1. **Create System Service**

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

### Step 6: Audio Configuration

1. **Test Audio**

   ```bash
   speaker-test -t wav -c 2
   ```

2. **Configure Audio Output**

   ```bash
   sudo raspi-config
   # Navigate to: System Options → Audio → Force 3.5mm jack
   ```

3. **Test with Application**
   ```bash
   # Test audio alerts
   python3 -c "
   from modules.audio import AudioManager
   audio = AudioManager()
   audio.play_alert('Test alert sound')
   "
   ```

### Step 7: Display Configuration

1. **For HDMI Display**

   ```bash
   # Check display info
   vcgencmd get_mem gpu

   # Configure display rotation (if needed)
   sudo nano /boot/config.txt
   # Add: display_rotate=0 (or 90, 180, 270)
   ```

2. **For Dedicated LCD Display**

   ```bash
   # Install additional dependencies
   sudo apt install -y python3-pil python3-pil.imagetk

   # Test display
   python3 -c "
   from modules.display import DisplayManager
   display = DisplayManager()
   display.show_message('Display test')
   "
   ```

3. **For Touch Display**
   ```bash
   sudo apt install -y xinput-calibrator
   # Run calibration if needed
   ```

### Step 8: Network Configuration

1. **Set Static IP (Optional)**

   ```bash
   sudo nano /etc/dhcpcd.conf
   ```

   Add at the end:

   ```
   interface eth0
   static ip_address=192.168.1.100/24
   static routers=192.168.1.1
   static domain_name_servers=8.8.8.8
   ```

2. **Configure Firewall**

   ```bash
   sudo ufw allow 8080
   sudo ufw enable
   ```

3. **Test Web Interface**
   ```bash
   # From another device on network
   curl http://raspberrypi.local:8080
   # or http://YOUR_PI_IP:8080
   ```

### Step 9: Hardware Integration (Optional)

#### LED Strip Setup

1. **Install LED Library**

   ```bash
   pip install rpi.gpio neopixel
   ```

2. **Test LED Strip**
   ```bash
   python3 -c "
   import board
   import neopixel
   pixels = neopixel.NeoPixel(board.D18, 8)
   pixels.fill((255, 0, 0))  # Red
   import time
   time.sleep(2)
   pixels.fill((0, 0, 0))  # Off
   "
   ```

#### Button Integration

1. **Test GPIO Button**
   ```bash
   python3 -c "
   import RPi.GPIO as GPIO
   import time
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   print('Button ready on GPIO 17')
   while True:
       if GPIO.input(17) == False:
           print('Button pressed!')
           time.sleep(0.2)
   "
   ```

### Step 10: Monitoring & Maintenance

1. **System Monitoring**

   ```bash
   # Check system resources
   htop
   free -h
   df -h

   # Check temperature
   vcgencmd measure_temp

   # View logs
   sudo journalctl -u raspberry-pi-day-planner -f
   ```

2. **Update Application**

   ```bash
   cd /home/pi/raspberry-pi-day-planner
   git pull
   source dayplanner/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart raspberry-pi-day-planner
   ```

3. **Backup Configuration**
   ```bash
   # Backup your personal schedule
   cp config/schedule.yaml /home/pi/backup_schedule_$(date +%Y%m%d).yaml
   ```

## 🔧 Troubleshooting

### Common Issues

1. **Service won't start**:

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
   vcgencmd get_mem gpu
   sudo nano /boot/config.txt
   ```

4. **Network problems**:
   ```bash
   ping google.com
   curl http://localhost:8080
   sudo ufw allow 8080
   ```

### Performance Optimization

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
```

## 🎯 Next Steps

1. **Customize Your Schedule**: Edit `config/schedule.yaml` with your tasks
2. **Add Hardware**: Integrate LED strips, buttons, or custom displays
3. **Set Up Monitoring**: Configure log rotation and system monitoring
4. **Backup Strategy**: Set up regular backups of your configuration
5. **Network Security**: Configure firewall and access controls

## 📞 Support

- Check the main README.md for detailed troubleshooting
- Review logs: `sudo journalctl -u raspberry-pi-day-planner -f`
- Test components individually before full integration
- Keep backups of your configuration files

Your Raspberry Pi Day Planner is now ready to help you stay organized and accountable! 🚀
