#!/usr/bin/env python3
"""
Raspberry Pi Day Planner - Main Entry Point

This application runs on boot and provides a fullscreen day planner/reminder system
with HDMI display and audio alerts. It loads a schedule from YAML configuration,
schedules reminders using APScheduler, and displays them in a Tkinter UI.

Enhanced features include:
- Configuration file watching and live reloading
- Web API for remote control and monitoring
- Analytics and progress tracking
- System monitoring and failure recovery
- Comprehensive logging and error handling

Author: Raspberry Pi Day Planner
License: MIT
"""

import sys
import os
import signal
import logging
import argparse
from pathlib import Path

# Add the project root to Python path for module imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.loader import ScheduleLoader
from modules.scheduler import TaskScheduler
from modules.display import DisplayManager
from modules.audio import AudioManager
from modules.logger import EventLogger
from modules.utils import setup_logging, handle_exit
from modules.config_watcher import ConfigWatcher
from modules.web_api import WebAPI
from modules.analytics import Analytics
from modules.monitor import SystemMonitor


class DayPlanner:
    """
    Main application class that coordinates all components of the day planner.
    
    This class initializes and manages:
    - Schedule loading and validation
    - Task scheduling with APScheduler
    - Display management with Tkinter
    - Audio management with pygame
    - Event logging with SQLite
    - Configuration watching and live reloading
    - Web API for remote control
    - Analytics and progress tracking
    - System monitoring and failure recovery
    """
    
    def __init__(self, args=None):
        """Initialize the day planner application and all its components."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Raspberry Pi Day Planner...")
        
        # Parse command line arguments
        self.args = args or self._parse_arguments()
        
        # Initialize components
        self.schedule_loader = None
        self.task_scheduler = None
        self.display_manager = None
        self.audio_manager = None
        self.event_logger = None
        self.config_watcher = None
        self.web_api = None
        self.analytics = None
        self.system_monitor = None
        
        # Flag to track if application is running
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _parse_arguments(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='Raspberry Pi Day Planner')
        parser.add_argument('--debug', action='store_true', 
                          help='Enable debug logging')
        parser.add_argument('--no-web', action='store_true',
                          help='Disable web API')
        parser.add_argument('--no-monitor', action='store_true',
                          help='Disable system monitoring')
        parser.add_argument('--web-port', type=int, default=8000,
                          help='Web API port (default: 8000)')
        parser.add_argument('--config', type=str,
                          help='Path to configuration file')
        return parser.parse_args()
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
    
    def initialize(self):
        """Initialize all components of the day planner."""
        try:
            # Setup logging first
            log_level = "DEBUG" if self.args.debug else "INFO"
            setup_logging(log_level=log_level)
            self.logger.info("Logging initialized")
            
            # Initialize event logger
            self.event_logger = EventLogger()
            self.logger.info("Event logger initialized")
            
            # Load and validate schedule
            config_path = self.args.config if self.args.config else None
            self.schedule_loader = ScheduleLoader(config_path=config_path)
            schedule = self.schedule_loader.load_schedule()
            self.logger.info(f"Loaded schedule with {len(schedule)} tasks")
            
            # Initialize audio manager
            self.audio_manager = AudioManager()
            self.logger.info("Audio manager initialized")
            
            # Initialize display manager
            self.display_manager = DisplayManager(
                audio_manager=self.audio_manager,
                event_logger=self.event_logger
            )
            self.logger.info("Display manager initialized")
            
            # Initialize task scheduler
            self.task_scheduler = TaskScheduler(
                schedule=schedule,
                display_manager=self.display_manager,
                event_logger=self.event_logger
            )
            self.logger.info("Task scheduler initialized")
            
            # Initialize configuration watcher
            if not self.args.no_web:
                self.config_watcher = ConfigWatcher(
                    config_path=config_path
                )
                self.config_watcher.add_reload_callback(self._on_config_reload)
                self.logger.info("Configuration watcher initialized")
            
            # Initialize analytics
            self.analytics = Analytics(self.event_logger)
            self.logger.info("Analytics initialized")
            
            # Initialize system monitor
            if not self.args.no_monitor:
                self.system_monitor = SystemMonitor(
                    audio_manager=self.audio_manager,
                    display_manager=self.display_manager,
                    notification_callback=self._send_notification
                )
                self.logger.info("System monitor initialized")
            
            # Initialize web API
            if not self.args.no_web:
                self.web_api = WebAPI(
                    scheduler=self.task_scheduler,
                    display_manager=self.display_manager,
                    audio_manager=self.audio_manager,
                    event_logger=self.event_logger,
                    config_watcher=self.config_watcher
                )
                self.logger.info("Web API initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize day planner: {e}")
            return False
    
    def _on_config_reload(self, new_config):
        """Handle configuration reload events."""
        try:
            self.logger.info("Configuration reloaded, updating scheduler...")
            
            # Update task scheduler with new configuration
            if self.task_scheduler:
                self.task_scheduler.update_schedule(new_config)
            
            # Update display manager settings
            if self.display_manager and 'settings' in new_config:
                self.display_manager.update_settings(new_config['settings'])
            
            # Update audio manager settings
            if self.audio_manager and 'settings' in new_config:
                settings = new_config['settings']
                if 'default_volume' in settings:
                    self.audio_manager.set_volume(settings['default_volume'])
            
            self.logger.info("Configuration update completed")
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
    
    def _send_notification(self, title, message):
        """Send system notification."""
        try:
            # Try to send desktop notification
            import subprocess
            subprocess.run(['notify-send', title, message], 
                         capture_output=True, timeout=5)
        except Exception as e:
            self.logger.warning(f"Could not send notification: {e}")
    
    def start(self):
        """Start the day planner application."""
        if not self.initialize():
            self.logger.error("Failed to initialize, exiting...")
            return False
        
        try:
            self.logger.info("Starting day planner...")
            self.running = True
            
            # Start configuration watcher
            if self.config_watcher:
                self.config_watcher.start_watching()
                self.logger.info("Configuration watcher started")
            
            # Start system monitoring
            if self.system_monitor:
                self.system_monitor.start_monitoring()
                self.logger.info("System monitoring started")
            
            # Start web API
            if self.web_api:
                self.web_api.start(port=self.args.web_port)
                self.logger.info(f"Web API started on port {self.args.web_port}")
            
            # Start the task scheduler
            self.task_scheduler.start()
            self.logger.info("Task scheduler started")
            
            # Generate initial analytics report
            if self.analytics:
                self.analytics.generate_daily_report()
                self.logger.info("Initial analytics report generated")
            
            # Start the display manager (this will block until closed)
            self.display_manager.start()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
        finally:
            self.shutdown()
        
        return False
    
    def shutdown(self):
        """Shutdown the day planner application gracefully."""
        if not self.running:
            return
        
        self.logger.info("Shutting down day planner...")
        self.running = False
        
        try:
            # Stop configuration watcher
            if self.config_watcher:
                self.config_watcher.stop_watching()
                self.logger.info("Configuration watcher stopped")
            
            # Stop system monitoring
            if self.system_monitor:
                self.system_monitor.stop_monitoring()
                self.logger.info("System monitoring stopped")
            
            # Stop web API
            if self.web_api:
                self.web_api.stop()
                self.logger.info("Web API stopped")
            
            # Stop task scheduler
            if self.task_scheduler:
                self.task_scheduler.stop()
                self.logger.info("Task scheduler stopped")
            
            # Close display manager
            if self.display_manager:
                self.display_manager.close()
                self.logger.info("Display manager closed")
            
            # Close audio manager
            if self.audio_manager:
                self.audio_manager.close()
                self.logger.info("Audio manager closed")
            
            # Close event logger
            if self.event_logger:
                self.event_logger.close()
                self.logger.info("Event logger closed")
            
            # Generate final analytics report
            if self.analytics:
                self.analytics.generate_daily_report()
                self.logger.info("Final analytics report generated")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        
        self.logger.info("Day planner shutdown complete")


def main():
    """Main entry point for the application."""
    # Handle exit signals
    handle_exit()
    
    # Create and start the day planner
    planner = DayPlanner()
    
    try:
        success = planner.start()
        if not success:
            sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 