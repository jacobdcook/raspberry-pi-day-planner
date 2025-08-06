#!/usr/bin/env python3
"""
Schedule Selector

This script allows you to select which schedule to use when starting the
Raspberry Pi day planner. It provides a simple menu interface to choose
between sample, personal, and peptide schedules.

Usage:
    python schedule_selector.py
"""

import sys
import os
from pathlib import Path

# Add the modules directory to the path
sys.path.append(str(Path(__file__).parent / "modules"))

from peptide_scheduler import PeptideScheduler


def show_menu():
    """Display the schedule selection menu."""
    print("\n" + "="*50)
    print("📅 SCHEDULE SELECTOR")
    print("="*50)
    print("Choose which schedule to use:")
    print()
    print("1. Sample Schedule (public - for GitHub)")
    print("   - Demo schedule with example tasks")
    print("   - Safe to share publicly")
    print()
    print("2. Personal Schedule (private)")
    print("   - Your actual daily schedule")
    print("   - Contains personal information")
    print("   - Excluded from Git")
    print()
    print("3. Peptide Schedule (specialized)")
    print("   - BPC-157 + TB-500 protocol")
    print("   - Detailed peptide administration")
    print("   - Excluded from Git")
    print()
    print("4. Exit")
    print()
    print("="*50)


def get_user_choice():
    """Get user's schedule choice."""
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)


def select_schedule(choice):
    """Select the schedule based on user choice."""
    config_dir = Path(__file__).parent / "config"
    peptide_scheduler = PeptideScheduler(config_dir=str(config_dir))
    
    schedule_map = {
        '1': 'sample',
        '2': 'personal', 
        '3': 'peptide'
    }
    
    if choice == '4':
        print("👋 Goodbye!")
        return None
    
    schedule_type = schedule_map[choice]
    
    print(f"\n🔄 Loading {schedule_type} schedule...")
    
    if peptide_scheduler.select_schedule(schedule_type):
        print(f"✅ Successfully loaded {schedule_type} schedule!")
        
        # Show schedule info
        schedule_info = peptide_scheduler.get_schedule_info()
        print(f"\n📋 Active Schedule: {schedule_info['active_schedule']}")
        
        # If it's a peptide schedule, show today's dose
        if schedule_type == 'peptide':
            today_dose = peptide_scheduler.get_today_peptide_dose()
            if today_dose:
                print(f"\n💉 Today's Peptide Dose:")
                print(f"   Time: {today_dose['administration_time']}")
                if today_dose.get('bpc_157'):
                    print(f"   BPC-157: {today_dose['bpc_157']}")
                if today_dose.get('tb_500'):
                    print(f"   TB-500: {today_dose['tb_500']}")
        
        return peptide_scheduler
    else:
        print(f"❌ Failed to load {schedule_type} schedule")
        return None


def main():
    """Main function for schedule selection."""
    print("🧬 Raspberry Pi Day Planner - Schedule Selector")
    
    while True:
        show_menu()
        choice = get_user_choice()
        
        if choice == '4':
            break
        
        scheduler = select_schedule(choice)
        
        if scheduler:
            print(f"\n🚀 Starting with {scheduler.active_schedule} schedule...")
            print("You can now run your main application!")
            print("\nTo integrate with your main app:")
            print("1. Import the peptide_scheduler module")
            print("2. Use the scheduler instance returned by this script")
            print("3. The scheduler is ready to use with your main system")
            break
        else:
            print("\n❌ Failed to load schedule. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main() 