#!/usr/bin/env python3
"""
Simple Web Server for Raspberry Pi Day Planner

This script runs just the web API without the problematic display manager.
Access the web interface at http://YOUR_PI_IP:8000
"""

import uvicorn
from modules.web_api import WebAPI
from modules.scheduler import TaskScheduler
from modules.display import DisplayManager
from modules.audio import AudioManager
from modules.logger import EventLogger
from modules.config_watcher import ConfigWatcher
from modules.loader import ScheduleLoader

def main():
    print("🍓 Starting Raspberry Pi Day Planner Web Server...")
    print("=" * 50)
    
    try:
        # Initialize components
        print("📋 Loading schedule...")
        schedule_loader = ScheduleLoader()
        schedule = schedule_loader.load_schedule()
        print(f"✅ Loaded {len(schedule)} tasks")
        
        print("🔧 Initializing components...")
        event_logger = EventLogger()
        audio_manager = AudioManager()
        display_manager = DisplayManager(audio_manager, event_logger, None)
        task_scheduler = TaskScheduler(schedule, display_manager, event_logger)
        config_watcher = ConfigWatcher()
        
        web_api = WebAPI(task_scheduler, display_manager, audio_manager, event_logger, config_watcher)
        
        print("✅ Web server starting on http://0.0.0.0:8000")
        print("🌐 Access from any device: http://192.168.1.110:8000")
        print("📱 Works on phones, tablets, computers")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 50)
        
        uvicorn.run(web_api.app, host='0.0.0.0', port=8000)
        
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        return False

if __name__ == '__main__':
    main()
