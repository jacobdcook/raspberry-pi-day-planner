#!/usr/bin/env python3
"""
Task Timer Module
=================

Handles countdown timers for tasks with voice alerts and adaptive time adjustment.
Provides intelligent task flow management based on user behavior.

Features:
- Countdown timer overlay for each task
- Voice alerts using pyttsx3 or pygame.mixer
- Task completion prompts and reason collection
- Adaptive time adjustment for missed/incomplete tasks
- Backlog tracking for overdue tasks
"""

import time
import threading
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
import logging

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import pygame.mixer
    PYGAME_AUDIO_AVAILABLE = True
except ImportError:
    PYGAME_AUDIO_AVAILABLE = False


class TaskTimer:
    def __init__(self):
        self.current_task = None
        self.start_time = None
        self.duration = None
        self.is_running = False
        self.is_paused = False
        self.pause_start = None
        self.total_paused_time = 0
        self.callback = None
        self.timer_thread = None
    
    def start_timer(self, task, duration_minutes=15, callback=None):
        """Start a timer for a task."""
        self.current_task = task
        self.duration = duration_minutes * 60  # Convert to seconds
        self.start_time = time.time()
        self.is_running = True
        self.is_paused = False
        self.pause_start = None
        self.total_paused_time = 0
        self.callback = callback
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        print(f"⏰ Timer started for {task.get('title', 'task')} ({duration_minutes} minutes)")
    
    def pause_timer(self):
        """Pause the current timer."""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.pause_start = time.time()
            print("⏸️ Timer paused")
    
    def resume_timer(self):
        """Resume the paused timer."""
        if self.is_running and self.is_paused:
            self.is_paused = False
            if self.pause_start:
                self.total_paused_time += time.time() - self.pause_start
            self.pause_start = None
            print("▶️ Timer resumed")
    
    def stop_timer(self):
        """Stop the current timer."""
        self.is_running = False
        self.is_paused = False
        self.current_task = None
        self.start_time = None
        self.duration = None
        self.callback = None
        print("⏹️ Timer stopped")
    
    def get_remaining_time(self):
        """Get remaining time in seconds."""
        if not self.is_running or not self.start_time:
            return 0
        
        elapsed = time.time() - self.start_time - self.total_paused_time
        remaining = self.duration - elapsed
        return max(0, remaining)
    
    def get_elapsed_time(self):
        """Get elapsed time in seconds."""
        if not self.is_running or not self.start_time:
            return 0
        
        elapsed = time.time() - self.start_time - self.total_paused_time
        return max(0, elapsed)
    
    def is_complete(self):
        """Check if timer is complete."""
        return self.get_remaining_time() <= 0 and self.is_running
    
    def _timer_loop(self):
        """Internal timer loop."""
        while self.is_running:
            if self.is_complete():
                self.is_running = False
                if self.callback:
                    self.callback(self.current_task)
                print(f"⏰ Timer completed for {self.current_task.get('title', 'task')}")
                break
            time.sleep(1)
    
    def format_time(self, seconds):
        """Format seconds as MM:SS."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_status(self):
        """Get current timer status."""
        if not self.is_running:
            return "stopped"
        elif self.is_paused:
            return "paused"
        else:
            return "running"
    
    def get_formatted_time(self):
        """Get formatted remaining time as MM:SS."""
        remaining = self.get_remaining_time()
        return self.format_time(remaining)
    
    def get_time_remaining(self):
        """Get remaining time in seconds."""
        return self.get_remaining_time()


class AdaptiveTimeManager:
    """
    Manages adaptive time adjustments based on task completion behavior.
    """
    
    def __init__(self):
        """Initialize the adaptive time manager."""
        self.logger = logging.getLogger(__name__)
        self.time_adjustments = []
        self.logger.info("Adaptive time manager initialized")
    
    def adjust_task_times(self, tasks: List[Dict], missed_task: Dict = None) -> List[Dict]:
        """
        Adjust task times based on missed or incomplete tasks.
        
        Args:
            tasks: List of remaining tasks
            missed_task: The task that was missed or incomplete
            
        Returns:
            List of tasks with adjusted times
        """
        if not missed_task:
            return tasks
        
        adjusted_tasks = tasks.copy()
        missed_duration = missed_task.get('duration', 0)
        missed_priority = missed_task.get('priority', 3)
        
        # Find next low-priority task to reduce time
        for i, task in enumerate(adjusted_tasks):
            if task.get('priority', 3) > 2:  # Low priority
                current_duration = task.get('duration', 0)
                reduction = min(missed_duration, current_duration * 0.3)  # Max 30% reduction
                
                if reduction > 0:
                    new_duration = max(5, current_duration - reduction)  # Minimum 5 minutes
                    old_duration = current_duration
                    
                    adjusted_tasks[i]['duration'] = new_duration
                    adjusted_tasks[i]['original_duration'] = old_duration
                    adjusted_tasks[i]['time_adjusted'] = True
                    
                    # Record adjustment
                    adjustment = {
                        'task_title': task.get('title', 'Unknown'),
                        'old_duration': old_duration,
                        'new_duration': new_duration,
                        'reduction': old_duration - new_duration,
                        'reason': f"Missed task: {missed_task.get('title', 'Unknown')}",
                        'timestamp': datetime.now().isoformat()
                    }
                    self.time_adjustments.append(adjustment)
                    
                    self.logger.info(f"Adjusted '{task.get('title')}' from {old_duration}min to {new_duration}min")
                    break
        
        return adjusted_tasks
    
    def get_recent_adjustments(self, limit: int = 5) -> List[Dict]:
        """Get recent time adjustments."""
        return self.time_adjustments[-limit:] if self.time_adjustments else []
    
    def create_adjustment_alert(self, adjustment: Dict) -> str:
        """Create alert message for time adjustment."""
        return f"Reduced '{adjustment['task_title']}' from {adjustment['old_duration']}min to {adjustment['new_duration']}min to catch up."
    
    def reset_adjustments(self):
        """Reset all time adjustments."""
        self.time_adjustments.clear()
        self.logger.info("Time adjustments reset") 