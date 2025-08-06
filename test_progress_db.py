#!/usr/bin/env python3
"""
Test Progress Database
=====================

Demonstrates the progress database functionality with sample data.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from progress_db import ProgressDatabase, save_today_progress

def test_progress_database():
    """Test the progress database functionality."""
    print("🧪 Testing Progress Database")
    print("=" * 40)
    
    # Create database
    db = ProgressDatabase("test_progress.db")
    
    # Sample task data
    sample_tasks = [
        {
            'title': 'Wake Up & Hydrate',
            'time': '06:45',
            'completed': True,
            'was_catch_up': False
        },
        {
            'title': 'Take Supplements',
            'time': '07:00',
            'completed': True,
            'was_catch_up': False
        },
        {
            'title': 'Cold Shower',
            'time': '07:15',
            'skipped': True,
            'was_catch_up': False
        },
        {
            'title': 'Breakfast',
            'time': '07:30',
            'completed': False,
            'skipped': False,
            'was_catch_up': False
        }
    ]
    
    # Save today's progress
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Saving progress for {today}")
    
    success = save_today_progress(sample_tasks, "test_progress.db")
    if success:
        print("✅ Progress saved successfully")
    else:
        print("❌ Failed to save progress")
    
    # Get daily summary
    summary = db.get_daily_summary(today)
    if summary:
        print(f"\n📊 Daily Summary for {today}:")
        print(f"   Total Tasks: {summary['total_tasks']}")
        print(f"   Completed: {summary['completed_tasks']}")
        print(f"   Skipped: {summary['skipped_tasks']}")
        print(f"   Completion Rate: {summary['completion_percentage']:.1f}%")
        print(f"   Skip Rate: {summary['skip_percentage']:.1f}%")
    
    # Get analytics data
    analytics = db.get_analytics_data(days=7)
    print(f"\n📈 Analytics (Last 7 days):")
    print(f"   Total Days: {analytics['total_days']}")
    print(f"   Average Completion: {analytics['average_completion']:.1f}%")
    
    # Get database stats
    stats = db.get_database_stats()
    print(f"\n📋 Database Statistics:")
    print(f"   Daily Summaries: {stats['total_daily_summaries']}")
    print(f"   Task Records: {stats['total_task_records']}")
    print(f"   Date Range: {stats['date_range']['min']} to {stats['date_range']['max']}")
    print(f"   Average Completion: {stats['average_completion_percentage']:.1f}%")
    
    # Export to JSON
    export_success = db.export_to_json("test_progress_export.json")
    if export_success:
        print(f"\n📄 Data exported to test_progress_export.json")
    
    print("\n✅ Progress database test completed!")

if __name__ == "__main__":
    test_progress_database() 