# Raspberry Pi Day Planner 🚀

A comprehensive, intelligent day planning system designed for Raspberry Pi with advanced features for productivity, health tracking, and personal development.

## ✨ **Latest Features (Phase 5 - Advanced UI/UX)**

### 🎨 **Dynamic Theme Support**
- **Light/Dark Mode Toggle**: Press `T` to switch between themes instantly
- **Professional Color Palettes**: Carefully designed themes for optimal readability
- **Automatic Color Adaptation**: All UI elements adapt to current theme
- **Theme Persistence**: Current theme displayed in instructions

### 📱 **Fully Responsive UI Layout**
- **Monitor Detection**: Automatically detects and uses full monitor size
- **Responsive Font Sizing**: Font sizes scale based on screen width
- **Adaptive UI Elements**: All buttons, text, and layouts use screen ratios
- **Cross-Platform Compatibility**: Works on any monitor size (tested on 2293x960)

## 🏗️ **Complete Feature Overview**

### **Phase 1: Persistent Data & Analytics System** 📊
- **Daily Summary Tracker**: Auto-save every 24h with completion metrics
- **Rolling 7-Day Burn Chart**: Visual progress tracking with completion rates
- **Focus Analytics**: Track streaks, missed days, and productivity patterns

### **Phase 2: Intelligent Task Flow & Adaptation** ⏰
- **Task Timer with Voice Alerts**: Countdown timers with ElevenLabs voice synthesis
- **Adaptive Time Adjustment**: Smart time redistribution for missed tasks
- **Floating Alerts**: Real-time notifications for schedule adjustments

### **Phase 3: Backlog & Redemption System** 🔄
- **Incomplete Task Backlog**: Track and manage overdue tasks
- **Redemption System**: Complete missed tasks for partial credit
- **Streak Rewards**: Gamified completion tracking with badges

### **Phase 4: Voice + Emotional Feedback** 🎤
- **ElevenLabs Voice Assistant**: High-quality voice synthesis for task announcements
- **Encouragement System**: Voice prompts for motivation and progress
- **Mood Tracking**: Daily mood correlation with task performance
- **Voice Settings**: Customizable voice selection and configuration

### **Phase 5: Advanced UI / UX** 🎨
- **Dynamic Theme Support**: Light/dark mode with professional color palettes
- **Fully Responsive Layout**: Scales perfectly on any monitor size
- **Modern UI Design**: Clean, intuitive interface with responsive elements

## 🚀 **Quick Start Options**

### **Option 1: Windows Test Environment** (Recommended for Testing)
```bash
# Install dependencies
pip install -r requirements.txt

# Run Windows GUI
python windows_test.py

# Or run Pi simulation
python pi_simulation.py
```

### **Option 2: Pi Simulation (Visual Preview)**
```bash
# See exactly how your Pi will look and behave
python pi_simulation.py

# Controls:
# - SPACE: Simulate task notification
# - T: Toggle theme (light/dark)
# - Mouse: Click buttons and interact
# - ESC: Exit simulation
```

### **Option 3: Complete Raspberry Pi Setup**
See [RASPBERRY_PI_SETUP_GUIDE.md](RASPBERRY_PI_SETUP_GUIDE.md) for full hardware setup.

## 🎯 **Key Features**

### **Smart Task Management**
- **Catch-up System**: Automatically consolidates missed morning tasks
- **Individual Task Control**: Complete or skip individual tasks in catch-up blocks
- **Pagination**: Handle large numbers of tasks with intuitive navigation
- **Bulk Actions**: "ALL COMPLETE", "DONE MARKED", "ALL SKIP" for efficient management

### **Voice Integration**
- **ElevenLabs Integration**: High-quality voice synthesis
- **Task Announcements**: "Next up: [task title]" with full descriptions
- **Encouragement**: Voice prompts for motivation
- **Voice Settings**: Customizable voice selection

### **Advanced Analytics**
- **Burn Charts**: Visual 7-day progress tracking
- **Streak Tracking**: Daily completion streaks with rewards
- **Mood Correlation**: Track mood vs. productivity
- **Export Functionality**: Detailed progress reports

### **Responsive Design**
- **Theme System**: Professional light/dark themes
- **Screen Adaptation**: Works on any monitor size
- **Responsive Typography**: Fonts scale with screen size
- **Touch-Friendly**: Optimized for touch interfaces

## 📋 **Schedule Management**

### **Personal Schedule** (Gitignored for Privacy)
- `config/schedule.yaml`: Your personal schedule (not tracked by Git)
- `config/peptide_schedule.yaml`: BPC-157 + TB-500 dosing protocol
- Automatic schedule loading with fallback to sample

### **Sample Schedule** (Public)
- `config/sample_schedule.yaml`: Example schedule for GitHub
- Perfect for resume showcasing and public repositories

## 🛠️ **Technical Stack**

### **Core Technologies**
- **Python 3.9+**: Main application logic
- **Pygame**: Pi simulation and display
- **Tkinter**: Windows GUI interface
- **ElevenLabs**: Voice synthesis
- **SQLite**: Local data storage
- **YAML**: Configuration files

### **Dependencies**
```bash
# Core
PyYAML>=6.0, APScheduler>=3.10.1, pygame>=2.5.0

# Voice & Audio
elevenlabs>=0.2.26, python-dotenv>=1.0.0

# Web API (optional)
fastapi>=0.68.0, uvicorn>=0.15.0

# Utilities
watchdog>=2.1.0, colorama>=0.4.4
```

## 🎮 **Simulation Features**

### **Visual Pi Preview**
- **Full-Screen Display**: Exactly like Pi with attached monitor
- **Responsive UI**: Adapts to any screen size
- **Theme Support**: Test light/dark modes
- **Voice Integration**: Test voice announcements
- **Interactive Elements**: Click buttons, navigate menus

### **Real-Time Testing**
- **Task Notifications**: Simulate task alerts
- **Catch-up Scenarios**: Test missed task handling
- **Voice Feedback**: Test ElevenLabs integration
- **Analytics**: View progress charts and stats

## 📊 **Analytics & Progress Tracking**

### **Daily Metrics**
- **Completion Rates**: Track daily task completion
- **Streak Tracking**: Monitor consistency
- **Mood Correlation**: Link mood to productivity
- **Export Reports**: Detailed progress analysis

### **Visual Analytics**
- **Burn Charts**: 7-day completion visualization
- **Progress Bars**: Real-time completion tracking
- **Streak Rewards**: Gamified motivation system

## 🔧 **Configuration**

### **Voice Settings**
```python
# elevenlabs_config.py
ELEVENLABS_API_KEY = "your_api_key"
ELEVENLABS_VOICE_ID = "Charlie"  # Male voice
```

### **Theme Configuration**
- **Dark Theme**: Professional dark interface
- **Light Theme**: Clean light interface
- **Automatic Adaptation**: All elements adapt to theme

## 🚀 **Resume Highlights**

### **Technical Achievements**
- **Full-Stack Development**: Python, Pygame, Tkinter, SQLite
- **Voice Integration**: ElevenLabs API integration
- **Responsive Design**: Cross-platform UI adaptation
- **Data Analytics**: Progress tracking and visualization
- **IoT Integration**: Raspberry Pi hardware integration

### **Project Features**
- **Multi-Platform**: Windows testing + Raspberry Pi deployment
- **Voice Assistant**: AI-powered task announcements
- **Smart Analytics**: Intelligent progress tracking
- **Modern UI**: Professional responsive design
- **Privacy-First**: Personal data protection with Gitignore

## 📚 **Documentation**

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)**: Quick setup guide
- **[RASPBERRY_PI_SETUP_GUIDE.md](RASPBERRY_PI_SETUP_GUIDE.md)**: Complete Pi setup
- **[PHASE_2_SUMMARY.md](PHASE_2_SUMMARY.md)**: Intelligent task flow details
- **[PHASE_3_SUMMARY.md](PHASE_3_SUMMARY.md)**: Backlog system details

## 🤝 **Contributing**

This project is designed for personal use but includes sample schedules for public showcasing. The personal schedule files are gitignored for privacy.

## 📄 **License**

Personal use project with sample schedules available for public viewing.

---

**Ready to transform your productivity with intelligent task management, voice assistance, and responsive design!** 🚀 