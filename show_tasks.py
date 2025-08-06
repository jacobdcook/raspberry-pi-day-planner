#!/usr/bin/env python3
"""
Quick script to show the first 12 tasks in order
"""

import json
from datetime import datetime

def show_tasks():
    """Display the first 12 tasks in order."""
    
    # Load the default schedule
    default_schedule = {
        "morning_tasks": [
            {"title": "Wake Up & Hydrate", "time": "06:00", "notes": "Drink 16 oz water with lemon + Himalayan salt", "duration": 5},
            {"title": "Take Supplements", "time": "06:05", "notes": "Vitamin D3+K2 (2000 IU), Fish Oil (1000mg), Probiotics", "duration": 2},
            {"title": "Cold Shower", "time": "06:10", "notes": "2-3 minutes cold exposure for norepinephrine boost", "duration": 3},
            {"title": "Breakfast & Planning", "time": "06:20", "notes": "Beef sweet-potato hash + carrots. Plan today's top 3 priorities", "duration": 20},
            {"title": "Morning Walk", "time": "07:00", "notes": "20 min walk for sunlight + movement", "duration": 20},
            {"title": "Work Session 1", "time": "08:00", "notes": "Deep work - most important task", "duration": 90},
            {"title": "Break & Stretch", "time": "09:30", "notes": "5 min movement + eye rest", "duration": 5},
            {"title": "Work Session 2", "time": "09:35", "notes": "Secondary priority task", "duration": 60},
            {"title": "Lunch Break", "time": "10:35", "notes": "Protein-rich meal + 10 min walk", "duration": 45},
            {"title": "Work Session 3", "time": "11:20", "notes": "Administrative tasks & emails", "duration": 60},
            {"title": "Afternoon Break", "time": "12:20", "notes": "Light snack + hydration", "duration": 15},
            {"title": "Work Session 4", "time": "12:35", "notes": "Creative work or learning", "duration": 90}
        ],
        "afternoon_tasks": [
            {"title": "Exercise", "time": "14:05", "notes": "Strength training or cardio", "duration": 45},
            {"title": "Shower & Recovery", "time": "14:50", "notes": "Cold shower + protein shake", "duration": 15},
            {"title": "Work Session 5", "time": "15:05", "notes": "Review & planning for tomorrow", "duration": 60},
            {"title": "Evening Walk", "time": "16:05", "notes": "30 min walk for sunset + reflection", "duration": 30},
            {"title": "Dinner", "time": "16:35", "notes": "Balanced meal with family", "duration": 45},
            {"title": "Evening Routine", "time": "17:20", "notes": "Journaling + gratitude practice", "duration": 20},
            {"title": "Reading", "time": "17:40", "notes": "30 min reading (no screens)", "duration": 30},
            {"title": "Prepare for Tomorrow", "time": "18:10", "notes": "Lay out clothes, pack bag", "duration": 10},
            {"title": "Relaxation", "time": "18:20", "notes": "Light stretching + meditation", "duration": 20},
            {"title": "Bedtime", "time": "18:40", "notes": "Sleep hygiene routine", "duration": 20}
        ]
    }
    
    print("📋 YOUR FIRST 12 TASKS (in order):")
    print("=" * 60)
    
    # Show morning tasks first
    print("\n🌅 MORNING TASKS:")
    for i, task in enumerate(default_schedule["morning_tasks"], 1):
        print(f"{i:2d}. {task['time']} - {task['title']}")
        print(f"    Duration: {task['duration']} min")
        print(f"    Notes: {task['notes']}")
        print()
    
    # Show first few afternoon tasks to get to 12
    print("\n🌆 AFTERNOON TASKS (first few):")
    for i, task in enumerate(default_schedule["afternoon_tasks"][:2], len(default_schedule["morning_tasks"]) + 1):
        print(f"{i:2d}. {task['time']} - {task['title']}")
        print(f"    Duration: {task['duration']} min")
        print(f"    Notes: {task['notes']}")
        print()
    
    print("=" * 60)
    print("💡 Total: 12 tasks spanning from 6:00 AM to 2:50 PM")
    print("⏰ Total duration: ~8 hours 50 minutes")
    print("🎯 Focus: Morning productivity, afternoon maintenance")

if __name__ == "__main__":
    show_tasks() 