"""
Display Manager Module

This module handles the fullscreen Tkinter UI for displaying task notifications,
countdown timers, and user interaction buttons (Done/Snooze).

Author: Raspberry Pi Day Planner
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
import queue


class DisplayManager:
    """
    Manages the fullscreen Tkinter display for task notifications.
    
    This class handles:
    - Fullscreen Tkinter window management
    - Task notification display with countdown timers
    - User interaction buttons (Done/Snooze)
    - Screen timeout and brightness control
    - Thread-safe UI updates
    """
    
    def __init__(self, audio_manager: Any, event_logger: Any):
        """
        Initialize the display manager.
        
        Args:
            audio_manager: Audio manager instance for playing sounds.
            event_logger: Event logger instance for recording user actions.
        """
        self.logger = logging.getLogger(__name__)
        self.audio_manager = audio_manager
        self.event_logger = event_logger
        
        # UI components
        self.root = None
        self.current_notification = None
        self.countdown_thread = None
        self.countdown_running = False
        
        # Thread-safe queue for UI updates
        self.ui_queue = queue.Queue()
        
        # Settings
        self.settings = {
            'fullscreen': True,
            'screen_timeout': 300,  # seconds
            'brightness': 0.8,
            'notification_duration': 60,
            'max_snooze_count': 3
        }
        
        self.logger.info("Display manager initialized")
    
    def start(self):
        """Start the display manager and create the main window."""
        try:
            # Create main window in a separate thread
            self._create_main_window()
            
            # Start UI update thread
            self._start_ui_thread()
            
            self.logger.info("Display manager started")
            
        except Exception as e:
            self.logger.error(f"Failed to start display manager: {e}")
            raise
    
    def _create_main_window(self):
        """Create the main Tkinter window."""
        self.root = tk.Tk()
        self.root.title("Raspberry Pi Day Planner")
        
        # Configure fullscreen
        if self.settings['fullscreen']:
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
        
        # Configure window properties
        self.root.configure(bg='black')
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Bind keyboard shortcuts
        self.root.bind('<Escape>', self._on_escape)
        self.root.bind('<F11>', self._toggle_fullscreen)
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create idle screen
        self._create_idle_screen()
        
        self.logger.info("Main window created")
    
    def _create_idle_screen(self):
        """Create the idle screen shown when no notifications are active."""
        # Clear existing widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create idle content
        idle_frame = tk.Frame(self.main_frame, bg='black')
        idle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Clock label
        self.clock_label = tk.Label(
            idle_frame,
            text="",
            font=('Arial', 48, 'bold'),
            fg='white',
            bg='black'
        )
        self.clock_label.pack(pady=50)
        
        # Status label
        self.status_label = tk.Label(
            idle_frame,
            text="Day Planner Active",
            font=('Arial', 24),
            fg='lightgray',
            bg='black'
        )
        self.status_label.pack(pady=20)
        
        # Next task label
        self.next_task_label = tk.Label(
            idle_frame,
            text="",
            font=('Arial', 18),
            fg='lightblue',
            bg='black'
        )
        self.next_task_label.pack(pady=20)
        
        # Start clock update
        self._update_clock()
    
    def _update_clock(self):
        """Update the clock display."""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            
            self.clock_label.config(text=f"{current_time}\n{current_date}")
            
            # Schedule next update
            self.root.after(1000, self._update_clock)
            
        except Exception as e:
            self.logger.error(f"Error updating clock: {e}")
    
    def show_task_notification(self, task: Dict[str, Any]):
        """
        Show a task notification with countdown timer.
        
        Args:
            task: Task dictionary to display.
        """
        try:
            # Put notification request in queue for thread safety
            self.ui_queue.put(('show_notification', task))
            
        except Exception as e:
            self.logger.error(f"Error showing task notification: {e}")
    
    def _show_notification_ui(self, task: Dict[str, Any]):
        """
        Show the notification UI (called from main thread).
        
        Args:
            task: Task dictionary to display.
        """
        try:
            # Stop countdown if running
            self._stop_countdown()
            
            # Clear main frame
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            
            # Create notification frame
            notification_frame = tk.Frame(self.main_frame, bg='black')
            notification_frame.pack(fill=tk.BOTH, expand=True)
            
            # Task title
            title_label = tk.Label(
                notification_frame,
                text=task['title'],
                font=('Arial', 36, 'bold'),
                fg='white',
                bg='black'
            )
            title_label.pack(pady=30)
            
            # Task time
            time_str = task['time'].strftime("%H:%M")
            time_label = tk.Label(
                notification_frame,
                text=f"Time: {time_str}",
                font=('Arial', 24),
                fg='lightblue',
                bg='black'
            )
            time_label.pack(pady=10)
            
            # Task notes
            if task.get('notes'):
                notes_label = tk.Label(
                    notification_frame,
                    text=task['notes'],
                    font=('Arial', 18),
                    fg='lightgray',
                    bg='black',
                    wraplength=600
                )
                notes_label.pack(pady=20)
            
            # Countdown timer
            self.countdown_label = tk.Label(
                notification_frame,
                text="",
                font=('Arial', 28, 'bold'),
                fg='yellow',
                bg='black'
            )
            self.countdown_label.pack(pady=30)
            
            # Priority indicator
            priority = task.get('priority', 3)
            priority_colors = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'lightblue', 5: 'lightgray'}
            priority_color = priority_colors.get(priority, 'yellow')
            
            priority_label = tk.Label(
                notification_frame,
                text=f"Priority: {priority}",
                font=('Arial', 16),
                fg=priority_color,
                bg='black'
            )
            priority_label.pack(pady=10)
            
            # Button frame
            button_frame = tk.Frame(notification_frame, bg='black')
            button_frame.pack(pady=40)
            
            # Done button
            done_button = tk.Button(
                button_frame,
                text="DONE",
                font=('Arial', 20, 'bold'),
                bg='green',
                fg='white',
                width=10,
                height=2,
                command=lambda: self._on_done_clicked(task)
            )
            done_button.pack(side=tk.LEFT, padx=20)
            
            # Snooze button
            snooze_button = tk.Button(
                button_frame,
                text="SNOOZE",
                font=('Arial', 20, 'bold'),
                bg='orange',
                fg='white',
                width=10,
                height=2,
                command=lambda: self._on_snooze_clicked(task)
            )
            snooze_button.pack(side=tk.LEFT, padx=20)
            
            # Store current notification
            self.current_notification = task
            
            # Play audio alert if enabled
            if task.get('audio_alert', True) and self.audio_manager:
                self.audio_manager.play_alert()
            
            # Start countdown
            self._start_countdown(task)
            
            self.logger.info(f"Showing notification for task: {task['title']}")
            
        except Exception as e:
            self.logger.error(f"Error showing notification UI: {e}")
    
    def _start_countdown(self, task: Dict[str, Any]):
        """Start countdown timer for the notification."""
        duration = self.settings.get('notification_duration', 60)
        self.countdown_running = True
        
        def countdown():
            remaining = duration
            while remaining > 0 and self.countdown_running:
                try:
                    minutes = remaining // 60
                    seconds = remaining % 60
                    countdown_text = f"Auto-dismiss in: {minutes:02d}:{seconds:02d}"
                    
                    # Update countdown label
                    if hasattr(self, 'countdown_label'):
                        self.ui_queue.put(('update_countdown', countdown_text))
                    
                    time.sleep(1)
                    remaining -= 1
                    
                except Exception as e:
                    self.logger.error(f"Error in countdown: {e}")
                    break
            
            # Auto-dismiss when countdown reaches zero
            if self.countdown_running:
                self.ui_queue.put(('auto_dismiss', None))
        
        self.countdown_thread = threading.Thread(target=countdown, daemon=True)
        self.countdown_thread.start()
    
    def _stop_countdown(self):
        """Stop the countdown timer."""
        self.countdown_running = False
        if self.countdown_thread and self.countdown_thread.is_alive():
            self.countdown_thread.join(timeout=1)
    
    def _on_done_clicked(self, task: Dict[str, Any]):
        """Handle Done button click."""
        try:
            self.logger.info(f"Task completed: {task['title']}")
            
            # Log the completion
            if self.event_logger:
                self.event_logger.log_task_completed(task)
            
            # Play completion sound
            if self.audio_manager:
                self.audio_manager.play_completion()
            
            # Return to idle screen
            self._return_to_idle()
            
        except Exception as e:
            self.logger.error(f"Error handling done click: {e}")
    
    def _on_snooze_clicked(self, task: Dict[str, Any]):
        """Handle Snooze button click."""
        try:
            snooze_duration = task.get('snooze_duration', 15)
            self.logger.info(f"Task snoozed: {task['title']} for {snooze_duration} minutes")
            
            # Log the snooze
            if self.event_logger:
                self.event_logger.log_task_snoozed(task, snooze_duration)
            
            # Play snooze sound
            if self.audio_manager:
                self.audio_manager.play_snooze()
            
            # Return to idle screen
            self._return_to_idle()
            
            # TODO: Reschedule task for snooze duration
            # This would require coordination with the TaskScheduler
            
        except Exception as e:
            self.logger.error(f"Error handling snooze click: {e}")
    
    def _return_to_idle(self):
        """Return to the idle screen."""
        try:
            # Stop countdown
            self._stop_countdown()
            
            # Clear current notification
            self.current_notification = None
            
            # Recreate idle screen
            self._create_idle_screen()
            
        except Exception as e:
            self.logger.error(f"Error returning to idle: {e}")
    
    def _start_ui_thread(self):
        """Start the UI update thread."""
        def ui_updater():
            while True:
                try:
                    # Get next UI update from queue
                    action, data = self.ui_queue.get(timeout=1)
                    
                    if action == 'show_notification':
                        self._show_notification_ui(data)
                    elif action == 'update_countdown':
                        if hasattr(self, 'countdown_label'):
                            self.countdown_label.config(text=data)
                    elif action == 'auto_dismiss':
                        self._return_to_idle()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error in UI updater: {e}")
        
        ui_thread = threading.Thread(target=ui_updater, daemon=True)
        ui_thread.start()
    
    def _on_closing(self):
        """Handle window closing."""
        self.logger.info("Display window closing")
        self.close()
    
    def _on_escape(self, event):
        """Handle Escape key press."""
        if self.current_notification:
            self._return_to_idle()
        else:
            self.close()
    
    def _toggle_fullscreen(self, event):
        """Toggle fullscreen mode."""
        if self.root:
            self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
    
    def close(self):
        """Close the display manager."""
        try:
            self._stop_countdown()
            
            if self.root:
                self.root.quit()
                self.root.destroy()
            
            self.logger.info("Display manager closed")
            
        except Exception as e:
            self.logger.error(f"Error closing display manager: {e}")
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update display settings."""
        self.settings.update(settings)
        self.logger.info("Display settings updated")
    
    def get_current_notification(self) -> Optional[Dict[str, Any]]:
        """Get the currently displayed notification."""
        return self.current_notification 