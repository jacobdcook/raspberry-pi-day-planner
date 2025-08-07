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
from modules.peptide_scheduler import PeptideScheduler
from modules.pi_detection import pi_detector


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
        
        # Detect and configure for Pi hardware
        self.pi_detector = pi_detector
        self.logger.info(f"Hardware detected: {'Pi' if self.pi_detector.is_raspberry_pi() else 'Simulation'}")
        if self.pi_detector.is_raspberry_pi():
            self.pi_detector.optimize_for_pi()
        
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
        self.peptide_scheduler = None
        
        # Enhanced task management
        self.today_tasks = []
        self.skipped_tasks = set()
        self.completed_tasks = set()
        
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
            
            # Initialize peptide scheduler
            config_dir = Path(__file__).parent / "config"
            self.peptide_scheduler = PeptideScheduler(config_dir=str(config_dir))
            
            # Load personal schedule
            if self.peptide_scheduler.select_schedule("personal"):
                self.logger.info("✅ Personal schedule loaded successfully!")
            elif self.peptide_scheduler.select_schedule("sample"):
                self.logger.info("⚠️ Using sample schedule (personal not found)")
            else:
                self.logger.warning("⚠️ No schedules found")
            
            # Load peptide schedule
            if self.peptide_scheduler.load_peptide_schedule():
                self.logger.info("✅ Peptide schedule loaded successfully!")
            else:
                self.logger.info("⚠️ No peptide schedule found")
            
            # Load and validate schedule using traditional loader as fallback
            config_path = self.args.config if self.args.config else None
            self.schedule_loader = ScheduleLoader(config_path=config_path)
            schedule = self.schedule_loader.load_schedule()
            self.logger.info(f"Loaded schedule with {len(schedule)} tasks")
            
            # Load today's tasks with enhanced functionality
            self._load_today_tasks()
            
            # Initialize audio manager
            self.audio_manager = AudioManager(pi_detector=self.pi_detector)
            self.logger.info("Audio manager initialized")
            
            # Initialize display manager
            self.display_manager = DisplayManager(
                audio_manager=self.audio_manager,
                event_logger=self.event_logger,
                pi_detector=self.pi_detector
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
    
    def _load_today_tasks(self):
        """Load today's tasks with enhanced functionality including catch-up tasks."""
        try:
            if self.peptide_scheduler and self.peptide_scheduler.main_schedule:
                # Get all task sections
                all_tasks = []
                
                # Check for different task section names
                task_sections = ["tasks", "morning_tasks", "afternoon_tasks", "evening_tasks", "daily_tasks"]
                
                for section in task_sections:
                    if section in self.peptide_scheduler.main_schedule:
                        section_tasks = self.peptide_scheduler.main_schedule[section]
                        if isinstance(section_tasks, list):
                            all_tasks.extend(section_tasks)
                
                # Filter tasks for today (or show all if no date specified)
                today = datetime.now().strftime("%Y-%m-%d")
                
                self.today_tasks = []
                for task in all_tasks:
                    # If task has a date, check if it's today
                    if "date" in task:
                        if task.get("date") == today:
                            self.today_tasks.append(task)
                    else:
                        # If no date specified, assume it's a daily task
                        self.today_tasks.append(task)
                
                # Sort tasks by time
                self.today_tasks.sort(key=lambda x: x.get("time", "00:00"))
                
                # Create catch-up tasks for missed time blocks
                self.today_tasks = self._create_catch_up_tasks(self.today_tasks)
                
                self.logger.info(f"Loaded {len(self.today_tasks)} tasks for today")
            else:
                self.logger.warning("No schedule loaded")
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
    
    def _create_catch_up_tasks(self, tasks):
        """Create consolidated catch-up tasks for missed time blocks."""
        from datetime import datetime
        
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_str = f"{current_hour:02d}:{current_minute:02d}"
        
        # Define time blocks
        time_blocks = {
            "morning": {"start": "06:00", "end": "10:00", "name": "Morning Routine"},
            "mid_morning": {"start": "10:00", "end": "12:00", "name": "Mid-Morning Tasks"},
            "afternoon": {"start": "12:00", "end": "16:00", "name": "Afternoon Tasks"},
            "evening": {"start": "16:00", "end": "20:00", "name": "Evening Tasks"},
            "night": {"start": "20:00", "end": "23:59", "name": "Night Routine"}
        }
        
        # Group tasks by time blocks
        tasks_by_block = {}
        for task in tasks:
            task_time = task.get("time", "00:00")
            block_found = False
            
            for block_name, block_info in time_blocks.items():
                if self._is_time_between(task_time, block_info["start"], block_info["end"]):
                    if block_name not in tasks_by_block:
                        tasks_by_block[block_name] = []
                    tasks_by_block[block_name].append(task)
                    block_found = True
                    break
            
            if not block_found:
                # Default to current block or next available
                if "other" not in tasks_by_block:
                    tasks_by_block["other"] = []
                tasks_by_block["other"].append(task)
        
        # Create catch-up tasks for missed blocks
        catch_up_tasks = []
        for block_name, block_info in time_blocks.items():
            if block_name in tasks_by_block:
                block_tasks = tasks_by_block[block_name]
                missed_tasks = []
                
                for task in block_tasks:
                    task_time = task.get("time", "00:00")
                    if self._is_time_before(task_time, current_time_str) and not task.get("completed", False) and not task.get("skipped", False):
                        missed_tasks.append(task)
                
                if missed_tasks:
                    # Create consolidated catch-up task
                    catch_up_task = {
                        "title": f"🚨 CATCH UP: {block_info['name']}",
                        "time": current_time_str,
                        "priority": 1,  # High priority
                        "duration": len(missed_tasks) * 15,  # Estimate 15 min per task
                        "notes": f"URGENT: Complete these missed tasks ASAP:\n\n" + 
                                "\n".join([f"• {task.get('title', 'Unknown')} ({task.get('time', 'No time')})" 
                                          for task in missed_tasks]),
                        "catch_up_tasks": missed_tasks,
                        "is_catch_up": True
                    }
                    catch_up_tasks.append(catch_up_task)
        
        # Add remaining tasks that aren't in catch-up blocks
        remaining_tasks = []
        for task in tasks:
            if not any(task in catch_up_task.get("catch_up_tasks", []) 
                      for catch_up_task in catch_up_tasks):
                remaining_tasks.append(task)
        
        # Combine catch-up tasks (at the top) with remaining tasks
        final_tasks = catch_up_tasks + remaining_tasks
        
        return final_tasks
    
    def _is_time_between(self, time_str, start_str, end_str):
        """Check if a time is between start and end times."""
        try:
            time_parts = time_str.split(":")
            start_parts = start_str.split(":")
            end_parts = end_str.split(":")
            
            time_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
            end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
            
            return start_minutes <= time_minutes <= end_minutes
        except:
            return False
    
    def _is_time_before(self, time_str, current_str):
        """Check if a time is before the current time."""
        try:
            time_parts = time_str.split(":")
            current_parts = current_str.split(":")
            
            time_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            current_minutes = int(current_parts[0]) * 60 + int(current_parts[1])
            
            return time_minutes < current_minutes
        except:
            return False
    
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