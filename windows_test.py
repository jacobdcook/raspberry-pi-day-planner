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
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Today's Tasks Tab
        tasks_frame = ttk.Frame(notebook)
        notebook.add(tasks_frame, text="📋 Today's Tasks")
        self.create_tasks_tab(tasks_frame)
        
        # Peptide Protocol Tab
        peptide_frame = ttk.Frame(notebook)
        notebook.add(peptide_frame, text="💉 Peptide Protocol")
        self.create_peptide_tab(peptide_frame)
        
        # Settings Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        self.create_settings_tab(settings_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
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
            height=8
        )
        task_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_listbox.yview)
        self.task_listbox.configure(yscrollcommand=task_scrollbar.set)
        
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Task control buttons
        task_buttons_frame = ttk.Frame(task_frame)
        task_buttons_frame.pack(fill=tk.X, pady=10)
        
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
        self.refresh_data()
        self.update_timer()
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
                
                # Update task listbox
                self.task_listbox.delete(0, tk.END)
                for i, task in enumerate(self.today_tasks):
                    status = "✅" if task.get("completed", False) else "⏳"
                    time_str = task.get("time", "No time")
                    title = task.get("title", "Untitled")
                    priority = task.get("priority", 3)
                    priority_emoji = "🔴" if priority == 1 else "🟡" if priority == 2 else "🟢"
                    self.task_listbox.insert(tk.END, f"{status} {priority_emoji} {time_str} - {title}")
                
                self.status_var.set(f"Loaded {len(self.today_tasks)} tasks for today")
            else:
                self.status_var.set("No schedule loaded")
        except Exception as e:
            self.status_var.set(f"Error loading tasks: {e}")
            print(f"Debug - Error loading tasks: {e}")
            print(f"Debug - Schedule keys: {list(self.peptide_scheduler.main_schedule.keys()) if self.peptide_scheduler.main_schedule else 'No schedule'}")
    
    def start_current_task(self):
        """Start timing the currently selected task."""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Task Selected", "Please select a task to start.")
            return
        
        task_index = selection[0]
        if task_index < len(self.today_tasks):
            self.current_task = self.today_tasks[task_index]
            self.task_start_time = datetime.now()
            self.task_timer_running = True
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.current_task_label.config(text=f"Working on: {self.current_task.get('title', 'Unknown')}")
            self.status_var.set(f"Started timing: {self.current_task.get('title', 'Unknown')}")
    
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
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Task Selected", "Please select a task to complete.")
            return
        
        task_index = selection[0]
        if task_index < len(self.today_tasks):
            task = self.today_tasks[task_index]
            task["completed"] = True
            
            # Update the display
            self.load_today_tasks()
            self.status_var.set(f"Completed: {task.get('title', 'Unknown')}")
            
            # Stop timer if this was the current task
            if self.current_task == task:
                self.stop_current_task()
    
    def export_progress(self):
        """Export today's progress."""
        try:
            completed_tasks = [task for task in self.today_tasks if task.get("completed", False)]
            total_tasks = len(self.today_tasks)
            completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
            
            progress_report = f"Today's Progress Report\n"
            progress_report += f"========================\n"
            progress_report += f"Total Tasks: {total_tasks}\n"
            progress_report += f"Completed: {len(completed_tasks)}\n"
            progress_report += f"Completion Rate: {completion_rate:.1f}%\n\n"
            
            if completed_tasks:
                progress_report += "Completed Tasks:\n"
                for task in completed_tasks:
                    progress_report += f"✅ {task.get('title', 'Unknown')}\n"
            
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