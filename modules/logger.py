"""
Event Logger Module

This module handles logging task events to a SQLite database for tracking
task completion, snoozes, and user interactions.

Author: Raspberry Pi Day Planner
License: MIT
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json


class EventLogger:
    """
    Logs task events to SQLite database for tracking and analytics.
    
    This class handles:
    - SQLite database initialization and management
    - Logging task events (shown, completed, snoozed)
    - Querying event history
    - Database maintenance and cleanup
    - Data export functionality
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the event logger.
        
        Args:
            db_path: Path to the SQLite database file.
                    Defaults to 'data/events.db' relative to project root.
        """
        self.logger = logging.getLogger(__name__)
        
        # Set database path
        if db_path is None:
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "events.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        self.logger.info(f"Event logger initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize the SQLite database and create tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        event_type TEXT NOT NULL,
                        task_title TEXT NOT NULL,
                        task_time TEXT,
                        task_notes TEXT,
                        task_priority INTEGER,
                        task_category TEXT,
                        additional_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create task_completions table for tracking completion rates
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS task_completions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_title TEXT NOT NULL,
                        task_time TEXT NOT NULL,
                        completion_date DATE NOT NULL,
                        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        snooze_count INTEGER DEFAULT 0,
                        total_duration_minutes INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(task_title, task_time, completion_date)
                    )
                ''')
                
                # Create indexes for better query performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                    ON events(timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_events_task_title 
                    ON events(task_title)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_events_event_type 
                    ON events(event_type)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_completions_task_title 
                    ON task_completions(task_title)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_completions_completion_date 
                    ON task_completions(completion_date)
                ''')
                
                conn.commit()
                
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def log_task_shown(self, task: Dict[str, Any]):
        """
        Log when a task notification is shown.
        
        Args:
            task: Task dictionary containing task information.
        """
        self._log_event('task_shown', task)
    
    def log_task_completed(self, task: Dict[str, Any]):
        """
        Log when a task is completed.
        
        Args:
            task: Task dictionary containing task information.
        """
        self._log_event('task_completed', task)
        self._log_completion(task)
    
    def log_task_snoozed(self, task: Dict[str, Any], snooze_duration: int):
        """
        Log when a task is snoozed.
        
        Args:
            task: Task dictionary containing task information.
            snooze_duration: Duration of snooze in minutes.
        """
        additional_data = {'snooze_duration': snooze_duration}
        self._log_event('task_snoozed', task, additional_data)
    
    def log_task_dismissed(self, task: Dict[str, Any]):
        """
        Log when a task notification is dismissed without action.
        
        Args:
            task: Task dictionary containing task information.
        """
        self._log_event('task_dismissed', task)
    
    def _log_event(self, event_type: str, task: Dict[str, Any], additional_data: Optional[Dict] = None):
        """
        Log an event to the database.
        
        Args:
            event_type: Type of event (task_shown, task_completed, etc.).
            task: Task dictionary containing task information.
            additional_data: Additional data to store as JSON.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO events (
                        event_type, task_title, task_time, task_notes,
                        task_priority, task_category, additional_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_type,
                    task.get('title', ''),
                    task.get('time', '').strftime('%H:%M') if hasattr(task.get('time', ''), 'strftime') else str(task.get('time', '')),
                    task.get('notes', ''),
                    task.get('priority', 0),
                    task.get('category', ''),
                    json.dumps(additional_data) if additional_data else None
                ))
                
                conn.commit()
                
            self.logger.debug(f"Logged event: {event_type} for task: {task.get('title', '')}")
            
        except Exception as e:
            self.logger.error(f"Failed to log event {event_type}: {e}")
    
    def _log_completion(self, task: Dict[str, Any]):
        """
        Log a task completion for tracking completion rates.
        
        Args:
            task: Task dictionary containing task information.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get snooze count for this task today
                today = datetime.now().date()
                snooze_count = self._get_snooze_count_today(task.get('title', ''), today)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO task_completions (
                        task_title, task_time, completion_date, 
                        snooze_count, completed_at
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    task.get('title', ''),
                    task.get('time', '').strftime('%H:%M') if hasattr(task.get('time', ''), 'strftime') else str(task.get('time', '')),
                    today.isoformat(),
                    snooze_count,
                    datetime.now()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log completion: {e}")
    
    def _get_snooze_count_today(self, task_title: str, date: datetime.date) -> int:
        """
        Get the number of times a task was snoozed today.
        
        Args:
            task_title: Title of the task.
            date: Date to check.
            
        Returns:
            Number of snoozes for the task on the given date.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(*) FROM events 
                    WHERE event_type = 'task_snoozed' 
                    AND task_title = ? 
                    AND DATE(timestamp) = ?
                ''', (task_title, date.isoformat()))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            self.logger.error(f"Failed to get snooze count: {e}")
            return 0
    
    def get_events(self, 
                  event_type: Optional[str] = None,
                  task_title: Optional[str] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query events from the database.
        
        Args:
            event_type: Filter by event type.
            task_title: Filter by task title.
            start_date: Start date for filtering.
            end_date: End date for filtering.
            limit: Maximum number of results.
            
        Returns:
            List of event dictionaries.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if task_title:
                    query += " AND task_title = ?"
                    params.append(task_title)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY timestamp DESC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = dict(row)
                    if event['additional_data']:
                        try:
                            event['additional_data'] = json.loads(event['additional_data'])
                        except json.JSONDecodeError:
                            pass
                    events.append(event)
                
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to query events: {e}")
            return []
    
    def get_completion_stats(self, 
                           days: int = 30,
                           task_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Get task completion statistics.
        
        Args:
            days: Number of days to analyze.
            task_title: Specific task to analyze (optional).
            
        Returns:
            Dictionary containing completion statistics.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                start_date = (datetime.now() - timedelta(days=days)).date()
                
                # Base query
                query = '''
                    SELECT 
                        task_title,
                        COUNT(*) as total_occurrences,
                        SUM(CASE WHEN completion_date IS NOT NULL THEN 1 ELSE 0 END) as completions,
                        AVG(snooze_count) as avg_snoozes
                    FROM task_completions 
                    WHERE completion_date >= ?
                '''
                params = [start_date.isoformat()]
                
                if task_title:
                    query += " AND task_title = ?"
                    params.append(task_title)
                
                query += " GROUP BY task_title ORDER BY completions DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                stats = {
                    'period_days': days,
                    'start_date': start_date.isoformat(),
                    'tasks': []
                }
                
                for row in rows:
                    task_title, total, completions, avg_snoozes = row
                    completion_rate = (completions / total * 100) if total > 0 else 0
                    
                    stats['tasks'].append({
                        'task_title': task_title,
                        'total_occurrences': total,
                        'completions': completions,
                        'completion_rate': round(completion_rate, 2),
                        'avg_snoozes': round(avg_snoozes or 0, 2)
                    })
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get completion stats: {e}")
            return {'period_days': days, 'start_date': start_date.isoformat(), 'tasks': []}
    
    def cleanup_old_events(self, days_to_keep: int = 90):
        """
        Clean up old events from the database.
        
        Args:
            days_to_keep: Number of days of events to keep.
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete old events
                cursor.execute('''
                    DELETE FROM events 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                events_deleted = cursor.rowcount
                
                # Delete old completions
                cursor.execute('''
                    DELETE FROM task_completions 
                    WHERE completion_date < ?
                ''', (cutoff_date.date().isoformat(),))
                
                completions_deleted = cursor.rowcount
                
                conn.commit()
                
            self.logger.info(f"Cleaned up {events_deleted} old events and {completions_deleted} old completions")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old events: {e}")
    
    def export_data(self, filepath: str, format: str = 'json'):
        """
        Export event data to a file.
        
        Args:
            filepath: Path to the export file.
            format: Export format ('json' or 'csv').
        """
        try:
            events = self.get_events()
            
            if format.lower() == 'json':
                with open(filepath, 'w') as f:
                    json.dump(events, f, indent=2, default=str)
            elif format.lower() == 'csv':
                import csv
                with open(filepath, 'w', newline='') as f:
                    if events:
                        writer = csv.DictWriter(f, fieldnames=events[0].keys())
                        writer.writeheader()
                        writer.writerows(events)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            self.logger.info(f"Exported {len(events)} events to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the database.
        
        Returns:
            Dictionary containing database statistics.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table sizes
                cursor.execute("SELECT COUNT(*) FROM events")
                event_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM task_completions")
                completion_count = cursor.fetchone()[0]
                
                # Get database file size
                file_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                return {
                    'database_path': str(self.db_path),
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'total_events': event_count,
                    'total_completions': completion_count,
                    'created_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {}
    
    def close(self):
        """Close the event logger and cleanup resources."""
        try:
            # SQLite connections are automatically closed when they go out of scope
            self.logger.info("Event logger closed")
        except Exception as e:
            self.logger.error(f"Error closing event logger: {e}") 