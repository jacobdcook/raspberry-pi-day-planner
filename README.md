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

### 1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/raspberry-pi-day-planner.git
cd raspberry-pi-day-planner
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Set Up Your Schedule**

Create a `config/schedule.yaml` file with your personal schedule:

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

# Advanced Features
advanced_features:
  weather_check:
    enabled: true
    location: "New York"
    check_time: "07:00"

  system_monitor:
    enabled: true
    check_interval: 300 # 5 minutes
```

### 4. **Run the Schedule Selector**

```bash
python schedule_selector.py
```

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
    target_value: value
    unit: "unit"
```

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
```

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
