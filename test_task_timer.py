#!/usr/bin/env python3
"""
Test Script for Task Timer Functionality
========================================

This script demonstrates the new task timer and adaptive time management features.
"""

import sys
import time
from pathlib import Path

# Add modules to path
modules_path = str(Path(__file__).parent / "raspberry-pi-day-planner" / "modules")
sys.path.append(modules_path)

try:
    from task_timer import TaskTimer, AdaptiveTimeManager
    print("✅ Successfully imported TaskTimer and AdaptiveTimeManager")
except Exception as e:
    print(f"❌ Failed to import TaskTimer: {e}")
    sys.exit(1)

def test_task_timer():
    """Test the task timer functionality."""
    print("\n🧪 Testing Task Timer Functionality")
    print("=" * 50)
    
    # Initialize task timer
    task_timer = TaskTimer()
    adaptive_manager = AdaptiveTimeManager()
    
    # Create a sample task
    sample_task = {
        'title': 'Test Task',
        'duration': 2,  # 2 minutes for testing
        'priority': 2,
        'completed': False
    }
    
    print(f"📋 Starting timer for: {sample_task['title']}")
    print(f"⏰ Duration: {sample_task['duration']} minutes")
    
    # Start timer
    task_timer.start_timer(sample_task, sample_task['duration'])
    
    # Monitor timer for 10 seconds
    for i in range(10):
        time_remaining = task_timer.get_time_remaining()
        formatted_time = task_timer.get_formatted_time()
        print(f"⏱️ Time remaining: {formatted_time} ({time_remaining}s)")
        time.sleep(1)
    
    # Stop timer
    task_timer.stop_timer()
    print("⏹️ Timer stopped")

def test_adaptive_time_manager():
    """Test the adaptive time manager functionality."""
    print("\n🧪 Testing Adaptive Time Manager")
    print("=" * 50)
    
    adaptive_manager = AdaptiveTimeManager()
    
    # Create sample tasks
    tasks = [
        {'title': 'High Priority Task', 'duration': 30, 'priority': 1},
        {'title': 'Medium Priority Task', 'duration': 20, 'priority': 2},
        {'title': 'Low Priority Task', 'duration': 15, 'priority': 4},  # Will be reduced
        {'title': 'Another Low Priority', 'duration': 10, 'priority': 5}
    ]
    
    # Simulate a missed task
    missed_task = {'title': 'Missed Task', 'duration': 15, 'priority': 2}
    
    print("📋 Original tasks:")
    for task in tasks:
        print(f"  - {task['title']}: {task['duration']}min (Priority {task['priority']})")
    
    # Apply adaptive adjustment
    adjusted_tasks = adaptive_manager.adjust_task_times(tasks, missed_task)
    
    print("\n📋 After adaptive adjustment:")
    for task in adjusted_tasks:
        if task.get('time_adjusted'):
            print(f"  - {task['title']}: {task['original_duration']}min → {task['duration']}min (ADJUSTED)")
        else:
            print(f"  - {task['title']}: {task['duration']}min (unchanged)")
    
    # Show recent adjustments
    recent_adjustments = adaptive_manager.get_recent_adjustments()
    if recent_adjustments:
        print(f"\n📊 Recent adjustments: {len(recent_adjustments)}")
        for adj in recent_adjustments:
            alert_msg = adaptive_manager.create_adjustment_alert(adj)
            print(f"  - {alert_msg}")

def test_backlog_functionality():
    """Test the backlog functionality."""
    print("\n🧪 Testing Backlog Functionality")
    print("=" * 50)
    
    task_timer = TaskTimer("test_backlog.json")
    
    # Simulate some overdue tasks
    overdue_tasks = [
        {'title': 'Missed Morning Exercise', 'id': 'task_001'},
        {'title': 'Skipped Meditation', 'id': 'task_002'},
        {'title': 'Incomplete Reading', 'id': 'task_003'}
    ]
    
    print("📋 Simulating overdue tasks...")
    for task in overdue_tasks:
        task_timer._save_to_backlog(task['id'], task['title'], "User was busy")
    
    # Show backlog
    backlog = task_timer.get_backlog()
    print(f"\n📊 Backlog contains {len(backlog)} overdue tasks:")
    for task_id, entry in backlog.items():
        print(f"  - {entry['task_title']} (ID: {task_id})")
        print(f"    Reason: {entry['reason']}")
        print(f"    Timestamp: {entry['timestamp']}")
    
    # Clear one entry
    if backlog:
        first_task_id = list(backlog.keys())[0]
        task_timer.clear_backlog_entry(first_task_id)
        print(f"\n🗑️ Cleared backlog entry: {first_task_id}")
        
        updated_backlog = task_timer.get_backlog()
        print(f"📊 Backlog now contains {len(updated_backlog)} tasks")

def main():
    """Run all tests."""
    print("🚀 Task Timer and Adaptive Time Manager Test Suite")
    print("=" * 60)
    
    try:
        # Test task timer
        test_task_timer()
        
        # Test adaptive time manager
        test_adaptive_time_manager()
        
        # Test backlog functionality
        test_backlog_functionality()
        
        print("\n✅ All tests completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("  - Countdown timer with voice alerts")
        print("  - Adaptive time adjustment for missed tasks")
        print("  - Backlog tracking for overdue tasks")
        print("  - Intelligent priority-based time redistribution")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 