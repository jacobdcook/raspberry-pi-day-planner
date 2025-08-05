#!/usr/bin/env python3
"""
Windows Test Environment for Raspberry Pi Day Planner

This script allows you to test the day planner functionality on Windows
before deploying to your Raspberry Pi. It simulates the display and
audio systems while providing full functionality.

Usage:
    python windows_test.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the modules directory to the path
sys.path.append(str(Path(__file__).parent / "modules"))

from peptide_scheduler import PeptideScheduler


class WindowsDayPlanner:
    """Windows-compatible day planner interface for testing."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧬 Raspberry Pi Day Planner - Windows Test")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize peptide scheduler
        config_dir = Path(__file__).parent / "config"
        self.peptide_scheduler = PeptideScheduler(config_dir=str(config_dir))
        
        # Load schedules
        self.load_schedules()
        
        # Create UI
        self.create_ui()
        
        # Start update loop
        self.update_display()
    
    def load_schedules(self):
        """Load available schedules."""
        self.schedule_options = self.peptide_scheduler.get_schedule_selection_menu()
        
        # Try to load personal schedule first (your actual schedule)
        if self.peptide_scheduler.select_schedule("personal"):
            self.current_schedule = "personal"
            print("✅ Personal schedule loaded successfully!")
        elif self.peptide_scheduler.select_schedule("sample"):
            self.current_schedule = "sample"
            print("⚠️ Using sample schedule (personal not found)")
        else:
            self.current_schedule = "personal"
            print("⚠️ No schedules found")
        
        # Try to load peptide schedule
        if self.peptide_scheduler.load_peptide_schedule():
            print("✅ Peptide schedule loaded successfully!")
        else:
            print("⚠️ No peptide schedule found")
    
    def create_ui(self):
        """Create the main user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🧬 Raspberry Pi Day Planner",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        title_label.pack(pady=10)
        
        # Status bar (create this first so it's available everywhere)
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Today's Tasks Tab
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="📋 Today's Tasks")
        self.create_tasks_tab(tasks_frame)
        
        # Task Details Tab (hidden by default)
        self.task_details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.task_details_frame, text="📋 Task Details")
        self.create_task_details_tab(self.task_details_frame)
        
        # Peptide Protocol Tab
        peptide_frame = ttk.Frame(self.notebook)
        self.notebook.add(peptide_frame, text="💉 Peptide Protocol")
        self.create_peptide_tab(peptide_frame)
        
        # Settings Tab
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        self.create_settings_tab(settings_frame)
    
    def create_tasks_tab(self, parent):
        """Create the tasks tab with start/stop functionality."""
        # Current time display
        time_frame = ttk.LabelFrame(parent, text="🕐 Current Time", padding=10)
        time_frame.pack(fill=tk.X, pady=10)
        
        self.time_label = tk.Label(
            time_frame,
            text="",
            font=("Arial", 16),
            fg="white",
            bg="#2b2b2b"
        )
        self.time_label.pack()
        
        # Task list
        task_frame = ttk.LabelFrame(parent, text="📋 Today's Tasks", padding=10)
        task_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Task listbox with scrollbar
        list_frame = ttk.Frame(task_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.task_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="white",
            selectmode=tk.SINGLE,
            height=8,
            selectbackground="#4a4a4a",
            selectforeground="white"
        )
        
        # Bind click events to handle selection
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)
        self.task_listbox.bind('<Double-Button-1>', self.on_task_double_click)
        task_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_listbox.yview)
        self.task_listbox.configure(yscrollcommand=task_scrollbar.set)
        
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Task control buttons
        task_buttons_frame = ttk.Frame(task_frame)
        task_buttons_frame.pack(fill=tk.X, pady=10)
        
        self.view_details_button = ttk.Button(
            task_buttons_frame,
            text="📋 View Details",
            command=self.view_task_details
        )
        self.view_details_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(
            task_buttons_frame,
            text="▶️ Start Task",
            command=self.start_current_task
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            task_buttons_frame,
            text="⏹️ Stop Task",
            command=self.stop_current_task,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.complete_button = ttk.Button(
            task_buttons_frame,
            text="✅ Complete Task",
            command=self.complete_current_task
        )
        self.complete_button.pack(side=tk.LEFT, padx=5)
        
        self.skip_button = ttk.Button(
            task_buttons_frame,
            text="⏭️ Skip Task",
            command=self.skip_current_task
        )
        self.skip_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(
            task_buttons_frame,
            text="🔄 Refresh",
            command=self.manual_refresh
        )
        self.refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Timer display
        timer_frame = ttk.LabelFrame(parent, text="⏱️ Timer", padding=10)
        timer_frame.pack(fill=tk.X, pady=10)
        
        self.timer_label = tk.Label(
            timer_frame,
            text="00:00:00",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        self.timer_label.pack()
        
        # Current task info
        self.current_task_label = tk.Label(
            timer_frame,
            text="No task selected",
            font=("Arial", 12),
            fg="white",
            bg="#2b2b2b"
        )
        self.current_task_label.pack()
        
        # Initialize task tracking
        self.current_task = None
        self.task_start_time = None
        self.task_timer_running = False
        self.today_tasks = []
        self.selected_task_index = None
    
    def create_task_details_tab(self, parent):
        """Create the task details tab."""
        # Back button
        back_frame = ttk.Frame(parent)
        back_frame.pack(fill=tk.X, pady=10)
        
        self.back_button = ttk.Button(
            back_frame,
            text="⬅️ Back to Tasks",
            command=self.go_back_to_tasks
        )
        self.back_button.pack(side=tk.LEFT, padx=10)
        
        # Task details content
        details_frame = ttk.LabelFrame(parent, text="📋 Task Details", padding=20)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Task title
        self.detail_title_label = tk.Label(
            details_frame,
            text="",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        self.detail_title_label.pack(pady=10)
        
        # Task details text
        self.detail_text = tk.Text(
            details_frame,
            font=("Arial", 12),
            bg="#2b2b2b",
            fg="white",
            wrap=tk.WORD,
            height=15,
            padx=10,
            pady=10
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.detail_start_button = ttk.Button(
            action_frame,
            text="▶️ Start Task",
            command=self.start_task_from_details
        )
        self.detail_start_button.pack(side=tk.LEFT, padx=5)
        
        self.detail_complete_button = ttk.Button(
            action_frame,
            text="✅ Complete Task",
            command=self.complete_task_from_details
        )
        self.detail_complete_button.pack(side=tk.LEFT, padx=5)
        
        self.detail_skip_button = ttk.Button(
            action_frame,
            text="⏭️ Skip Task",
            command=self.skip_task_from_details
        )
        self.detail_skip_button.pack(side=tk.LEFT, padx=5)
        
        # Store the current task being viewed
        self.current_detail_task = None
    
    def create_peptide_tab(self, parent):
        """Create the peptide protocol tab."""
        # Schedule selector
        schedule_frame = ttk.LabelFrame(parent, text="📅 Schedule Selection", padding=10)
        schedule_frame.pack(fill=tk.X, pady=10)
        
        self.schedule_var = tk.StringVar(value=self.current_schedule)
        for option in self.schedule_options:
            if option["exists"]:
                status = " (LOADED)" if option["id"] == self.current_schedule else ""
                rb = ttk.Radiobutton(
                    schedule_frame,
                    text=f"{option['name']} - {option['description']}{status}",
                    variable=self.schedule_var,
                    value=option["id"],
                    command=self.on_schedule_change
                )
                rb.pack(anchor=tk.W, pady=2)
        
        # Today's peptide dose
        peptide_frame = ttk.LabelFrame(parent, text="💉 Today's Peptide Dose", padding=10)
        peptide_frame.pack(fill=tk.X, pady=10)
        
        self.peptide_label = tk.Label(
            peptide_frame,
            text="Loading...",
            font=("Arial", 12),
            fg="white",
            bg="#2b2b2b",
            wraplength=700
        )
        self.peptide_label.pack()
        
        # Progress tracking
        progress_frame = ttk.LabelFrame(parent, text="📊 Protocol Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Loading...",
            font=("Arial", 12),
            fg="white",
            bg="#2b2b2b",
            wraplength=700
        )
        self.progress_label.pack()
        
        # Peptide control buttons
        peptide_buttons_frame = ttk.Frame(parent)
        peptide_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            peptide_buttons_frame,
            text="💉 Log Dose",
            command=self.log_dose
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            peptide_buttons_frame,
            text="📋 Test Integration",
            command=self.test_integration
        ).pack(side=tk.LEFT, padx=5)
    
    def create_settings_tab(self, parent):
        """Create the settings tab."""
        # General settings
        settings_frame = ttk.LabelFrame(parent, text="⚙️ General Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            settings_frame,
            text="🔄 Refresh Data",
            command=self.refresh_data
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            settings_frame,
            text="📊 Export Progress",
            command=self.export_progress
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            settings_frame,
            text="❌ Exit",
            command=self.root.quit
        ).pack(side=tk.RIGHT, padx=5)
    
    def on_schedule_change(self):
        """Handle schedule selection change."""
        new_schedule = self.schedule_var.get()
        if self.peptide_scheduler.select_schedule(new_schedule):
            self.current_schedule = new_schedule
            self.status_var.set(f"Switched to {new_schedule} schedule")
            self.refresh_data()
        else:
            messagebox.showerror("Error", f"Failed to load {new_schedule} schedule")
    
    def refresh_data(self):
        """Refresh all displayed data."""
        # Update time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        
        # Load today's tasks
        self.load_today_tasks()
        
        # Update peptide dose
        today_dose = self.peptide_scheduler.get_today_peptide_dose()
        if today_dose:
            dose_text = f"Date: {today_dose['date']}\n"
            dose_text += f"Time: {today_dose['administration_time']}\n"
            if today_dose.get('bpc_157'):
                dose_text += f"BPC-157: {today_dose['bpc_157']}\n"
            if today_dose.get('tb_500'):
                dose_text += f"TB-500: {today_dose['tb_500']}\n"
            if today_dose.get('notes'):
                dose_text += f"Notes: {today_dose['notes']}"
        else:
            dose_text = "No peptide dose scheduled for today"
        
        self.peptide_label.config(text=dose_text)
        
        # Update progress
        progress = self.peptide_scheduler.get_peptide_progress()
        if progress:
            progress_text = f"Protocol: {progress['protocol_name']}\n"
            progress_text += f"Duration: {progress['protocol_duration']}\n"
            progress_text += f"Progress: {progress['progress_percentage']}%\n"
            progress_text += f"Administered: {progress['administered_doses']}/{progress['total_doses']}\n"
            progress_text += f"Current Streak: {progress['current_streak']} days"
        else:
            progress_text = "No progress data available"
        
        self.progress_label.config(text=progress_text)
        
        self.status_var.set("Data refreshed")
    
    def on_task_select(self, event):
        """Handle task selection in the listbox."""
        print(f"🔍 DEBUG: on_task_select called with event: {event}")
        selection = self.task_listbox.curselection()
        print(f"🔍 DEBUG: Listbox selection: {selection}")
        print(f"🔍 DEBUG: Number of tasks loaded: {len(self.today_tasks)}")
        
        if selection:
            self.selected_task_index = selection[0]
            print(f"🔍 DEBUG: Selected task index: {self.selected_task_index}")
            
            if self.selected_task_index < len(self.today_tasks):
                selected_task = self.today_tasks[self.selected_task_index]
                task_title = selected_task.get('title', 'Unknown')
                print(f"🔍 DEBUG: Selected task: {task_title}")
                self.status_var.set(f"Selected: {task_title}")
            else:
                print(f"🔍 DEBUG: Invalid selection - index {self.selected_task_index} >= {len(self.today_tasks)}")
                self.selected_task_index = None
        else:
            print("🔍 DEBUG: No selection found")
            self.selected_task_index = None
    
    def on_task_double_click(self, event):
        """Handle double-click on task for immediate action."""
        print(f"🔍 DEBUG: Double-click detected at position: {event.x}, {event.y}")
        selection = self.task_listbox.curselection()
        print(f"🔍 DEBUG: Double-click selection: {selection}")
        if selection:
            index = selection[0]
            print(f"🔍 DEBUG: Double-clicked task index: {index}")
            if index < len(self.today_tasks):
                task = self.today_tasks[index]
                print(f"🔍 DEBUG: Double-clicked task: {task.get('title', 'Unknown')}")
                # Show details in the details tab
                self.show_task_details_in_tab()
    
    def log_dose(self):
        """Log today's peptide dose."""
        today_dose = self.peptide_scheduler.get_today_peptide_dose()
        if today_dose:
            result = messagebox.askyesno(
                "Log Dose",
                f"Log today's dose as administered?\n\n{today_dose.get('bpc_157', '')}\n{today_dose.get('tb_500', '')}"
            )
            if result:
                self.peptide_scheduler.log_peptide_administration(today_dose, administered=True)
                self.status_var.set("Dose logged as administered")
                self.refresh_data()
        else:
            messagebox.showinfo("No Dose", "No peptide dose scheduled for today")
    
    def test_integration(self):
        """Test the peptide integration functionality."""
        try:
            # Test upcoming doses
            upcoming = self.peptide_scheduler.get_upcoming_peptide_doses(days=3)
            
            # Test task generation
            start_date = datetime.now()
            end_date = start_date + timedelta(days=7)
            tasks = self.peptide_scheduler.get_peptide_tasks_for_scheduler(start_date, end_date)
            
            # Test export
            export_data = self.peptide_scheduler.export_peptide_history("json")
            
            messagebox.showinfo(
                "Integration Test",
                f"✅ All tests passed!\n\n"
                f"Upcoming doses: {len(upcoming)}\n"
                f"Generated tasks: {len(tasks)}\n"
                f"Export data length: {len(export_data)} characters"
            )
            
        except Exception as e:
            messagebox.showerror("Test Failed", f"Integration test failed: {str(e)}")
    
    def update_display(self):
        """Update the display every second."""
        self.update_timer()
        # Only refresh data every 30 seconds to avoid clearing selection
        if not hasattr(self, '_last_refresh') or (datetime.now() - self._last_refresh).seconds > 30:
            self.refresh_data()
            self._last_refresh = datetime.now()
        self.root.after(1000, self.update_display)  # Update every 1 second
    
    def update_timer(self):
        """Update the timer display."""
        if self.task_timer_running and self.task_start_time:
            elapsed = datetime.now() - self.task_start_time
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=timer_text)
    
    def load_today_tasks(self):
        """Load today's tasks from the schedule."""
        try:
            if self.peptide_scheduler.main_schedule:
                # Get all task sections
                all_tasks = []
                
                # Check for different task section names
                task_sections = ["tasks", "morning_tasks", "afternoon_tasks", "evening_tasks", "daily_tasks"]
                
                for section in task_sections:
                    if section in self.peptide_scheduler.main_schedule:
                        section_tasks = self.peptide_scheduler.main_schedule[section]
                        if isinstance(section_tasks, list):
                            all_tasks.extend(section_tasks)
                
                # Filter tasks for today (or show all if no date specified)
                today = datetime.now().strftime("%Y-%m-%d")
                
                self.today_tasks = []
                for task in all_tasks:
                    # If task has a date, check if it's today
                    if "date" in task:
                        if task.get("date") == today:
                            self.today_tasks.append(task)
                    else:
                        # If no date specified, assume it's a daily task
                        self.today_tasks.append(task)
                
                # Sort tasks by time
                self.today_tasks.sort(key=lambda x: x.get("time", "00:00"))
                
                # Create catch-up tasks for missed time blocks
                self.today_tasks = self.create_catch_up_tasks(self.today_tasks)
                
                # Update task listbox
                self.task_listbox.delete(0, tk.END)
                print(f"🔍 DEBUG: Loading {len(self.today_tasks)} tasks into listbox")
                for i, task in enumerate(self.today_tasks):
                    if task.get("skipped", False):
                        status = "⏭️"
                    elif task.get("completed", False):
                        status = "✅"
                    else:
                        status = "⏳"
                    
                    time_str = task.get("time", "No time")
                    title = task.get("title", "Untitled")
                    priority = task.get("priority", 3)
                    
                    # Special formatting for catch-up tasks
                    if task.get("is_catch_up", False):
                        priority_emoji = "🚨"
                        display_text = f"{status} {priority_emoji} {time_str} - {title}"
                    else:
                        priority_emoji = "🔴" if priority == 1 else "🟡" if priority == 2 else "🟢"
                        display_text = f"{status} {priority_emoji} {time_str} - {title}"
                    
                    self.task_listbox.insert(tk.END, display_text)
                    print(f"🔍 DEBUG: Added task {i}: {display_text}")
                
                # Don't reset selection if user has selected something
                if self.selected_task_index is None:
                    print(f"🔍 DEBUG: No selection to preserve")
                else:
                    print(f"🔍 DEBUG: Preserving selection: {self.selected_task_index}")
                self.status_var.set(f"Loaded {len(self.today_tasks)} tasks for today")
            else:
                self.status_var.set("No schedule loaded")
        except Exception as e:
            self.status_var.set(f"Error loading tasks: {e}")
            print(f"Debug - Error loading tasks: {e}")
            print(f"Debug - Schedule keys: {list(self.peptide_scheduler.main_schedule.keys()) if self.peptide_scheduler.main_schedule else 'No schedule'}")
    
    def start_current_task(self):
        """Start timing the currently selected task."""
        print(f"🔍 DEBUG: start_current_task called")
        print(f"🔍 DEBUG: selected_task_index: {self.selected_task_index}")
        print(f"🔍 DEBUG: Number of tasks: {len(self.today_tasks)}")
        
        if self.selected_task_index is None:
            print("🔍 DEBUG: No task selected - showing warning")
            messagebox.showwarning("No Task Selected", "Please select a task to start.")
            return
        
        task_index = self.selected_task_index
        print(f"🔍 DEBUG: Using task index: {task_index}")
        if task_index < len(self.today_tasks):
            self.current_task = self.today_tasks[task_index]
            self.task_start_time = datetime.now()
            self.task_timer_running = True
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.current_task_label.config(text=f"Working on: {self.current_task.get('title', 'Unknown')}")
            self.status_var.set(f"Started timing: {self.current_task.get('title', 'Unknown')}")
            
            # Show detailed task information
            task = self.current_task
            details = f"🎯 TASK STARTED\n\n"
            details += f"📋 Task: {task.get('title', 'Unknown')}\n"
            details += f"⏰ Time: {task.get('time', 'No time')}\n"
            details += f"⏱️ Duration: {task.get('duration', 0)} minutes\n"
            details += f"🔴 Priority: {task.get('priority', 3)}\n"
            
            # Special handling for catch-up tasks
            if task.get("is_catch_up", False):
                details += f"🚨 Type: CATCH-UP TASK (High Priority)\n"
                details += f"📝 Instructions:\n{task.get('notes', 'No detailed instructions')}\n\n"
                details += f"🔍 DETAILED BREAKDOWN OF MISSED TASKS:\n"
                details += f"{'='*50}\n"
                
                for i, missed_task in enumerate(task.get('catch_up_tasks', []), 1):
                    details += f"\n{i}. {missed_task.get('title', 'Unknown')} ({missed_task.get('time', 'No time')})\n"
                    details += f"   Priority: {missed_task.get('priority', 3)}\n"
                    details += f"   Duration: {missed_task.get('duration', 0)} minutes\n"
                    details += f"   Instructions: {missed_task.get('notes', 'No detailed instructions')}\n"
            else:
                details += f"📝 Instructions:\n{task.get('notes', 'No detailed instructions')}\n\n"
            
            details += f"✅ Timer started at {self.task_start_time.strftime('%H:%M:%S')}"
            
            messagebox.showinfo("Task Started", details)
    
    def view_task_details(self):
        """Show detailed information about the selected task."""
        print(f"🔍 DEBUG: view_task_details called")
        print(f"🔍 DEBUG: selected_task_index: {self.selected_task_index}")
        print(f"🔍 DEBUG: Number of tasks: {len(self.today_tasks)}")
        
        if self.selected_task_index is None:
            print("🔍 DEBUG: No task selected - showing warning")
            messagebox.showwarning("No Task Selected", "Please select a task to view details.")
            return
        
        task_index = self.selected_task_index
        print(f"🔍 DEBUG: Using task index: {task_index}")
        if task_index < len(self.today_tasks):
            task = self.today_tasks[task_index]
            
            details = f"📋 TASK DETAILS\n\n"
            details += f"🎯 Task: {task.get('title', 'Unknown')}\n"
            details += f"⏰ Time: {task.get('time', 'No time')}\n"
            details += f"⏱️ Duration: {task.get('duration', 0)} minutes\n"
            details += f"🔴 Priority: {task.get('priority', 3)}\n"
            
            # Special handling for catch-up tasks
            if task.get("is_catch_up", False):
                details += f"🚨 Type: CATCH-UP TASK (High Priority)\n"
                details += f"📋 Contains {len(task.get('catch_up_tasks', []))} missed tasks\n"
                details += f"⏰ Snooze Duration: {task.get('snooze_duration', 0)} minutes\n"
                details += f"📝 Instructions:\n{task.get('notes', 'No detailed instructions')}\n\n"
                details += f"🔍 DETAILED BREAKDOWN OF MISSED TASKS:\n"
                details += f"{'='*50}\n"
                
                for i, missed_task in enumerate(task.get('catch_up_tasks', []), 1):
                    details += f"\n{i}. {missed_task.get('title', 'Unknown')} ({missed_task.get('time', 'No time')})\n"
                    details += f"   Priority: {missed_task.get('priority', 3)}\n"
                    details += f"   Duration: {missed_task.get('duration', 0)} minutes\n"
                    details += f"   Instructions: {missed_task.get('notes', 'No detailed instructions')}\n"
            else:
                details += f"🔔 Audio Alert: {'Yes' if task.get('audio_alert', False) else 'No'}\n"
                details += f"⏰ Snooze Duration: {task.get('snooze_duration', 0)} minutes\n"
                details += f"📝 Instructions:\n{task.get('notes', 'No detailed instructions')}"
            
            messagebox.showinfo("Task Details", details)
        else:
            messagebox.showerror("Error", "Invalid task selection.")
    
    def show_task_details_in_tab(self):
        """Show task details in the dedicated details tab."""
        if self.selected_task_index is None:
            messagebox.showwarning("No Task Selected", "Please select a task to view details.")
            return
        
        task_index = self.selected_task_index
        if task_index < len(self.today_tasks):
            task = self.today_tasks[task_index]
            self.current_detail_task = task
            
            # Update the details tab content
            self.detail_title_label.config(text=task.get('title', 'Unknown'))
            
            # Clear and populate the details text
            self.detail_text.delete(1.0, tk.END)
            
            details = f"📋 TASK DETAILS\n\n"
            details += f"🎯 Task: {task.get('title', 'Unknown')}\n"
            details += f"⏰ Time: {task.get('time', 'No time')}\n"
            details += f"⏱️ Duration: {task.get('duration', 0)} minutes\n"
            details += f"🔴 Priority: {task.get('priority', 3)}\n"
            
            # Special handling for catch-up tasks
            if task.get("is_catch_up", False):
                details += f"🚨 Type: CATCH-UP TASK (High Priority)\n"
                details += f"📋 Contains {len(task.get('catch_up_tasks', []))} missed tasks\n"
                details += f"⏰ Snooze Duration: {task.get('snooze_duration', 0)} minutes\n"
                details += f"📝 Instructions:\n{task.get('notes', 'No detailed instructions')}\n\n"
                details += f"🔍 DETAILED BREAKDOWN OF MISSED TASKS:\n"
                details += f"{'='*50}\n"
                
                for i, missed_task in enumerate(task.get('catch_up_tasks', []), 1):
                    details += f"\n{i}. {missed_task.get('title', 'Unknown')} ({missed_task.get('time', 'No time')})\n"
                    details += f"   Priority: {missed_task.get('priority', 3)}\n"
                    details += f"   Duration: {missed_task.get('duration', 0)} minutes\n"
                    details += f"   Instructions: {missed_task.get('notes', 'No detailed instructions')}\n"
            else:
                details += f"🔔 Audio Alert: {'Yes' if task.get('audio_alert', False) else 'No'}\n"
                details += f"⏰ Snooze Duration: {task.get('snooze_duration', 0)} minutes\n"
                details += f"📝 Instructions:\n{task.get('notes', 'No detailed instructions')}"
            
            self.detail_text.insert(1.0, details)
            
            # Switch to the details tab
            self.notebook.select(1)  # Index 1 is the task details tab
        else:
            messagebox.showerror("Error", "Invalid task selection.")
    
    def go_back_to_tasks(self):
        """Go back to the tasks tab."""
        self.notebook.select(0)  # Index 0 is the tasks tab
    
    def start_task_from_details(self):
        """Start the task from the details tab."""
        if self.current_detail_task:
            # Set the current task and start timing
            self.current_task = self.current_detail_task
            self.task_start_time = datetime.now()
            self.task_timer_running = True
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.current_task_label.config(text=f"Working on: {self.current_task.get('title', 'Unknown')}")
            self.status_var.set(f"Started timing: {self.current_task.get('title', 'Unknown')}")
            
            # Go back to tasks tab
            self.go_back_to_tasks()
            
            # Show confirmation
            messagebox.showinfo("Task Started", f"✅ Started timing: {self.current_task.get('title', 'Unknown')}")
        else:
            messagebox.showwarning("No Task", "No task selected to start.")
    
    def complete_task_from_details(self):
        """Complete the task from the details tab."""
        if self.current_detail_task:
            task = self.current_detail_task
            
            # Handle catch-up tasks specially
            if task.get("is_catch_up", False):
                # Mark all individual tasks in the catch-up block as completed
                catch_up_tasks = task.get("catch_up_tasks", [])
                for catch_up_task in catch_up_tasks:
                    catch_up_task["completed"] = True
                
                messagebox.showinfo(
                    "Catch-Up Completed", 
                    f"✅ All missed tasks in '{task.get('title', 'Unknown')}' marked as completed!\n\n"
                    f"This included {len(catch_up_tasks)} tasks that were missed earlier."
                )
            else:
                task["completed"] = True
                self.status_var.set(f"Completed: {task.get('title', 'Unknown')}")
            
            # Update the display
            self.load_today_tasks()
            
            # Stop timer if this was the current task
            if self.current_task == task:
                self.stop_current_task()
            
            # Go back to tasks tab
            self.go_back_to_tasks()
        else:
            messagebox.showwarning("No Task", "No task selected to complete.")
    
    def create_catch_up_tasks(self, tasks):
        """Create consolidated catch-up tasks for missed time blocks."""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_str = f"{current_hour:02d}:{current_minute:02d}"
        
        # Define time blocks
        time_blocks = {
            "morning": {"start": "06:00", "end": "10:00", "name": "Morning Routine"},
            "mid_morning": {"start": "10:00", "end": "12:00", "name": "Mid-Morning Tasks"},
            "afternoon": {"start": "12:00", "end": "16:00", "name": "Afternoon Tasks"},
            "evening": {"start": "16:00", "end": "20:00", "name": "Evening Tasks"},
            "night": {"start": "20:00", "end": "23:59", "name": "Night Routine"}
        }
        
        # Group tasks by time blocks
        tasks_by_block = {}
        for task in tasks:
            task_time = task.get("time", "00:00")
            block_found = False
            
            for block_name, block_info in time_blocks.items():
                if self.is_time_between(task_time, block_info["start"], block_info["end"]):
                    if block_name not in tasks_by_block:
                        tasks_by_block[block_name] = []
                    tasks_by_block[block_name].append(task)
                    block_found = True
                    break
            
            if not block_found:
                # Default to current block or next available
                if "other" not in tasks_by_block:
                    tasks_by_block["other"] = []
                tasks_by_block["other"].append(task)
        
        # Create catch-up tasks for missed blocks
        catch_up_tasks = []
        for block_name, block_info in time_blocks.items():
            if block_name in tasks_by_block:
                block_tasks = tasks_by_block[block_name]
                missed_tasks = []
                
                for task in block_tasks:
                    task_time = task.get("time", "00:00")
                    if self.is_time_before(task_time, current_time_str) and not task.get("completed", False) and not task.get("skipped", False):
                        missed_tasks.append(task)
                
                if missed_tasks:
                    # Create consolidated catch-up task
                    catch_up_task = {
                        "title": f"🚨 CATCH UP: {block_info['name']}",
                        "time": current_time_str,
                        "priority": 1,  # High priority
                        "duration": len(missed_tasks) * 15,  # Estimate 15 min per task
                        "notes": f"URGENT: Complete these missed tasks ASAP:\n\n" + 
                                "\n".join([f"• {task.get('title', 'Unknown')} ({task.get('time', 'No time')})" 
                                          for task in missed_tasks]),
                        "catch_up_tasks": missed_tasks,
                        "is_catch_up": True
                    }
                    catch_up_tasks.append(catch_up_task)
        
        # Add remaining tasks that aren't in catch-up blocks
        remaining_tasks = []
        for task in tasks:
            if not any(task in catch_up_task.get("catch_up_tasks", []) 
                      for catch_up_task in catch_up_tasks):
                remaining_tasks.append(task)
        
        # Combine catch-up tasks (at the top) with remaining tasks
        final_tasks = catch_up_tasks + remaining_tasks
        
        return final_tasks
    
    def is_time_between(self, time_str, start_str, end_str):
        """Check if a time is between start and end times."""
        try:
            time_parts = time_str.split(":")
            start_parts = start_str.split(":")
            end_parts = end_str.split(":")
            
            time_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
            end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
            
            return start_minutes <= time_minutes <= end_minutes
        except:
            return False
    
    def is_time_before(self, time_str, current_str):
        """Check if a time is before the current time."""
        try:
            time_parts = time_str.split(":")
            current_parts = current_str.split(":")
            
            time_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            current_minutes = int(current_parts[0]) * 60 + int(current_parts[1])
            
            return time_minutes < current_minutes
        except:
            return False
    
    def manual_refresh(self):
        """Manually refresh the task list."""
        print("🔍 DEBUG: Manual refresh requested")
        self.refresh_data()
    
    def stop_current_task(self):
        """Stop timing the current task."""
        if self.task_timer_running:
            self.task_timer_running = False
            self.task_start_time = None
            
            # Update UI
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.timer_label.config(text="00:00:00")
            self.current_task_label.config(text="No task selected")
            self.status_var.set("Task timing stopped")
    
    def complete_current_task(self):
        """Mark the currently selected task as completed."""
        if self.selected_task_index is None:
            messagebox.showwarning("No Task Selected", "Please select a task to complete.")
            return
        
        task_index = self.selected_task_index
        if task_index < len(self.today_tasks):
            task = self.today_tasks[task_index]
            
            # Handle catch-up tasks specially
            if task.get("is_catch_up", False):
                # Mark all individual tasks in the catch-up block as completed
                catch_up_tasks = task.get("catch_up_tasks", [])
                for catch_up_task in catch_up_tasks:
                    catch_up_task["completed"] = True
                
                messagebox.showinfo(
                    "Catch-Up Completed", 
                    f"✅ All missed tasks in '{task.get('title', 'Unknown')}' marked as completed!\n\n"
                    f"This included {len(catch_up_tasks)} tasks that were missed earlier."
                )
            else:
                task["completed"] = True
                self.status_var.set(f"Completed: {task.get('title', 'Unknown')}")
            
            # Update the display
            self.load_today_tasks()
            
            # Stop timer if this was the current task
            if self.current_task == task:
                self.stop_current_task()
        else:
            messagebox.showerror("Error", "Invalid task selection.")
    
    def skip_current_task(self):
        """Skip the currently selected task for today."""
        if self.selected_task_index is None:
            messagebox.showwarning("No Task Selected", "Please select a task to skip.")
            return
        
        task_index = self.selected_task_index
        if task_index < len(self.today_tasks):
            task = self.today_tasks[task_index]
            
            # Handle catch-up tasks specially
            if task.get("is_catch_up", False):
                # Skip all individual tasks in the catch-up block
                catch_up_tasks = task.get("catch_up_tasks", [])
                for catch_up_task in catch_up_tasks:
                    catch_up_task["skipped"] = True
                
                messagebox.showinfo(
                    "Catch-Up Skipped", 
                    f"⏭️ All missed tasks in '{task.get('title', 'Unknown')}' skipped for today!\n\n"
                    f"This included {len(catch_up_tasks)} tasks that were missed earlier."
                )
            else:
                task["skipped"] = True
                self.status_var.set(f"Skipped: {task.get('title', 'Unknown')}")
            
            # Update the display
            self.load_today_tasks()
            
            # Stop timer if this was the current task
            if self.current_task == task:
                self.stop_current_task()
        else:
            messagebox.showerror("Error", "Invalid task selection.")
    
    def skip_task_from_details(self):
        """Skip the task from the details tab."""
        if self.current_detail_task:
            task = self.current_detail_task
            
            # Handle catch-up tasks specially
            if task.get("is_catch_up", False):
                # Skip all individual tasks in the catch-up block
                catch_up_tasks = task.get("catch_up_tasks", [])
                for catch_up_task in catch_up_tasks:
                    catch_up_task["skipped"] = True
                
                messagebox.showinfo(
                    "Catch-Up Skipped", 
                    f"⏭️ All missed tasks in '{task.get('title', 'Unknown')}' skipped for today!\n\n"
                    f"This included {len(catch_up_tasks)} tasks that were missed earlier."
                )
            else:
                task["skipped"] = True
                self.status_var.set(f"Skipped: {task.get('title', 'Unknown')}")
            
            # Update the display
            self.load_today_tasks()
            
            # Stop timer if this was the current task
            if self.current_task == task:
                self.stop_current_task()
            
            # Go back to tasks tab
            self.go_back_to_tasks()
        else:
            messagebox.showwarning("No Task", "No task selected to skip.")
    
    def export_progress(self):
        """Export today's progress."""
        try:
            completed_tasks = [task for task in self.today_tasks if task.get("completed", False)]
            skipped_tasks = [task for task in self.today_tasks if task.get("skipped", False)]
            total_tasks = len(self.today_tasks)
            active_tasks = total_tasks - len(skipped_tasks)
            completion_rate = (len(completed_tasks) / active_tasks * 100) if active_tasks > 0 else 0
            
            progress_report = f"Today's Progress Report\n"
            progress_report += f"========================\n"
            progress_report += f"Total Tasks: {total_tasks}\n"
            progress_report += f"Active Tasks: {active_tasks}\n"
            progress_report += f"Completed: {len(completed_tasks)}\n"
            progress_report += f"Skipped: {len(skipped_tasks)}\n"
            progress_report += f"Completion Rate: {completion_rate:.1f}%\n\n"
            
            if completed_tasks:
                progress_report += "Completed Tasks:\n"
                for task in completed_tasks:
                    progress_report += f"✅ {task.get('title', 'Unknown')}\n"
            
            if skipped_tasks:
                progress_report += "\nSkipped Tasks:\n"
                for task in skipped_tasks:
                    progress_report += f"⏭️ {task.get('title', 'Unknown')}\n"
            
            messagebox.showinfo("Progress Report", progress_report)
            self.status_var.set("Progress report generated")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export progress: {e}")
            self.status_var.set("Export failed")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main function to run the Windows test environment."""
    print("🧬 Starting Raspberry Pi Day Planner - Windows Test Environment")
    print("=" * 60)
    print("This simulates the Raspberry Pi environment for testing.")
    print("Your personal data is protected and not shared.")
    print("=" * 60)
    
    try:
        app = WindowsDayPlanner()
        app.run()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main() 