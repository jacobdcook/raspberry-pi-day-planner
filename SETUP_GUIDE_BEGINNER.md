# 🍓 Raspberry Pi Day Planner - SUPER SIMPLE Setup Guide

**For Complete Beginners - No Experience Required!**

---

## 📋 **What You Need (Hardware)**

✅ **Raspberry Pi 4** (4GB version)  
✅ **MicroSD Card** (32GB)  
✅ **Power Supply** (comes with Pi)  
✅ **HDMI Monitor** (your side monitor)  
✅ **USB Speakers**  
✅ **USB Keyboard & Mouse**  
✅ **USB Drive** (to copy files)  

---

## 🚀 **Step 1: First Time Setup**

### **1.1 Put SD Card in Pi**
- **Find the microSD slot** on your Raspberry Pi (it's on the bottom)
- **Insert your SD card** (it only goes in one way)
- **Make sure it clicks in**

### **1.2 Connect Everything**
- **HDMI cable** → Connect to your side monitor
- **USB speakers** → Plug into any USB port
- **Keyboard & mouse** → Plug into USB ports
- **Power supply** → Plug into Pi and wall outlet

### **1.3 Turn It On**
- **Press the power button** (if your case has one)
- **Or just plug in the power supply**
- **Wait 1-2 minutes** for it to start up

---

## 💻 **Step 2: First Boot Setup**

### **2.1 Initial Setup Screen**
When your Pi starts for the first time, you'll see a setup screen:

1. **Click "Next"** on the welcome screen
2. **Set your country** (United States, etc.)
3. **Create a password** (write this down!)
4. **Connect to WiFi** (if you have it)
5. **Click "Skip"** for software updates (we'll do this later)
6. **Click "Restart"**

### **2.2 After Restart**
- **Wait for desktop to load**
- **You should see a desktop** with icons

---

## 📁 **Step 3: Get the Day Planner Files**

### **3.1 Download Files to Your Computer**
1. **On your regular computer**, download the day planner files
2. **Put them on a USB drive**
3. **Make sure the folder is called** `raspberry-pi-day-planner`

### **3.2 Copy Files to Pi**
1. **Plug USB drive into your Pi**
2. **Open File Manager** (folder icon on desktop)
3. **Find your USB drive** in the left sidebar
4. **Right-click** on the `raspberry-pi-day-planner` folder
5. **Select "Copy"**
6. **Go to Desktop** (or Documents)
7. **Right-click empty space**
8. **Select "Paste"**

---

## ⚙️ **Step 4: Install the Day Planner**

### **4.1 Open Terminal**
1. **Press Ctrl + Alt + T** (opens terminal)
2. **Or click the terminal icon** on desktop

### **4.2 Navigate to Files**
```bash
# Type these commands one by one:
cd Desktop
cd raspberry-pi-day-planner
```

### **4.3 Run the Installer**
```bash
# Make installer work
chmod +x install.sh

# Run the installer
./install.sh
```

**What this does:**
- Installs Python programs
- Sets up the database
- Creates folders for data
- Sets up auto-start

---

## ⚡ **Step 5: Test It**

### **5.1 Start the Day Planner**
```bash
# In the terminal, type:
python main.py
```

**You should see:**
- A fullscreen window
- Clock display
- "Raspberry Pi Day Planner" title

### **5.2 Test the Buttons**
- **Press "Done"** → Should play a sound
- **Press "Snooze"** → Should play a sound
- **Press Escape** → Should close the app

---

## 🕐 **Step 6: Set Your Schedule**

### **6.1 Edit Your Schedule**
```bash
# In terminal, type:
nano config/schedule.yaml
```

### **6.2 Example Schedule**
Replace everything with this (7am-6pm PST schedule):

```yaml
morning_tasks:
  - title: "Take Supplements"
    time: "07:00"
    notes: "Vitamins and supplements"
    priority: 1
    audio_alert: true
    snooze_duration: 15

  - title: "Breakfast"
    time: "07:30"
    notes: "Eat breakfast"
    priority: 1
    audio_alert: true
    snooze_duration: 30

  - title: "Study Spanish"
    time: "08:00"
    notes: "30 minutes of Spanish practice"
    priority: 2
    audio_alert: true
    snooze_duration: 15

  - title: "Start Work"
    time: "09:00"
    notes: "Begin work day"
    priority: 1
    audio_alert: true
    snooze_duration: 10

  - title: "Morning Break"
    time: "10:30"
    notes: "Take a short break"
    priority: 2
    audio_alert: true
    snooze_duration: 15

afternoon_tasks:
  - title: "Lunch Break"
    time: "12:00"
    notes: "Lunch time"
    priority: 1
    audio_alert: true
    snooze_duration: 30

  - title: "CompTIA Study"
    time: "14:00"
    notes: "Study for CompTIA certification"
    priority: 1
    audio_alert: true
    snooze_duration: 30

  - title: "Afternoon Break"
    time: "15:30"
    notes: "Take a short break"
    priority: 2
    audio_alert: true
    snooze_duration: 15

  - title: "Bike Ride"
    time: "16:00"
    notes: "30 minute bike ride"
    priority: 2
    audio_alert: true
    snooze_duration: 15

  - title: "Wife Time"
    time: "17:00"
    notes: "Spend time with wife"
    priority: 1
    audio_alert: true
    snooze_duration: 30

  - title: "End Work Day"
    time: "18:00"
    notes: "Wrap up work for the day"
    priority: 1
    audio_alert: true
    snooze_duration: 10

settings:
  fullscreen: true
  default_volume: 0.7
  timezone: "America/Los_Angeles"
```

### **6.3 Save the File**
1. **Press Ctrl + X**
2. **Press Y** (to save)
3. **Press Enter** (to confirm filename)

---

## 🔄 **Step 7: Make It Start Automatically**

### **7.1 Enable Auto-Start**
```bash
# In terminal, type:
sudo systemctl enable raspberry-pi-day-planner
sudo systemctl start raspberry-pi-day-planner
```

### **7.2 Test Auto-Start**
```bash
# Restart your Pi
sudo reboot
```

**After restart:**
- Wait 1-2 minutes
- The day planner should start automatically
- You should see the fullscreen display

---

## 🌐 **Step 8: Web Dashboard (Optional)**

### **8.1 Find Your Pi's Address**
```bash
# In terminal, type:
hostname -I
```

**You'll see something like:** `192.168.1.100`

### **8.2 Access Web Dashboard**
1. **On any device** (phone, computer, tablet)
2. **Open web browser**
3. **Go to:** `http://192.168.1.100:8000`
4. **You'll see a dashboard** to control your day planner

---

## 🎯 **What You Have Now**

✅ **Day planner** that starts automatically  
✅ **Fullscreen display** on your side monitor  
✅ **Audio alerts** through speakers  
✅ **Web dashboard** to control from phone  
✅ **Customizable schedule**  
✅ **Auto-start** when Pi boots  

---

## 🔧 **Common Problems & Fixes**

### **"No module named..." error**
```bash
# Reinstall requirements
pip3 install -r requirements.txt
```

### **"Permission denied" error**
```bash
# Fix permissions
sudo chmod +x install.sh
```

### **Day planner won't start**
```bash
# Check if it's running
sudo systemctl status raspberry-pi-day-planner

# Restart it
sudo systemctl restart raspberry-pi-day-planner
```

### **No sound**
1. **Check speakers are plugged in**
2. **Check volume on speakers**
3. **Check Pi volume** (speaker icon on desktop)

### **Monitor not working**
1. **Check HDMI cable**
2. **Try different HDMI port**
3. **Check monitor power**

---

## 📞 **Need Help?**

### **Check if it's working:**
```bash
# Check service status
sudo systemctl status raspberry-pi-day-planner

# View recent logs
sudo journalctl -u raspberry-pi-day-planner -n 20
```

### **Restart everything:**
```bash
# Stop the service
sudo systemctl stop raspberry-pi-day-planner

# Start it again
sudo systemctl start raspberry-pi-day-planner
```

### **Complete reset:**
```bash
# Remove everything
sudo systemctl stop raspberry-pi-day-planner
sudo systemctl disable raspberry-pi-day-planner

# Reinstall
./install.sh
```

---

## 🎉 **You're Done!**

**Your Raspberry Pi Day Planner is now:**
- ✅ **Running automatically**
- ✅ **Displaying on your monitor**
- ✅ **Playing audio alerts**
- ✅ **Controllable from your phone**
- ✅ **Ready to remind you of tasks**

**Just unplug and replug your Pi anytime you want to use it!**

---

## 🔄 **Upgrading Your Case Later**

**Want a better case? No problem!**

1. **Turn off your Pi** (unplug power)
2. **Remove from old case**
3. **Put in new case**
4. **Turn back on**

**Everything will work exactly the same!** The case is just a shell.

**Recommended upgrades:**
- **Official Raspberry Pi Case** ($15) - Good quality
- **Argon ONE V2** ($30) - Aluminum, professional
- **FLIRC** ($25) - Aluminum, passive cooling

---

**That's it! You now have a working day planner! 🚀** 