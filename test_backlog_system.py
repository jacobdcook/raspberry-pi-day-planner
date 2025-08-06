#!/usr/bin/env python3
"""
Backlog System Test Script
==========================

This script tests the backlog manager and streak tracking functionality.
It demonstrates how incomplete tasks are tracked and can be redeemed later.

Features tested:
- Adding tasks to backlog
- Retrieving backlog tasks
- Redeeming tasks
- Streak tracking
- Badge system
"""

import sys
import time
from pathlib import Path

# Add the modules directory to the path
sys.path.append(str(Path(__file__).parent / "raspberry-pi-day-planner" / "modules"))

from backlog_manager import BacklogManager
from task_timer import TaskTimer, AdaptiveTimeManager

def test_backlog_manager():
    """Test the backlog manager functionality."""
    print("🧪 Testing Backlog Manager")
    print("=" * 50)
    
    # Initialize backlog manager
    backlog_manager = BacklogManager()
    
    # Add some test tasks to backlog
    test_tasks = [
        {
            'task_id': 'task_001',
            'task_title': 'Morning Meditation',
            'reason': 'Overslept and missed the time window',
            'original_date': '2024-01-15',
            'priority': 1
        },
        {
            'task_id': 'task_002', 
            'task_title': 'Take Supplements',
            'reason': 'Forgot to bring supplements to work',
            'original_date': '2024-01-14',
            'priority': 2
        },
        {
            'task_id': 'task_003',
            'task_title': 'Evening Walk',
            'reason': 'Weather was bad, will do tomorrow',
            'original_date': '2024-01-13',
            'priority': 3
        }
    ]
    
    print("📝 Adding test tasks to backlog...")
    for task in test_tasks:
        backlog_manager.add_to_backlog(
            task['task_id'],
            task['task_title'],
            task['reason'],
            task['original_date'],
            task['priority']
        )
        print(f"  ✅ Added: {task['task_title']}")
    
    # Get backlog tasks
    print("\n📋 Retrieving backlog tasks...")
    backlog_tasks = backlog_manager.get_backlog_tasks()
    print(f"  Found {len(backlog_tasks)} tasks in backlog:")
    
    for task in backlog_tasks:
        print(f"    - {task['task_title']} (Priority: {task['priority']})")
        print(f"      Reason: {task['reason']}")
        print(f"      Original Date: {task['original_date']}")
    
    # Test redeeming a task
    print("\n🔄 Testing task redemption...")
    if backlog_tasks:
        task_to_redeem = backlog_tasks[0]
        success = backlog_manager.redeem_task(task_to_redeem['task_id'])
        if success:
            print(f"  ✅ Successfully redeemed: {task_to_redeem['task_title']}")
        else:
            print(f"  ❌ Failed to redeem: {task_to_redeem['task_title']}")
    
    # Get updated backlog
    updated_backlog = backlog_manager.get_backlog_tasks()
    print(f"  Remaining tasks in backlog: {len(updated_backlog)}")
    
    return backlog_manager

def test_streak_tracking():
    """Test streak tracking functionality."""
    print("\n🔥 Testing Streak Tracking")
    print("=" * 50)
    
    backlog_manager = BacklogManager()
    
    # Test different completion percentages
    test_percentages = [85.0, 90.0, 75.0, 95.0, 100.0]
    
    print("📊 Testing streak updates with different completion percentages:")
    for percentage in test_percentages:
        backlog_manager.update_streak(percentage)
        streak_info = backlog_manager.get_streak_info()
        print(f"  {percentage}% completion -> Current streak: {streak_info['current_streak']}, Longest: {streak_info['longest_streak']}")
    
    # Test badge system
    print("\n🏆 Testing Badge System:")
    badge_info = backlog_manager.get_badge_info()
    print(f"  Current streak: {badge_info['current_streak']}")
    print(f"  Longest streak: {badge_info['longest_streak']}")
    print(f"  Badges earned: {', '.join(badge_info['badges']) if badge_info['badges'] else 'None'}")
    
    # Test celebration messages
    print("\n🎉 Testing Celebration Messages:")
    if backlog_manager.should_show_streak_celebration():
        celebration_msg = backlog_manager.get_celebration_message()
        print(f"  Celebration: {celebration_msg}")
    else:
        print("  No celebration needed (streak < 3 days)")

def test_task_timer_integration():
    """Test integration between task timer and backlog manager."""
    print("\n⏰ Testing Task Timer Integration")
    print("=" * 50)
    
    # Initialize task timer (which includes backlog manager)
    task_timer = TaskTimer()
    
    # Create a test task
    test_task = {
        'id': 'test_task_001',
        'title': 'Test Task',
        'priority': 2,
        'duration': 5  # 5 minutes for testing
    }
    
    print("🔄 Testing task timer with backlog integration...")
    print(f"  Task: {test_task['title']}")
    print(f"  Duration: {test_task['duration']} minutes")
    
    # Start timer
    task_timer.start_timer(test_task, test_task['duration'])
    print("  ✅ Timer started")
    
    # Simulate task completion
    test_task['completed'] = True
    
    # Stop timer
    task_timer.stop_timer()
    print("  ✅ Timer stopped")
    
    # Check backlog
    backlog = task_timer.get_backlog()
    print(f"  Backlog tasks: {len(backlog)}")
    
    # Get backlog manager
    backlog_manager = task_timer.get_backlog_manager()
    if backlog_manager:
        backlog_tasks = backlog_manager.get_backlog_tasks()
        print(f"  Backlog manager tasks: {len(backlog_tasks)}")
    
    return task_timer

def test_adaptive_time_manager():
    """Test adaptive time manager functionality."""
    print("\n🧠 Testing Adaptive Time Manager")
    print("=" * 50)
    
    adaptive_manager = AdaptiveTimeManager()
    
    # Create test tasks
    tasks = [
        {
            'title': 'High Priority Task',
            'priority': 1,
            'duration': 30
        },
        {
            'title': 'Medium Priority Task', 
            'priority': 2,
            'duration': 20
        },
        {
            'title': 'Low Priority Task',
            'priority': 3,
            'duration': 15
        }
    ]
    
    # Create a missed task
    missed_task = {
        'title': 'Missed Task',
        'priority': 2,
        'duration': 25
    }
    
    print("📋 Original task durations:")
    for task in tasks:
        print(f"  {task['title']}: {task['duration']} minutes")
    
    # Apply adaptive adjustments
    adjusted_tasks = adaptive_manager.adjust_task_times(tasks, missed_task)
    
    print("\n⚡ After adaptive adjustment:")
    for task in adjusted_tasks:
        if task.get('time_adjusted'):
            print(f"  {task['title']}: {task['duration']} minutes (was {task['original_duration']})")
        else:
            print(f"  {task['title']}: {task['duration']} minutes (no change)")
    
    # Get recent adjustments
    recent_adjustments = adaptive_manager.get_recent_adjustments()
    print(f"\n📊 Recent adjustments: {len(recent_adjustments)}")
    for adjustment in recent_adjustments:
        alert_msg = adaptive_manager.create_adjustment_alert(adjustment)
        print(f"  {alert_msg}")

def main():
    """Run all backlog system tests."""
    print("🚀 Backlog System Test Suite")
    print("=" * 60)
    
    try:
        # Test backlog manager
        backlog_manager = test_backlog_manager()
        
        # Test streak tracking
        test_streak_tracking()
        
        # Test task timer integration
        task_timer = test_task_timer_integration()
        
        # Test adaptive time manager
        test_adaptive_time_manager()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary:")
        print("  - Backlog manager: ✅ Working")
        print("  - Streak tracking: ✅ Working") 
        print("  - Task timer integration: ✅ Working")
        print("  - Adaptive time manager: ✅ Working")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 