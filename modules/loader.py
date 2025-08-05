"""
Schedule Loader Module

This module handles loading and validating the daily schedule configuration
from the YAML file. It provides validation for task structure, time formats,
and recurrence rules.

Author: Raspberry Pi Day Planner
License: MIT
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime, time
from typing import Dict, List, Any, Optional
import re


class ScheduleLoader:
    """
    Loads and validates schedule configuration from YAML files.
    
    This class handles:
    - Loading YAML configuration files
    - Validating task structure and data types
    - Parsing time strings into time objects
    - Validating recurrence rules (RRULE format)
    - Merging tasks from different categories
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the schedule loader.
        
        Args:
            config_path: Path to the YAML configuration file.
                        Defaults to 'config/schedule.yaml' relative to project root.
        """
        self.logger = logging.getLogger(__name__)
        
        if config_path is None:
            # Default to config/schedule.yaml relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "schedule.yaml"
        
        self.config_path = Path(config_path)
        self.logger.info(f"Schedule loader initialized with config: {self.config_path}")
    
    def load_schedule(self) -> List[Dict[str, Any]]:
        """
        Load and validate the complete schedule from the YAML file.
        
        Returns:
            List of validated task dictionaries.
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
            ValueError: If the schedule validation fails.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
            
            self.logger.info("Configuration file loaded successfully")
            
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML file: {e}")
            raise
        
        # Extract and validate tasks
        tasks = self._extract_tasks(config_data)
        validated_tasks = self._validate_tasks(tasks)
        
        # Extract settings
        settings = config_data.get('settings', {})
        validated_settings = self._validate_settings(settings)
        
        # Add settings to each task for easy access
        for task in validated_tasks:
            task['settings'] = validated_settings
        
        self.logger.info(f"Loaded {len(validated_tasks)} validated tasks")
        return validated_tasks
    
    def _extract_tasks(self, config_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tasks from all categories in the configuration.
        
        Args:
            config_data: The loaded YAML configuration data.
            
        Returns:
            List of all tasks from all categories.
        """
        tasks = []
        
        # Define task categories to extract
        task_categories = [
            'morning_tasks', 'learning_tasks', 'exercise_tasks',
            'personal_tasks', 'evening_tasks', 'weekly_tasks'
        ]
        
        for category in task_categories:
            if category in config_data:
                category_tasks = config_data[category]
                if isinstance(category_tasks, list):
                    for task in category_tasks:
                        if isinstance(task, dict):
                            # Add category information to task
                            task['category'] = category
                            tasks.append(task)
                        else:
                            self.logger.warning(f"Invalid task in {category}: {task}")
                else:
                    self.logger.warning(f"Invalid category {category}: expected list, got {type(category_tasks)}")
        
        return tasks
    
    def _validate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate all tasks in the schedule.
        
        Args:
            tasks: List of task dictionaries to validate.
            
        Returns:
            List of validated task dictionaries.
            
        Raises:
            ValueError: If any task validation fails.
        """
        validated_tasks = []
        
        for i, task in enumerate(tasks):
            try:
                validated_task = self._validate_single_task(task, i)
                validated_tasks.append(validated_task)
            except ValueError as e:
                self.logger.error(f"Task {i} validation failed: {e}")
                raise
        
        return validated_tasks
    
    def _validate_single_task(self, task: Dict[str, Any], task_index: int) -> Dict[str, Any]:
        """
        Validate a single task dictionary.
        
        Args:
            task: Task dictionary to validate.
            task_index: Index of the task for error reporting.
            
        Returns:
            Validated task dictionary.
            
        Raises:
            ValueError: If task validation fails.
        """
        # Required fields
        required_fields = ['title', 'time']
        for field in required_fields:
            if field not in task:
                raise ValueError(f"Task {task_index}: Missing required field '{field}'")
        
        # Validate title
        if not isinstance(task['title'], str) or not task['title'].strip():
            raise ValueError(f"Task {task_index}: Invalid title")
        
        # Validate and parse time
        time_str = task['time']
        if not isinstance(time_str, str):
            raise ValueError(f"Task {task_index}: Time must be a string")
        
        try:
            parsed_time = self._parse_time_string(time_str)
            task['time'] = parsed_time
        except ValueError as e:
            raise ValueError(f"Task {task_index}: Invalid time format '{time_str}': {e}")
        
        # Validate optional fields
        if 'notes' in task:
            if not isinstance(task['notes'], str):
                raise ValueError(f"Task {task_index}: Notes must be a string")
        
        if 'priority' in task:
            priority = task['priority']
            if not isinstance(priority, int) or priority < 1 or priority > 5:
                raise ValueError(f"Task {task_index}: Priority must be an integer between 1-5")
        
        if 'audio_alert' in task:
            if not isinstance(task['audio_alert'], bool):
                raise ValueError(f"Task {task_index}: audio_alert must be a boolean")
        
        if 'snooze_duration' in task:
            snooze = task['snooze_duration']
            if not isinstance(snooze, int) or snooze < 1:
                raise ValueError(f"Task {task_index}: snooze_duration must be a positive integer")
        
        if 'rrule' in task:
            rrule = task['rrule']
            if not isinstance(rrule, str):
                raise ValueError(f"Task {task_index}: rrule must be a string")
            self._validate_rrule(rrule, task_index)
        
        # Set defaults for missing optional fields
        task.setdefault('notes', '')
        task.setdefault('priority', 3)
        task.setdefault('audio_alert', True)
        task.setdefault('snooze_duration', 15)
        task.setdefault('category', 'general')
        
        return task
    
    def _parse_time_string(self, time_str: str) -> time:
        """
        Parse a time string into a time object.
        
        Args:
            time_str: Time string in HH:MM format.
            
        Returns:
            time object.
            
        Raises:
            ValueError: If time string is invalid.
        """
        # Validate time format (HH:MM)
        time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$')
        match = time_pattern.match(time_str)
        
        if not match:
            raise ValueError("Time must be in HH:MM format (24-hour)")
        
        hour = int(match.group(1))
        minute = int(match.group(2))
        
        return time(hour, minute)
    
    def _validate_rrule(self, rrule: str, task_index: int) -> None:
        """
        Validate recurrence rule (RRULE) format.
        
        Args:
            rrule: RRULE string to validate.
            task_index: Index of the task for error reporting.
            
        Raises:
            ValueError: If RRULE is invalid.
        """
        # Basic RRULE validation - check for required components
        rrule = rrule.upper()
        
        if not rrule.startswith('FREQ='):
            raise ValueError(f"Task {task_index}: RRULE must start with FREQ=")
        
        # Check for valid frequency values
        valid_freqs = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
        freq_match = re.search(r'FREQ=([A-Z]+)', rrule)
        if not freq_match or freq_match.group(1) not in valid_freqs:
            raise ValueError(f"Task {task_index}: Invalid frequency in RRULE")
        
        # Additional validation can be added here for more complex RRULE parsing
        # For now, we'll rely on python-dateutil for full validation when scheduling
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate application settings.
        
        Args:
            settings: Settings dictionary to validate.
            
        Returns:
            Validated settings dictionary.
        """
        validated_settings = {}
        
        # Display settings
        validated_settings['fullscreen'] = settings.get('fullscreen', True)
        validated_settings['screen_timeout'] = max(30, settings.get('screen_timeout', 300))
        validated_settings['brightness'] = max(0.1, min(1.0, settings.get('brightness', 0.8)))
        
        # Audio settings
        validated_settings['default_volume'] = max(0.0, min(1.0, settings.get('default_volume', 0.7)))
        validated_settings['alert_sound'] = settings.get('alert_sound', 'alert.wav')
        validated_settings['snooze_sound'] = settings.get('snooze_sound', 'snooze.wav')
        
        # Notification settings
        validated_settings['notification_duration'] = max(10, settings.get('notification_duration', 60))
        validated_settings['max_snooze_count'] = max(1, settings.get('max_snooze_count', 3))
        
        # Logging settings
        validated_settings['log_level'] = settings.get('log_level', 'INFO')
        validated_settings['log_retention_days'] = max(1, settings.get('log_retention_days', 30))
        
        # Timezone
        validated_settings['timezone'] = settings.get('timezone', None)
        
        return validated_settings
    
    def reload_schedule(self) -> List[Dict[str, Any]]:
        """
        Reload the schedule from the configuration file.
        
        Returns:
            List of validated task dictionaries.
        """
        self.logger.info("Reloading schedule configuration...")
        return self.load_schedule() 