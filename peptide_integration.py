#!/usr/bin/env python3
"""
Peptide Scheduler Integration

This script demonstrates how to integrate the peptide scheduler with your
Raspberry Pi day planner system. It shows how to:
- Select between different schedules
- Load peptide schedules
- Get today's peptide dose
- Track administration
- View progress

Usage:
    python peptide_integration.py
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the modules directory to the path
sys.path.append(str(Path(__file__).parent / "modules"))

from peptide_scheduler import PeptideScheduler


def main():
    """Main function to demonstrate peptide scheduler functionality."""
    
    print("🧬 Peptide Scheduler Integration Demo")
    print("=" * 50)
    
    # Initialize peptide scheduler
    config_dir = Path(__file__).parent / "config"
    peptide_scheduler = PeptideScheduler(config_dir=str(config_dir))
    
    # Show available schedules
    print("\n📋 Available Schedules:")
    schedule_options = peptide_scheduler.get_schedule_selection_menu()
    
    for option in schedule_options:
        status = "✅" if option["exists"] else "❌"
        active = " (ACTIVE)" if option["active"] else ""
        print(f"  {status} {option['name']}{active}")
        print(f"     Description: {option['description']}")
        print(f"     File: {option['file']}")
        print()
    
    # Load peptide schedule
    print("🔬 Loading Peptide Schedule...")
    if peptide_scheduler.load_peptide_schedule():
        print("✅ Peptide schedule loaded successfully!")
    else:
        print("❌ Failed to load peptide schedule")
        return
    
    # Get today's dose
    print("\n💉 Today's Peptide Dose:")
    today_dose = peptide_scheduler.get_today_peptide_dose()
    
    if today_dose:
        print(f"  Date: {today_dose['date']}")
        print(f"  Time: {today_dose['administration_time']}")
        if today_dose.get('bpc_157'):
            print(f"  BPC-157: {today_dose['bpc_157']}")
        if today_dose.get('tb_500'):
            print(f"  TB-500: {today_dose['tb_500']}")
        if today_dose.get('notes'):
            print(f"  Notes: {today_dose['notes']}")
    else:
        print("  No peptide dose scheduled for today")
    
    # Get upcoming doses
    print("\n📅 Upcoming Doses (Next 7 Days):")
    upcoming_doses = peptide_scheduler.get_upcoming_peptide_doses(days=7)
    
    for dose in upcoming_doses:
        date_obj = datetime.strptime(dose['date'], "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        print(f"  {dose['date']} ({day_name}):")
        if dose.get('bpc_157'):
            print(f"    BPC-157: {dose['bpc_157']}")
        if dose.get('tb_500'):
            print(f"    TB-500: {dose['tb_500']}")
        print()
    
    # Show progress
    print("📊 Protocol Progress:")
    progress = peptide_scheduler.get_peptide_progress()
    
    if progress:
        print(f"  Protocol: {progress['protocol_name']}")
        print(f"  Duration: {progress['protocol_duration']}")
        print(f"  Total Doses: {progress['total_doses']}")
        print(f"  Administered: {progress['administered_doses']}")
        print(f"  Missed: {progress['missed_doses']}")
        print(f"  Progress: {progress['progress_percentage']}%")
        print(f"  Days Remaining: {progress['days_remaining']}")
        print(f"  Current Streak: {progress['current_streak']} days")
    else:
        print("  No progress data available")
    
    # Demonstrate schedule selection
    print("\n🔄 Schedule Selection Demo:")
    print("Available options:")
    print("  1. Sample Schedule (public)")
    print("  2. Personal Schedule (private)")
    print("  3. Peptide Schedule (specialized)")
    
    # Show current active schedule
    schedule_info = peptide_scheduler.get_schedule_info()
    print(f"\nCurrent active schedule: {schedule_info['active_schedule']}")
    
    # Demonstrate task generation for main scheduler
    print("\n📋 Generating Tasks for Main Scheduler:")
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    tasks = peptide_scheduler.get_peptide_tasks_for_scheduler(start_date, end_date)
    print(f"Generated {len(tasks)} peptide tasks for the next 30 days")
    
    if tasks:
        print("\nSample tasks:")
        for i, task in enumerate(tasks[:3]):  # Show first 3 tasks
            print(f"  {i+1}. {task['title']}")
            print(f"     Time: {task['time']}")
            print(f"     Notes: {task['notes']}")
            print()
    
    print("✅ Peptide scheduler integration demo completed!")
    print("\nTo use this in your main application:")
    print("1. Import PeptideScheduler from modules.peptide_scheduler")
    print("2. Initialize with your config directory")
    print("3. Load the desired schedule")
    print("4. Integrate with your main scheduler")


if __name__ == "__main__":
    main() 