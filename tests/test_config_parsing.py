"""
Test Configuration Parsing

Tests for the configuration loading and validation functionality.

Author: Raspberry Pi Day Planner
License: MIT
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from datetime import time
from modules.loader import ScheduleLoader


class TestScheduleLoader:
    """Test cases for ScheduleLoader class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file for testing."""
        config_data = {
            'morning_tasks': [
                {
                    'title': 'Test Task',
                    'time': '08:00',
                    'notes': 'Test notes',
                    'priority': 1,
                    'audio_alert': True,
                    'snooze_duration': 15
                }
            ],
            'settings': {
                'fullscreen': True,
                'default_volume': 0.7,
                'timezone': 'America/New_York'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            yield f.name
        
        # Cleanup
        Path(f.name).unlink()
    
    def test_load_valid_config(self, temp_config_file):
        """Test loading a valid configuration file."""
        loader = ScheduleLoader(config_path=temp_config_file)
        schedule = loader.load_schedule()
        
        assert schedule is not None
        assert 'morning_tasks' in schedule
        assert 'settings' in schedule
        assert len(schedule['morning_tasks']) == 1
        assert schedule['morning_tasks'][0]['title'] == 'Test Task'
    
    def test_validate_time_format(self):
        """Test time string validation."""
        loader = ScheduleLoader()
        
        # Valid times
        assert loader._parse_time_string("08:00") == time(8, 0)
        assert loader._parse_time_string("23:59") == time(23, 59)
        assert loader._parse_time_string("00:00") == time(0, 0)
        
        # Invalid times
        with pytest.raises(ValueError):
            loader._parse_time_string("25:00")
        with pytest.raises(ValueError):
            loader._parse_time_string("08:60")
        with pytest.raises(ValueError):
            loader._parse_time_string("8:00")
        with pytest.raises(ValueError):
            loader._parse_time_string("08:0")
    
    def test_validate_rrule(self):
        """Test RRULE validation."""
        loader = ScheduleLoader()
        
        # Valid RRULEs
        assert loader._validate_rrule("FREQ=DAILY;INTERVAL=1")
        assert loader._validate_rrule("FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR")
        assert loader._validate_rrule("FREQ=MONTHLY;BYMONTHDAY=1")
        
        # Invalid RRULEs
        with pytest.raises(ValueError):
            loader._validate_rrule("INVALID=RULE")
        with pytest.raises(ValueError):
            loader._validate_rrule("FREQ=INVALID")
    
    def test_validate_task_fields(self):
        """Test task field validation."""
        loader = ScheduleLoader()
        
        # Valid task
        valid_task = {
            'title': 'Test Task',
            'time': '08:00',
            'notes': 'Test notes',
            'priority': 1,
            'audio_alert': True,
            'snooze_duration': 15
        }
        assert loader._validate_single_task(valid_task) is True
        
        # Missing required fields
        invalid_task = {'title': 'Test Task'}
        with pytest.raises(ValueError):
            loader._validate_single_task(invalid_task)
        
        # Invalid priority
        invalid_priority_task = valid_task.copy()
        invalid_priority_task['priority'] = 6
        with pytest.raises(ValueError):
            loader._validate_single_task(invalid_priority_task)
        
        # Invalid snooze duration
        invalid_snooze_task = valid_task.copy()
        invalid_snooze_task['snooze_duration'] = 0
        with pytest.raises(ValueError):
            loader._validate_single_task(invalid_snooze_task)
    
    def test_extract_tasks(self):
        """Test task extraction from configuration."""
        config = {
            'morning_tasks': [
                {'title': 'Task 1', 'time': '08:00', 'priority': 1}
            ],
            'afternoon_tasks': [
                {'title': 'Task 2', 'time': '14:00', 'priority': 2}
            ],
            'settings': {'fullscreen': True}
        }
        
        loader = ScheduleLoader()
        tasks = loader._extract_tasks(config)
        
        assert len(tasks) == 2
        assert tasks[0]['title'] == 'Task 1'
        assert tasks[1]['title'] == 'Task 2'
    
    def test_validate_settings(self):
        """Test settings validation."""
        loader = ScheduleLoader()
        
        # Valid settings
        valid_settings = {
            'fullscreen': True,
            'default_volume': 0.7,
            'timezone': 'America/New_York'
        }
        assert loader._validate_settings(valid_settings) is True
        
        # Invalid volume
        invalid_volume_settings = valid_settings.copy()
        invalid_volume_settings['default_volume'] = 1.5
        with pytest.raises(ValueError):
            loader._validate_settings(invalid_volume_settings)
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file."""
        loader = ScheduleLoader(config_path="nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            loader.load_schedule()
    
    def test_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: syntax: [")
            f.flush()
            
            loader = ScheduleLoader(config_path=f.name)
            with pytest.raises(yaml.YAMLError):
                loader.load_schedule()
        
        Path(f.name).unlink()
    
    def test_reload_schedule(self, temp_config_file):
        """Test schedule reloading functionality."""
        loader = ScheduleLoader(config_path=temp_config_file)
        original_schedule = loader.load_schedule()
        
        # Reload should return the same data
        reloaded_schedule = loader.reload_schedule()
        assert reloaded_schedule == original_schedule


class TestConfigurationIntegration:
    """Integration tests for configuration functionality."""
    
    def test_full_config_validation(self):
        """Test complete configuration validation process."""
        config_data = {
            'morning_tasks': [
                {
                    'title': 'Morning Task',
                    'time': '07:00',
                    'notes': 'Morning routine',
                    'priority': 1,
                    'audio_alert': True,
                    'snooze_duration': 15,
                    'rrule': 'FREQ=DAILY;INTERVAL=1'
                }
            ],
            'learning_tasks': [
                {
                    'title': 'Study Session',
                    'time': '10:00',
                    'notes': 'Learning time',
                    'priority': 2,
                    'audio_alert': True,
                    'snooze_duration': 30,
                    'rrule': 'FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR'
                }
            ],
            'settings': {
                'fullscreen': True,
                'screen_timeout': 300,
                'brightness': 0.8,
                'default_volume': 0.7,
                'alert_sound': 'alert.wav',
                'snooze_sound': 'snooze.wav',
                'notification_duration': 60,
                'max_snooze_count': 3,
                'log_level': 'INFO',
                'log_retention_days': 30,
                'timezone': 'America/New_York'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            
            loader = ScheduleLoader(config_path=f.name)
            schedule = loader.load_schedule()
            
            # Verify structure
            assert 'morning_tasks' in schedule
            assert 'learning_tasks' in schedule
            assert 'settings' in schedule
            
            # Verify task data
            morning_task = schedule['morning_tasks'][0]
            assert morning_task['title'] == 'Morning Task'
            assert morning_task['time'] == time(7, 0)
            assert morning_task['priority'] == 1
            
            # Verify settings
            settings = schedule['settings']
            assert settings['fullscreen'] is True
            assert settings['default_volume'] == 0.7
            assert settings['timezone'] == 'America/New_York'
        
        Path(f.name).unlink()
    
    def test_error_handling(self):
        """Test error handling in configuration loading."""
        # Test with malformed task data
        config_data = {
            'morning_tasks': [
                {
                    'title': 'Invalid Task',
                    'time': '25:00',  # Invalid time
                    'priority': 6     # Invalid priority
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            
            loader = ScheduleLoader(config_path=f.name)
            with pytest.raises(ValueError):
                loader.load_schedule()
        
        Path(f.name).unlink() 