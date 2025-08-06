# 📋 Setup Guide

## Quick Setup for Your Schedule

### Step 1: Create Your Schedule File

After cloning the repository, create a `config/schedule.yaml` file with your personal schedule:

```yaml
# Your Personal Schedule Configuration
settings:
  timezone: "America/New_York" # Change to your timezone
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

  - title: "Lunch Break"
    time: "12:00"
    notes: "Take a break and eat lunch"
    priority: 1
    audio_alert: true
    snooze_duration: 15
    duration: 60

  - title: "Evening Routine"
    time: "18:00"
    notes: "Review day and plan tomorrow"
    priority: 1
    audio_alert: true
    snooze_duration: 10
    duration: 45

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

  - title: "Grocery Shopping"
    day: "Saturday"
    time: "14:00"
    notes: "Buy groceries for the week"
    priority: 2
    audio_alert: true
    snooze_duration: 10
    duration: 90

# Health Metrics (Optional)
health_metrics:
  - title: "Morning Weight Check"
    time: "07:30"
    metric_type: "weight"
    target_value: 70.0
    unit: "kg"
    priority: 2
    audio_alert: false

  - title: "Evening Blood Pressure"
    time: "20:00"
    metric_type: "blood_pressure"
    target_value: "120/80"
    unit: "mmHg"
    priority: 1
    audio_alert: true

# Advanced Features (Optional)
advanced_features:
  weather_check:
    enabled: true
    location: "New York" # Change to your city
    check_time: "07:00"

  system_monitor:
    enabled: true
    check_interval: 300 # 5 minutes

  backup_schedule:
    enabled: true
    backup_time: "23:00"
    retention_days: 7

# Display Settings
display_settings:
  brightness: 0.7
  contrast: 0.8
  font_size: "medium"
  show_weather: true
  show_time: true
  show_next_task: true

# Audio Settings
audio_settings:
  volume: 0.8
  alert_sound: "beep"
  snooze_sound: "gentle_reminder"
  enable_voice_alerts: false

# Web Interface Settings
web_settings:
  theme: "dark"
  auto_refresh: true
  refresh_interval: 30
  enable_remote_access: false
```

### Step 2: Customize Your Schedule

**Task Fields Explained:**

- `title`: Name of your task
- `time`: When the task should occur (24-hour format)
- `notes`: Description or instructions
- `priority`: 1 (High), 2 (Medium), 3 (Low)
- `audio_alert`: Whether to play a sound
- `snooze_duration`: Minutes to wait before reminder
- `duration`: How long the task takes

**Priority Colors:**

- 🔴 Priority 1: High importance (Red)
- 🟡 Priority 2: Medium importance (Orange)
- 🟢 Priority 3: Low importance (Green)

### Step 3: Run the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Choose your schedule
python schedule_selector.py

# Start the application
python main.py
```

### Step 4: Access Web Dashboard

Open your browser and go to:

```
http://your-raspberry-pi-ip:8080
```

## 🔒 Privacy Protection

Your `config/schedule.yaml` file is automatically excluded from Git to protect your privacy. Only you can see your personal schedule.



## 🎯 Tips for Success

1. **Start Simple**: Begin with 3-5 daily tasks
2. **Be Realistic**: Don't over-schedule yourself
3. **Use Priorities**: Mark important tasks as Priority 1
4. **Test Audio**: Make sure your speakers work
5. **Check Timezone**: Set the correct timezone for your location

## 🆘 Need Help?

- Check the main README.md for detailed documentation
- Run `python test_installation.py` to test the system
- Use `python schedule_selector.py` to switch schedules

---

**Your schedule is private and secure! 🛡️**
