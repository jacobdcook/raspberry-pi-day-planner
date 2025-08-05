"""
Peptide Scheduler Module

This module handles peptide administration scheduling with support for multiple
schedule files and schedule selection. It integrates with the main scheduler
and provides specialized peptide tracking functionality.

Author: Raspberry Pi Day Planner
License: MIT
"""

import logging
import yaml
import os
from datetime import datetime, time, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import pytz


class PeptideScheduler:
    """
    Manages peptide administration scheduling with support for multiple schedule files.
    
    This class handles:
    - Loading peptide schedules from different files
    - Schedule selection (sample vs personal)
    - Peptide-specific task creation
    - Integration with main scheduler
    - Peptide administration tracking
    """
    
    def __init__(self, 
                 config_dir: str = "config",
                 display_manager: Any = None,
                 event_logger: Any = None):
        """
        Initialize the peptide scheduler.
        
        Args:
            config_dir: Directory containing schedule files
            display_manager: Display manager instance for showing notifications
            event_logger: Event logger instance for recording events
        """
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path(config_dir)
        self.display_manager = display_manager
        self.event_logger = event_logger
        
        # Available schedule files
        self.schedule_files = {
            "sample": "sample_schedule.yaml",  # This would be a demo file
            "personal": "schedule.yaml",        # Your actual personal schedule
            "peptide": "peptide_schedule.yaml"
        }
        
        # Current active schedule
        self.active_schedule = "personal"  # Default to personal schedule
        self.peptide_schedule = None
        self.main_schedule = None
        
        # Peptide tracking
        self.peptide_history = []
        self.current_protocol = None
        
        self.logger.info("Peptide scheduler initialized")
    
    def select_schedule(self, schedule_type: str = "personal") -> bool:
        """
        Select which schedule to use.
        
        Args:
            schedule_type: "sample", "personal", or "peptide"
            
        Returns:
            True if schedule loaded successfully, False otherwise
        """
        try:
            if schedule_type not in self.schedule_files:
                self.logger.error(f"Invalid schedule type: {schedule_type}")
                return False
            
            schedule_file = self.schedule_files[schedule_type]
            schedule_path = self.config_dir / schedule_file
            
            if not schedule_path.exists():
                self.logger.error(f"Schedule file not found: {schedule_path}")
                return False
            
            # Load the selected schedule with proper encoding
            try:
                with open(schedule_path, 'r', encoding='utf-8') as f:
                    schedule_data = yaml.safe_load(f)
            except UnicodeDecodeError:
                # Fallback to system default encoding
                with open(schedule_path, 'r', encoding='latin-1') as f:
                    schedule_data = yaml.safe_load(f)
            
            if schedule_type == "peptide":
                self.peptide_schedule = schedule_data
                self.logger.info(f"Loaded peptide schedule from {schedule_file}")
            else:
                self.main_schedule = schedule_data
                self.active_schedule = schedule_type
                self.logger.info(f"Loaded {schedule_type} schedule from {schedule_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load schedule {schedule_type}: {e}")
            return False
    
    def get_schedule_selection_menu(self) -> List[Dict[str, str]]:
        """
        Get available schedule options for user selection.
        
        Returns:
            List of schedule options with descriptions
        """
        options = [
            {
                "id": "sample",
                "name": "Sample Schedule",
                "description": "Demo schedule for GitHub (public)",
                "file": self.schedule_files["sample"]
            },
            {
                "id": "personal", 
                "name": "Personal Schedule",
                "description": "Your actual schedule (private)",
                "file": self.schedule_files["personal"]
            },
            {
                "id": "peptide",
                "name": "Peptide Schedule",
                "description": "BPC-157 + TB-500 protocol",
                "file": self.schedule_files["peptide"]
            }
        ]
        
        # Check which files exist
        for option in options:
            file_path = self.config_dir / option["file"]
            option["exists"] = file_path.exists()
            option["active"] = (option["id"] == self.active_schedule)
        
        return options
    
    def load_peptide_schedule(self) -> bool:
        """
        Load the peptide schedule specifically.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        return self.select_schedule("peptide")
    
    def get_today_peptide_dose(self, date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Get today's peptide dose information.
        
        Args:
            date: Date to check (defaults to today)
            
        Returns:
            Peptide dose information for the specified date
        """
        if not self.peptide_schedule:
            self.logger.warning("No peptide schedule loaded")
            return None
        
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        # Check in peptide schedule
        if "peptide_protocol" in self.peptide_schedule:
            protocol = self.peptide_schedule["peptide_protocol"]
            
            # Check each month section
            for month_key, month_data in protocol.items():
                if isinstance(month_data, dict) and date_str in month_data:
                    dose_info = month_data[date_str]
                    return {
                        "date": date_str,
                        "bpc_157": dose_info.get("bpc_157"),
                        "tb_500": dose_info.get("tb_500"),
                        "notes": dose_info.get("notes"),
                        "protocol": protocol.get("protocol_name"),
                        "administration_time": protocol.get("administration_time")
                    }
        
        return None
    
    def get_peptide_tasks_for_scheduler(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Convert peptide schedule to task format for main scheduler.
        
        Args:
            start_date: Start date for task generation
            end_date: End date for task generation
            
        Returns:
            List of tasks in scheduler format
        """
        if not self.peptide_schedule:
            return []
        
        tasks = []
        current_date = start_date
        
        while current_date <= end_date:
            dose_info = self.get_today_peptide_dose(current_date)
            if dose_info:
                # Create task for this dose
                task = {
                    "title": f"Peptide Dose - {dose_info['date']}",
                    "date": dose_info["date"],
                    "time": dose_info.get("administration_time", "12:15"),
                    "notes": self._format_peptide_notes(dose_info),
                    "priority": 1,
                    "audio_alert": True,
                    "snooze_duration": 10,
                    "duration": 15,
                    "task_type": "peptide",
                    "peptide_info": dose_info
                }
                tasks.append(task)
            
            current_date += timedelta(days=1)
        
        return tasks
    
    def _format_peptide_notes(self, dose_info: Dict[str, Any]) -> str:
        """
        Format peptide dose information into readable notes.
        
        Args:
            dose_info: Peptide dose information
            
        Returns:
            Formatted notes string
        """
        notes_parts = []
        
        if dose_info.get("bpc_157"):
            notes_parts.append(f"BPC-157: {dose_info['bpc_157']}")
        
        if dose_info.get("tb_500"):
            notes_parts.append(f"TB-500: {dose_info['tb_500']}")
        
        if dose_info.get("notes"):
            notes_parts.append(f"Notes: {dose_info['notes']}")
        
        return " | ".join(notes_parts)
    
    def log_peptide_administration(self, dose_info: Dict[str, Any], administered: bool = True):
        """
        Log peptide administration for tracking.
        
        Args:
            dose_info: Peptide dose information
            administered: Whether the dose was actually administered
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "date": dose_info["date"],
            "bpc_157": dose_info.get("bpc_157"),
            "tb_500": dose_info.get("tb_500"),
            "administered": administered,
            "notes": dose_info.get("notes", "")
        }
        
        self.peptide_history.append(log_entry)
        
        if self.event_logger:
            status = "ADMINISTERED" if administered else "MISSED"
            self.event_logger.log_event(
                "peptide_administration",
                f"Peptide dose {status}: {dose_info['date']}",
                log_entry
            )
        
        self.logger.info(f"Peptide administration logged: {dose_info['date']} - {status}")
    
    def get_peptide_progress(self) -> Dict[str, Any]:
        """
        Get peptide protocol progress information.
        
        Returns:
            Progress information including completion percentage, days remaining, etc.
        """
        if not self.peptide_schedule:
            return {}
        
        protocol = self.peptide_schedule.get("peptide_protocol", {})
        protocol_name = protocol.get("protocol_name", "Unknown Protocol")
        protocol_duration = protocol.get("protocol_duration", "")
        
        # Calculate progress
        total_doses = 0
        administered_doses = 0
        
        for month_data in protocol.values():
            if isinstance(month_data, dict):
                total_doses += len(month_data)
        
        for entry in self.peptide_history:
            if entry.get("administered", False):
                administered_doses += 1
        
        progress_percentage = (administered_doses / total_doses * 100) if total_doses > 0 else 0
        days_remaining = total_doses - administered_doses
        
        return {
            "protocol_name": protocol_name,
            "protocol_duration": protocol_duration,
            "total_doses": total_doses,
            "administered_doses": administered_doses,
            "missed_doses": len([e for e in self.peptide_history if not e.get("administered", False)]),
            "progress_percentage": round(progress_percentage, 1),
            "days_remaining": days_remaining,
            "current_streak": self._calculate_current_streak()
        }
    
    def _calculate_current_streak(self) -> int:
        """
        Calculate current streak of administered doses.
        
        Returns:
            Current streak count
        """
        streak = 0
        today = datetime.now().date()
        
        # Check recent history in reverse order
        for entry in reversed(self.peptide_history):
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            days_diff = (today - entry_date).days
            
            if days_diff <= 1 and entry.get("administered", False):
                streak += 1
            else:
                break
        
        return streak
    
    def get_upcoming_peptide_doses(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming peptide doses for the next N days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming dose information
        """
        upcoming = []
        today = datetime.now()
        
        for i in range(days):
            check_date = today + timedelta(days=i)
            dose_info = self.get_today_peptide_dose(check_date)
            if dose_info:
                upcoming.append(dose_info)
        
        return upcoming
    
    def export_peptide_history(self, format: str = "json") -> str:
        """
        Export peptide administration history.
        
        Args:
            format: Export format ("json", "csv", "yaml")
            
        Returns:
            Exported data as string
        """
        import json
        
        export_data = {
            "protocol_info": self.peptide_schedule.get("peptide_protocol", {}),
            "administration_history": self.peptide_history,
            "progress": self.get_peptide_progress()
        }
        
        if format == "json":
            return json.dumps(export_data, indent=2)
        elif format == "yaml":
            return yaml.dump(export_data, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def reset_peptide_history(self):
        """Reset peptide administration history."""
        self.peptide_history.clear()
        self.logger.info("Peptide administration history reset")
    
    def get_schedule_info(self) -> Dict[str, Any]:
        """
        Get information about available schedules.
        
        Returns:
            Dictionary with schedule information
        """
        info = {
            "active_schedule": self.active_schedule,
            "available_schedules": [],
            "peptide_schedule_loaded": self.peptide_schedule is not None
        }
        
        for schedule_id, filename in self.schedule_files.items():
            file_path = self.config_dir / filename
            info["available_schedules"].append({
                "id": schedule_id,
                "filename": filename,
                "exists": file_path.exists(),
                "active": schedule_id == self.active_schedule
            })
        
        return info


def create_peptide_scheduler(config_dir: str = "config", **kwargs) -> PeptideScheduler:
    """
    Factory function to create a peptide scheduler instance.
    
    Args:
        config_dir: Directory containing schedule files
        **kwargs: Additional arguments for PeptideScheduler
        
    Returns:
        Configured PeptideScheduler instance
    """
    return PeptideScheduler(config_dir=config_dir, **kwargs) 