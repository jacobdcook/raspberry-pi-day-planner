import time
from datetime import datetime, timedelta

class AdaptiveTimeManager:
    def __init__(self):
        self.task_history = []
        self.time_adjustments = {}
        self.adaptive_rules = {
            'high_priority': 1.2,  # Increase time for high priority tasks
            'low_priority': 0.8,   # Decrease time for low priority tasks
            'frequent_failure': 1.3,  # Increase time for frequently failed tasks
            'success_streak': 0.9   # Slightly decrease time for successful streaks
        }
    
    def record_task_completion(self, task, actual_duration, was_completed):
        """Record task completion for adaptive learning."""
        record = {
            'task_id': task.get('id', task.get('title', 'unknown')),
            'task_title': task.get('title', 'Unknown'),
            'scheduled_duration': task.get('duration', 15),
            'actual_duration': actual_duration,
            'was_completed': was_completed,
            'priority': task.get('priority', 3),
            'timestamp': datetime.now().isoformat()
        }
        
        self.task_history.append(record)
        
        # Keep only last 100 records
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
        
        print(f"📊 Recorded task: {task.get('title', 'Unknown')} - "
              f"Completed: {was_completed}, Duration: {actual_duration}min")
    
    def calculate_adaptive_duration(self, task):
        """Calculate adaptive duration for a task based on history."""
        task_id = task.get('id', task.get('title', 'unknown'))
        base_duration = task.get('duration', 15)
        
        # Get recent history for this task
        recent_history = [h for h in self.task_history[-20:] 
                         if h['task_id'] == task_id]
        
        if not recent_history:
            return base_duration
        
        # Calculate success rate
        success_rate = sum(1 for h in recent_history if h['was_completed']) / len(recent_history)
        
        # Calculate average actual duration
        avg_duration = sum(h['actual_duration'] for h in recent_history) / len(recent_history)
        
        # Apply adaptive rules
        adjustment_factor = 1.0
        
        # Adjust based on success rate
        if success_rate < 0.5:  # Less than 50% success
            adjustment_factor *= self.adaptive_rules['frequent_failure']
        elif success_rate > 0.8:  # More than 80% success
            adjustment_factor *= self.adaptive_rules['success_streak']
        
        # Adjust based on priority
        priority = task.get('priority', 3)
        if priority <= 1:  # High priority
            adjustment_factor *= self.adaptive_rules['high_priority']
        elif priority >= 4:  # Low priority
            adjustment_factor *= self.adaptive_rules['low_priority']
        
        # Use actual duration if available, otherwise apply adjustment to base
        if avg_duration > 0:
            adaptive_duration = avg_duration * adjustment_factor
        else:
            adaptive_duration = base_duration * adjustment_factor
        
        # Ensure minimum duration
        adaptive_duration = max(5, adaptive_duration)
        
        # Store adjustment for this task
        self.time_adjustments[task_id] = {
            'original_duration': base_duration,
            'adaptive_duration': adaptive_duration,
            'adjustment_factor': adjustment_factor,
            'success_rate': success_rate,
            'avg_duration': avg_duration
        }
        
        print(f"🎯 Adaptive duration for {task.get('title', 'Unknown')}: "
              f"{base_duration}min → {adaptive_duration:.1f}min "
              f"(factor: {adjustment_factor:.2f})")
        
        return int(adaptive_duration)
    
    def get_time_adjustment_info(self, task):
        """Get information about time adjustments for a task."""
        task_id = task.get('id', task.get('title', 'unknown'))
        return self.time_adjustments.get(task_id, {})
    
    def redistribute_time(self, tasks, total_available_time):
        """Redistribute time among tasks based on priority and history."""
        if not tasks:
            return tasks
        
        # Calculate adaptive durations
        adaptive_tasks = []
        total_adaptive_time = 0
        
        for task in tasks:
            adaptive_duration = self.calculate_adaptive_duration(task)
            task['adaptive_duration'] = adaptive_duration
            total_adaptive_time += adaptive_duration
            adaptive_tasks.append(task)
        
        # If total adaptive time exceeds available time, redistribute
        if total_adaptive_time > total_available_time:
            # Sort by priority (lower number = higher priority)
            adaptive_tasks.sort(key=lambda x: x.get('priority', 3))
            
            # Redistribute time, keeping high priority tasks intact
            remaining_time = total_available_time
            for i, task in enumerate(adaptive_tasks):
                if i < len(adaptive_tasks) // 2:  # Keep first half intact
                    task['final_duration'] = task['adaptive_duration']
                    remaining_time -= task['adaptive_duration']
                else:
                    # Reduce time for lower priority tasks
                    reduction_factor = remaining_time / sum(t['adaptive_duration'] for t in adaptive_tasks[i:])
                    task['final_duration'] = int(task['adaptive_duration'] * reduction_factor)
                    remaining_time -= task['final_duration']
        
        else:
            # No redistribution needed
            for task in adaptive_tasks:
                task['final_duration'] = task['adaptive_duration']
        
        return adaptive_tasks
    
    def get_adaptive_insights(self):
        """Get insights about adaptive time management."""
        if not self.task_history:
            return "No task history available for insights."
        
        insights = []
        
        # Most challenging tasks
        task_success_rates = {}
        for record in self.task_history:
            task_id = record['task_id']
            if task_id not in task_success_rates:
                task_success_rates[task_id] = {'completed': 0, 'total': 0}
            
            task_success_rates[task_id]['total'] += 1
            if record['was_completed']:
                task_success_rates[task_id]['completed'] += 1
        
        challenging_tasks = []
        for task_id, stats in task_success_rates.items():
            success_rate = stats['completed'] / stats['total']
            if success_rate < 0.6:  # Less than 60% success
                challenging_tasks.append((task_id, success_rate))
        
        if challenging_tasks:
            challenging_tasks.sort(key=lambda x: x[1])
            insights.append(f"Most challenging tasks: {', '.join(t[0] for t in challenging_tasks[:3])}")
        
        # Time adjustment summary
        total_adjustments = len(self.time_adjustments)
        if total_adjustments > 0:
            avg_adjustment = sum(a['adjustment_factor'] for a in self.time_adjustments.values()) / total_adjustments
            insights.append(f"Average time adjustment factor: {avg_adjustment:.2f}")
        
        return insights
    
    def reset_adaptive_data(self):
        """Reset all adaptive learning data."""
        self.task_history = []
        self.time_adjustments = {}
        print("🔄 Adaptive learning data reset")
    
    def export_adaptive_data(self):
        """Export adaptive learning data for analysis."""
        return {
            'task_history': self.task_history,
            'time_adjustments': self.time_adjustments,
            'adaptive_rules': self.adaptive_rules,
            'export_timestamp': datetime.now().isoformat()
        } 