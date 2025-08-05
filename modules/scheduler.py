"""
Task Scheduler Module

This module handles scheduling tasks using APScheduler and python-dateutil.
It processes recurrence rules (RRULE) and manages task execution timing.

Author: Raspberry Pi Day Planner
License: MIT
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Any, Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from dateutil import rrule as dateutil_rrule
from dateutil.parser import parse as dateutil_parse
import pytz


class TaskScheduler:
    """
    Manages task scheduling using APScheduler and handles recurrence rules.
    
    This class handles:
    - Scheduling tasks with APScheduler
    - Processing iCalendar RRULE recurrence rules
    - Managing task execution timing
    - Handling timezone conversions
    - Providing task execution callbacks
    """
    
    def __init__(self, 
                 schedule: List[Dict[str, Any]],
                 display_manager: Any,
                 event_logger: Any):
        """
        Initialize the task scheduler.
        
        Args:
            schedule: List of validated task dictionaries.
            display_manager: Display manager instance for showing notifications.
            event_logger: Event logger instance for recording task events.
        """
        self.logger = logging.getLogger(__name__)
        self.schedule = schedule
        self.display_manager = display_manager
        self.event_logger = event_logger
        
        # Initialize APScheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_jobstore('default', job_defaults={'coalesce': True})
        
        # Track scheduled jobs
        self.scheduled_jobs = {}
        
        # Get timezone from first task's settings (all tasks should have same settings)
        self.timezone = None
        if schedule and 'settings' in schedule[0]:
            tz_name = schedule[0]['settings'].get('timezone')
            if tz_name:
                try:
                    self.timezone = pytz.timezone(tz_name)
                    self.logger.info(f"Using timezone: {tz_name}")
                except pytz.exceptions.UnknownTimeZoneError:
                    self.logger.warning(f"Unknown timezone: {tz_name}, using system default")
        
        if not self.timezone:
            self.timezone = pytz.UTC
            self.logger.info("Using UTC timezone")
        
        self.logger.info("Task scheduler initialized")
    
    def start(self):
        """Start the scheduler and schedule all tasks."""
        try:
            self.scheduler.start()
            self.logger.info("APScheduler started")
            
            # Schedule all tasks
            self._schedule_all_tasks()
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler and clear all jobs."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                self.logger.info("APScheduler stopped")
            
            self.scheduled_jobs.clear()
            
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    def _schedule_all_tasks(self):
        """Schedule all tasks from the configuration."""
        for task in self.schedule:
            try:
                self._schedule_task(task)
            except Exception as e:
                self.logger.error(f"Failed to schedule task '{task.get('title', 'Unknown')}': {e}")
    
    def _schedule_task(self, task: Dict[str, Any]):
        """
        Schedule a single task.
        
        Args:
            task: Task dictionary to schedule.
        """
        task_id = self._generate_task_id(task)
        task_time = task['time']
        
        # Check if task has recurrence rule
        if 'rrule' in task:
            self._schedule_recurring_task(task, task_id, task_time)
        else:
            self._schedule_one_time_task(task, task_id, task_time)
    
    def _schedule_recurring_task(self, task: Dict[str, Any], task_id: str, task_time: time):
        """
        Schedule a recurring task using RRULE.
        
        Args:
            task: Task dictionary.
            task_id: Unique task identifier.
            task_time: Time of day for the task.
        """
        rrule_str = task['rrule']
        
        try:
            # Parse RRULE using dateutil
            rrule_obj = dateutil_rrule.rrulestr(rrule_str, dtstart=datetime.now(self.timezone))
            
            # Get next occurrence
            next_occurrence = rrule_obj.after(datetime.now(self.timezone))
            
            if next_occurrence:
                # Schedule the next occurrence
                self._schedule_task_occurrence(task, task_id, next_occurrence)
                
                # Schedule subsequent occurrences
                self._schedule_future_occurrences(task, task_id, rrule_obj)
            
        except Exception as e:
            self.logger.error(f"Failed to parse RRULE '{rrule_str}' for task '{task['title']}': {e}")
            # Fall back to daily scheduling
            self._schedule_daily_task(task, task_id, task_time)
    
    def _schedule_future_occurrences(self, task: Dict[str, Any], task_id: str, rrule_obj):
        """
        Schedule future occurrences of a recurring task.
        
        Args:
            task: Task dictionary.
            task_id: Unique task identifier.
            rrule_obj: Parsed RRULE object.
        """
        # Get occurrences for the next 30 days
        end_date = datetime.now(self.timezone) + timedelta(days=30)
        occurrences = list(rrule_obj.between(
            datetime.now(self.timezone), 
            end_date
        ))
        
        for i, occurrence in enumerate(occurrences[1:], 1):  # Skip first occurrence (already scheduled)
            occurrence_id = f"{task_id}_occ_{i}"
            self._schedule_task_occurrence(task, occurrence_id, occurrence)
    
    def _schedule_daily_task(self, task: Dict[str, Any], task_id: str, task_time: time):
        """
        Schedule a daily task using cron trigger.
        
        Args:
            task: Task dictionary.
            task_id: Unique task identifier.
            task_time: Time of day for the task.
        """
        trigger = CronTrigger(
            hour=task_time.hour,
            minute=task_time.minute,
            timezone=self.timezone
        )
        
        job = self.scheduler.add_job(
            func=self._task_callback,
            trigger=trigger,
            args=[task],
            id=task_id,
            replace_existing=True
        )
        
        self.scheduled_jobs[task_id] = job
        self.logger.info(f"Scheduled daily task '{task['title']}' at {task_time.strftime('%H:%M')}")
    
    def _schedule_one_time_task(self, task: Dict[str, Any], task_id: str, task_time: time):
        """
        Schedule a one-time task.
        
        Args:
            task: Task dictionary.
            task_id: Unique task identifier.
            task_time: Time of day for the task.
        """
        # Calculate next occurrence of this time today or tomorrow
        now = datetime.now(self.timezone)
        today = now.date()
        
        # Create datetime for today at the specified time
        task_datetime = datetime.combine(today, task_time, tzinfo=self.timezone)
        
        # If the time has already passed today, schedule for tomorrow
        if task_datetime <= now:
            task_datetime += timedelta(days=1)
        
        trigger = DateTrigger(run_date=task_datetime)
        
        job = self.scheduler.add_job(
            func=self._task_callback,
            trigger=trigger,
            args=[task],
            id=task_id,
            replace_existing=True
        )
        
        self.scheduled_jobs[task_id] = job
        self.logger.info(f"Scheduled one-time task '{task['title']}' for {task_datetime}")
    
    def _schedule_task_occurrence(self, task: Dict[str, Any], task_id: str, occurrence_time: datetime):
        """
        Schedule a specific task occurrence.
        
        Args:
            task: Task dictionary.
            task_id: Unique task identifier.
            occurrence_time: Specific datetime for the occurrence.
        """
        trigger = DateTrigger(run_date=occurrence_time)
        
        job = self.scheduler.add_job(
            func=self._task_callback,
            trigger=trigger,
            args=[task],
            id=task_id,
            replace_existing=True
        )
        
        self.scheduled_jobs[task_id] = job
        self.logger.info(f"Scheduled task occurrence '{task['title']}' for {occurrence_time}")
    
    def _task_callback(self, task: Dict[str, Any]):
        """
        Callback function executed when a task is due.
        
        Args:
            task: Task dictionary.
        """
        try:
            self.logger.info(f"Task due: {task['title']}")
            
            # Check if task is skipped
            if task.get('skipped', False):
                self.logger.info(f"Task skipped: {task['title']}")
                return
            
            # Log the task event
            if self.event_logger:
                self.event_logger.log_task_shown(task)
            
            # Show the task notification
            if self.display_manager:
                self.display_manager.show_task_notification(task)
            
            # Schedule next occurrence if this is a recurring task
            if 'rrule' in task:
                self._reschedule_recurring_task(task)
                
        except Exception as e:
            self.logger.error(f"Error in task callback for '{task.get('title', 'Unknown')}': {e}")
    
    def _reschedule_recurring_task(self, task: Dict[str, Any]):
        """
        Reschedule the next occurrence of a recurring task.
        
        Args:
            task: Task dictionary.
        """
        try:
            rrule_str = task['rrule']
            rrule_obj = dateutil_rrule.rrulestr(rrule_str, dtstart=datetime.now(self.timezone))
            
            # Get next occurrence after now
            next_occurrence = rrule_obj.after(datetime.now(self.timezone))
            
            if next_occurrence:
                task_id = self._generate_task_id(task)
                self._schedule_task_occurrence(task, task_id, next_occurrence)
                
        except Exception as e:
            self.logger.error(f"Failed to reschedule recurring task '{task['title']}': {e}")
    
    def _generate_task_id(self, task: Dict[str, Any]) -> str:
        """
        Generate a unique identifier for a task.
        
        Args:
            task: Task dictionary.
            
        Returns:
            Unique task identifier.
        """
        title = task['title'].replace(' ', '_').lower()
        time_str = task['time'].strftime('%H%M')
        return f"{title}_{time_str}"
    
    def get_scheduled_jobs(self) -> Dict[str, Any]:
        """
        Get information about all scheduled jobs.
        
        Returns:
            Dictionary of job information.
        """
        jobs_info = {}
        for job_id, job in self.scheduled_jobs.items():
            jobs_info[job_id] = {
                'id': job.id,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            }
        return jobs_info
    
    def remove_job(self, job_id: str):
        """
        Remove a scheduled job.
        
        Args:
            job_id: Job identifier to remove.
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.scheduled_jobs:
                del self.scheduled_jobs[job_id]
            self.logger.info(f"Removed job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to remove job {job_id}: {e}")
    
    def pause_job(self, job_id: str):
        """
        Pause a scheduled job.
        
        Args:
            job_id: Job identifier to pause.
        """
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info(f"Paused job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to pause job {job_id}: {e}")
    
    def resume_job(self, job_id: str):
        """
        Resume a paused job.
        
        Args:
            job_id: Job identifier to resume.
        """
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to resume job {job_id}: {e}")
    
    def skip_task(self, task: Dict[str, Any]):
        """
        Mark a task as skipped for today.
        
        Args:
            task: Task dictionary to skip.
        """
        try:
            task['skipped'] = True
            self.logger.info(f"Task skipped: {task.get('title', 'Unknown')}")
            
            # Log the skip event
            if self.event_logger:
                self.event_logger.log_event(
                    event_type='task_skipped',
                    task_id=task.get('id'),
                    task_title=task.get('title'),
                    details="Task skipped for today"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to skip task: {e}")
    
    def complete_task(self, task: Dict[str, Any]):
        """
        Mark a task as completed.
        
        Args:
            task: Task dictionary to complete.
        """
        try:
            task['completed'] = True
            self.logger.info(f"Task completed: {task.get('title', 'Unknown')}")
            
            # Log the completion event
            if self.event_logger:
                self.event_logger.log_task_completed(task)
                
        except Exception as e:
            self.logger.error(f"Failed to complete task: {e}")
    
    def update_schedule(self, new_schedule: List[Dict[str, Any]]):
        """
        Update the schedule with new tasks.
        
        Args:
            new_schedule: New list of task dictionaries.
        """
        try:
            # Stop current scheduler
            self.scheduler.shutdown(wait=True)
            
            # Clear existing jobs
            self.scheduled_jobs.clear()
            
            # Update schedule
            self.schedule = new_schedule
            
            # Restart scheduler
            self.scheduler.start()
            
            # Reschedule all tasks
            self._schedule_all_tasks()
            
            self.logger.info("Schedule updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update schedule: {e}") 