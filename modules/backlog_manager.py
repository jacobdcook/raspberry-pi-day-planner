import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class BacklogManager:
    def __init__(self, backlog_file="task_backlog.json"):
        self.backlog_file = backlog_file
        self.backlog_tasks = self.load_backlog()
    
    def load_backlog(self):
        """Load backlog tasks from JSON file."""
        try:
            if os.path.exists(self.backlog_file):
                with open(self.backlog_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both old format (list) and new format (dict with tasks key)
                    if isinstance(data, dict) and 'tasks' in data:
                        tasks = data['tasks']
                        print(f"✅ Loaded {len(tasks)} backlog tasks")
                        return tasks
                    elif isinstance(data, list):
                        print(f"✅ Loaded {len(data)} backlog tasks")
                        return data
                    else:
                        print("⚠️ Unknown backlog format")
                        return []
            else:
                print("📋 No existing backlog file found")
                return []
        except Exception as e:
            print(f"❌ Error loading backlog: {e}")
            return []
    
    def save_backlog(self):
        """Save backlog tasks to JSON file."""
        try:
            with open(self.backlog_file, 'w', encoding='utf-8') as f:
                json.dump(self.backlog_tasks, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {len(self.backlog_tasks)} backlog tasks")
        except Exception as e:
            print(f"❌ Error saving backlog: {e}")
    
    def add_to_backlog(self, task, reason="", original_date=None):
        """Add a task to the backlog."""
        if original_date is None:
            original_date = datetime.now().strftime("%Y-%m-%d")
        
        backlog_entry = {
            'id': f"backlog_{datetime.now().timestamp()}",
            'task_title': task.get('title', 'Unknown Task'),
            'task_notes': task.get('notes', ''),
            'original_date': original_date,
            'backlog_date': datetime.now().strftime("%Y-%m-%d"),
            'reason': reason,
            'priority': task.get('priority', 3),
            'completed': False,
            'completed_date': None,
            'created_at': datetime.now().isoformat()
        }
        
        self.backlog_tasks.append(backlog_entry)
        self.save_backlog()
        
        print(f"📋 Added to backlog: {task.get('title', 'Unknown Task')}")
        return backlog_entry['id']
    
    def get_backlog_tasks(self, include_completed=False):
        """Get backlog tasks, optionally including completed ones."""
        if include_completed:
            return self.backlog_tasks
        else:
            return [task for task in self.backlog_tasks if not task.get('completed', False)]
    
    def get_backlog_by_priority(self, priority=None):
        """Get backlog tasks filtered by priority."""
        tasks = self.get_backlog_tasks()
        if priority is not None:
            return [task for task in tasks if task.get('priority', 3) == priority]
        return tasks
    
    def get_backlog_by_date_range(self, start_date, end_date):
        """Get backlog tasks within a date range."""
        tasks = self.get_backlog_tasks()
        filtered_tasks = []
        
        for task in tasks:
            task_date = task.get('original_date')
            if task_date and start_date <= task_date <= end_date:
                filtered_tasks.append(task)
        
        return filtered_tasks
    
    def complete_backlog_task(self, task_id):
        """Mark a backlog task as completed."""
        for task in self.backlog_tasks:
            if task.get('id') == task_id:
                task['completed'] = True
                task['completed_date'] = datetime.now().strftime("%Y-%m-%d")
                self.save_backlog()
                print(f"✅ Completed backlog task: {task.get('task_title', 'Unknown')}")
                return True
        
        print(f"❌ Backlog task not found: {task_id}")
        return False
    
    def remove_backlog_task(self, task_id):
        """Remove a task from the backlog."""
        for i, task in enumerate(self.backlog_tasks):
            if task.get('id') == task_id:
                removed_task = self.backlog_tasks.pop(i)
                self.save_backlog()
                print(f"🗑️ Removed backlog task: {removed_task.get('task_title', 'Unknown')}")
                return True
        
        print(f"❌ Backlog task not found: {task_id}")
        return False
    
    def update_backlog_task(self, task_id, updates):
        """Update a backlog task with new information."""
        for task in self.backlog_tasks:
            if task.get('id') == task_id:
                task.update(updates)
                task['updated_at'] = datetime.now().isoformat()
                self.save_backlog()
                print(f"✏️ Updated backlog task: {task.get('task_title', 'Unknown')}")
                return True
        
        print(f"❌ Backlog task not found: {task_id}")
        return False
    
    def get_backlog_stats(self):
        """Get statistics about the backlog."""
        total_tasks = len(self.backlog_tasks)
        completed_tasks = len([t for t in self.backlog_tasks if t.get('completed', False)])
        pending_tasks = total_tasks - completed_tasks
        
        # Priority distribution
        priority_stats = {}
        for task in self.backlog_tasks:
            priority = task.get('priority', 3)
            if priority not in priority_stats:
                priority_stats[priority] = 0
            priority_stats[priority] += 1
        
        # Age distribution
        today = datetime.now().date()
        age_stats = {'recent': 0, 'week_old': 0, 'month_old': 0, 'older': 0}
        
        for task in self.backlog_tasks:
            if not task.get('completed', False):
                try:
                    task_date = datetime.strptime(task.get('original_date', ''), '%Y-%m-%d').date()
                    days_old = (today - task_date).days
                    
                    if days_old <= 3:
                        age_stats['recent'] += 1
                    elif days_old <= 7:
                        age_stats['week_old'] += 1
                    elif days_old <= 30:
                        age_stats['month_old'] += 1
                    else:
                        age_stats['older'] += 1
                except:
                    age_stats['older'] += 1
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'priority_distribution': priority_stats,
            'age_distribution': age_stats
        }
    
    def get_oldest_backlog_tasks(self, limit=5):
        """Get the oldest pending backlog tasks."""
        pending_tasks = self.get_backlog_tasks()
        
        # Sort by original date (oldest first)
        pending_tasks.sort(key=lambda x: x.get('original_date', ''))
        
        return pending_tasks[:limit]
    
    def get_high_priority_backlog_tasks(self, limit=10):
        """Get high priority backlog tasks."""
        high_priority_tasks = [t for t in self.get_backlog_tasks() if t.get('priority', 3) <= 2]
        
        # Sort by priority (lowest number first) then by original date
        high_priority_tasks.sort(key=lambda x: (x.get('priority', 3), x.get('original_date', '')))
        
        return high_priority_tasks[:limit]
    
    def cleanup_old_completed_tasks(self, days_old=30):
        """Remove completed tasks older than specified days."""
        cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime("%Y-%m-%d")
        
        original_count = len(self.backlog_tasks)
        self.backlog_tasks = [
            task for task in self.backlog_tasks
            if not (task.get('completed', False) and 
                   task.get('completed_date', '') < cutoff_date)
        ]
        
        removed_count = original_count - len(self.backlog_tasks)
        if removed_count > 0:
            self.save_backlog()
            print(f"🧹 Cleaned up {removed_count} old completed tasks")
        
        return removed_count
    
    def export_backlog(self, filename=None):
        """Export backlog to JSON file."""
        if filename is None:
            filename = f"backlog_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'backlog_tasks': self.backlog_tasks,
                'stats': self.get_backlog_stats()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Backlog exported to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exporting backlog: {e}")
            return False
    
    def import_backlog(self, filename):
        """Import backlog from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'backlog_tasks' in data:
                self.backlog_tasks = data['backlog_tasks']
                self.save_backlog()
                print(f"✅ Imported {len(self.backlog_tasks)} backlog tasks from {filename}")
                return True
            else:
                print(f"❌ Invalid backlog file format: {filename}")
                return False
        except Exception as e:
            print(f"❌ Error importing backlog: {e}")
            return False
    
    def reset_backlog(self):
        """Reset the entire backlog."""
        self.backlog_tasks = []
        self.save_backlog()
        print("🔄 Backlog reset") 