#!/usr/bin/env python3
"""
Progress Database Module
=======================

Tracks daily task statistics and exports them to SQLite database for analytics.
Provides persistent data for long-term productivity tracking and visualization.

Features:
- Daily summary tracking (total, completed, skipped tasks)
- Automatic percentage calculations
- SQLite database storage
- Export functionality
- Analytics data preparation
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class ProgressDatabase:
    def __init__(self, db_path="progress.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create daily_summary table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_summary (
                        date TEXT PRIMARY KEY,
                        total_tasks INTEGER,
                        completed_tasks INTEGER,
                        skipped_tasks INTEGER,
                        completion_rate REAL,
                        skip_rate REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create task_backlog table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS task_backlog (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_title TEXT,
                        task_notes TEXT,
                        original_date TEXT,
                        backlog_date TEXT,
                        reason TEXT,
                        completed BOOLEAN DEFAULT FALSE,
                        completed_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create mood_tracker table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS mood_tracker (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        mood TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create badges table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS badges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        badge_emoji TEXT,
                        badge_name TEXT,
                        earned_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
    
    def save_daily_summary(self, date, total_tasks, completed_tasks, skipped_tasks):
        """Save daily progress summary."""
        try:
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            skip_rate = (skipped_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_summary 
                    (date, total_tasks, completed_tasks, skipped_tasks, completion_rate, skip_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (date, total_tasks, completed_tasks, skipped_tasks, completion_rate, skip_rate))
                conn.commit()
                print(f"✅ Daily summary saved for {date}")
        except Exception as e:
            print(f"❌ Error saving daily summary: {e}")
    
    def get_daily_summary(self, date):
        """Get daily summary for a specific date."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM daily_summary WHERE date = ?
                ''', (date,))
                return cursor.fetchone()
        except Exception as e:
            print(f"❌ Error getting daily summary: {e}")
            return None
    
    def get_last_7_days_summary(self):
        """Get summary for the last 7 days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM daily_summary 
                    WHERE date >= date('now', '-6 days')
                    ORDER BY date DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting 7-day summary: {e}")
            return []
    
    def add_to_backlog(self, task_title, task_notes, original_date, reason=""):
        """Add a task to the backlog."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO task_backlog (task_title, task_notes, original_date, backlog_date, reason)
                    VALUES (?, ?, ?, ?, ?)
                ''', (task_title, task_notes, original_date, datetime.now().strftime("%Y-%m-%d"), reason))
                conn.commit()
                print(f"✅ Task added to backlog: {task_title}")
        except Exception as e:
            print(f"❌ Error adding to backlog: {e}")
    
    def get_backlog_tasks(self):
        """Get all incomplete backlog tasks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM task_backlog 
                    WHERE completed = FALSE
                    ORDER BY original_date ASC
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting backlog tasks: {e}")
            return []
    
    def complete_backlog_task(self, task_id):
        """Mark a backlog task as completed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE task_backlog 
                    SET completed = TRUE, completed_date = ?
                    WHERE id = ?
                ''', (datetime.now().strftime("%Y-%m-%d"), task_id))
                conn.commit()
                print(f"✅ Backlog task {task_id} marked as completed")
        except Exception as e:
            print(f"❌ Error completing backlog task: {e}")
    
    def save_mood(self, date, mood, notes=""):
        """Save mood tracking data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO mood_tracker (date, mood, notes)
                    VALUES (?, ?, ?)
                ''', (date, mood, notes))
                conn.commit()
                print(f"✅ Mood saved for {date}: {mood}")
        except Exception as e:
            print(f"❌ Error saving mood: {e}")
    
    def get_mood_history(self, days=7):
        """Get mood history for the last N days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM mood_tracker 
                    WHERE date >= date('now', ?)
                    ORDER BY date DESC
                ''', (f'-{days-1} days',))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting mood history: {e}")
            return []
    
    def save_badge(self, badge_emoji, badge_name):
        """Save an earned badge."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO badges (badge_emoji, badge_name, earned_date)
                    VALUES (?, ?, ?)
                ''', (badge_emoji, badge_name, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                print(f"✅ Badge saved: {badge_emoji} {badge_name}")
        except Exception as e:
            print(f"❌ Error saving badge: {e}")
    
    def get_earned_badges(self):
        """Get all earned badges."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM badges ORDER BY earned_date DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting badges: {e}")
            return []
    
    def export_to_json(self, filename="progress_export.json"):
        """Export all data to JSON file."""
        try:
            export_data = {
                "daily_summaries": [],
                "backlog_tasks": [],
                "mood_history": [],
                "badges": [],
                "export_date": datetime.now().isoformat()
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Export daily summaries
                cursor.execute('SELECT * FROM daily_summary ORDER BY date DESC')
                export_data["daily_summaries"] = [dict(zip([col[0] for col in cursor.description], row)) 
                                                for row in cursor.fetchall()]
                
                # Export backlog tasks
                cursor.execute('SELECT * FROM task_backlog ORDER BY created_at DESC')
                export_data["backlog_tasks"] = [dict(zip([col[0] for col in cursor.description], row)) 
                                              for row in cursor.fetchall()]
                
                # Export mood history
                cursor.execute('SELECT * FROM mood_tracker ORDER BY date DESC')
                export_data["mood_history"] = [dict(zip([col[0] for col in cursor.description], row)) 
                                             for row in cursor.fetchall()]
                
                # Export badges
                cursor.execute('SELECT * FROM badges ORDER BY earned_date DESC')
                export_data["badges"] = [dict(zip([col[0] for col in cursor.description], row)) 
                                       for row in cursor.fetchall()]
            
            # Save to JSON file
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Data exported to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return False 