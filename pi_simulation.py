#!/usr/bin/env python3
"""
Raspberry Pi Day Planner - Visual Simulation
============================================

This script simulates the exact Raspberry Pi experience using pygame.
It shows how the Pi will display tasks, notifications, and user interactions.

Features simulated:
- Full-screen display (like Pi with attached monitor)
- Task notifications with buttons (DONE, SKIP, SNOOZE)
- Idle screen with current time and next task
- Audio feedback (simulated)
- Touch/click interactions
- Real-time updates
- Voice assistant prompting (PHASE 4)
- Mood tracking (PHASE 4)

Usage:
    python pi_simulation.py

This gives you a preview of exactly how your Pi will behave!
"""

import pygame
import yaml
import os
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import sys
import math

# Add modules directory to path
modules_path = Path(__file__).parent / "modules"
sys.path.append(str(modules_path))

from progress_db import ProgressDatabase
from task_timer import TaskTimer
from adaptive_time import AdaptiveTimeManager
from backlog_manager import BacklogManager
try:
    from elevenlabs import generate, set_api_key
    ELEVENLABS_AVAILABLE = True
except ImportError:
    # Fallback if elevenlabs is not available
    ELEVENLABS_AVAILABLE = False
    def generate(*args, **kwargs):
        return None
    def set_api_key(*args, **kwargs):
        pass
import threading
import tempfile

class PiSimulation:
    def __init__(self, width=1920, height=1080):
        pygame.init()
        
        # Get monitor info for responsive design
        info = pygame.display.Info()
        self.monitor_width = info.current_w
        self.monitor_height = info.current_h
        
        # Use monitor size if available, otherwise default
        if self.monitor_width > 0 and self.monitor_height > 0:
            self.width = self.monitor_width
            self.height = self.monitor_height
        else:
            self.width = width
            self.height = height
        
        # Theme system
        self.current_theme = "dark"  # Start with dark theme
        self.themes = {
            "dark": {
                "background": (20, 20, 20),
                "text": (255, 255, 255),
                "accent": (0, 150, 255),
                "button": (40, 40, 40),
                "button_hover": (60, 60, 60),
                "border": (100, 100, 100),
                "success": (0, 255, 0),
                "warning": (255, 165, 0),
                "error": (255, 0, 0),
                "completed": (0, 200, 0),
                "skipped": (200, 200, 200),
                "focus": (255, 100, 100),  # Red for focus mode
                "distraction": (255, 200, 0)  # Orange for distraction alerts
            },
            "light": {
                "background": (245, 245, 245),
                "text": (20, 20, 20),
                "accent": (0, 100, 200),
                "button": (220, 220, 220),
                "button_hover": (200, 200, 200),
                "border": (150, 150, 150),
                "success": (0, 200, 0),
                "warning": (255, 140, 0),
                "error": (200, 0, 0),
                "completed": (0, 150, 0),
                "skipped": (100, 100, 100),
                "focus": (200, 50, 50),  # Darker red for light theme
                "distraction": (200, 150, 0)  # Darker orange for light theme
            }
        }
        
        # Responsive font sizes (based on screen width)
        self.base_font_size = max(16, self.width // 80)
        self.large_font_size = max(24, self.width // 50)
        self.small_font_size = max(12, self.width // 100)
        
        # Initialize fonts with responsive sizes
        self.large_font = pygame.font.SysFont('Arial', self.large_font_size)
        self.font = pygame.font.SysFont('Arial', self.base_font_size)
        self.medium_font = pygame.font.SysFont('Arial', self.base_font_size)  # Same as base font
        self.small_font = pygame.font.SysFont('Arial', self.small_font_size)
        self.tiny_font = pygame.font.SysFont('Arial', max(10, self.width // 150))  # For very small text
        
        # Responsive UI dimensions
        self.button_width = max(150, self.width // 12)
        self.button_height = max(50, self.height // 20)
        self.task_box_width = max(400, self.width // 4)
        self.task_box_height = max(80, self.height // 12)
        self.margin = max(20, self.width // 100)
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Raspberry Pi Day Planner Simulation")
        
        # Get current theme colors
        self.colors = self.themes[self.current_theme]
        
        # Legacy color constants for backward compatibility
        self.BLACK = self.get_theme_color("background")
        self.WHITE = self.get_theme_color("text")
        self.GREEN = self.get_theme_color("success")
        self.RED = self.get_theme_color("error")
        self.BLUE = self.get_theme_color("accent")
        self.YELLOW = self.get_theme_color("warning")
        self.GRAY = self.get_theme_color("border")
        self.DARK_GRAY = self.get_theme_color("button")
        
        # Initialize components
        self.progress_db = ProgressDatabase()
        self.task_timer = TaskTimer()
        self.adaptive_time = AdaptiveTimeManager()
        self.backlog_manager = BacklogManager()
        
        # Setup ElevenLabs
        if ELEVENLABS_AVAILABLE:
            try:
                # Try to load from config file first
                try:
                    from elevenlabs_config import ELEVENLABS_API_KEY
                    set_api_key(ELEVENLABS_API_KEY)
                    print("✅ ElevenLabs configured from config file")
                except ImportError:
                    # Use the key directly (for testing)
                    set_api_key("sk_f8bd094182fd27ab6d2ba6d1447a3346ea745159f422970d")
                    print("✅ ElevenLabs configured with test key")
            except Exception as e:
                print(f"⚠️ ElevenLabs setup failed: {e}")
        else:
            print("⚠️ ElevenLabs not available - voice features disabled")
        
        # Load schedule
        self.schedule = self.load_schedule()
        self.current_task_index = 0
        self.tasks = self.get_todays_tasks()
        
        # Initialize state variables
        self.current_time = datetime.now()
        self.today_tasks = self.tasks
        self.completed_tasks = []
        self.skipped_tasks = []
        self.completed_tasks_count = 0
        self.skipped_tasks_count = 0
        self.current_task = None
        self.current_screen = "idle"
        self.show_popup = False
        self.popup_title = ""
        self.popup_message = ""
        self.popup_type = "info"
        self.popup_ok_rect = None
        self.exit_confirmation_active = False
        
        # Phase 6: Add Task functionality
        self.new_task_title = ""
        self.new_task_time = ""
        self.new_task_notes = ""
        self.new_task_date = datetime.now().strftime("%Y-%m-%d")  # Default to today
        self.active_input_field = None  # "title", "time", "notes", "date", or None
        self.clock = pygame.time.Clock()
        self.show_mood_prompt = False
        
        # Enhanced Add Task UI components
        self.show_time_picker = False
        self.show_calendar = False
        self.time_picker_hour = 12
        self.time_picker_minute = 0
        self.time_picker_am_pm = "AM"
        self.calendar_year = datetime.now().year
        self.calendar_month = datetime.now().month
        self.calendar_selected_day = datetime.now().day
        self.current_mood = None
        self.mood_notes = ""
        self.tasks_per_page = 4
        self.last_encouragement_time = None
        
        # State management
        self.current_view = "idle"  # idle, task, catch_up, backlog, stats, voice_settings, focus, distraction
        self.catch_up_page = 0
        self.backlog_page = 0
        self.selected_task = None
        self.task_details_open = False
        
        # Persistent catch-up tasks list (to maintain completed/skipped status)
        self.todays_catch_up_tasks = []
        self.catch_up_tasks_initialized = False
        
        # BONUS FEATURE 1: Focus Mode
        self.focus_mode = False
        self.pomodoro_timer = 25 * 60  # 25 minutes in seconds
        self.pomodoro_start_time = None
        self.focus_task = None
        self.pomodoro_paused = False
        self.pomodoro_pause_start = None
        
        # BONUS FEATURE 2: Distraction Alerts
        self.last_interaction_time = time.time()
        self.distraction_threshold = 30  # 30 seconds of inactivity
        self.distraction_warning_shown = False
        self.distraction_warning_time = None
        self.distraction_warning_duration = 5  # Show warning for 5 seconds
        
        # BONUS FEATURE 3: Emoji Analytics
        self.emoji_analytics = {
            "💪": "Consistency Crusher",  # 3+ days in a row completed
            "🔥": "Focus Fire",  # 5+ tasks completed in a day
            "⏰": "Time Master",  # All tasks completed on time
            "🎯": "Precision Player",  # 100% completion rate
            "🚀": "Rocket Start",  # First 3 tasks completed
            "🏆": "Champion",  # 7-day streak
            "💎": "Diamond Focus",  # Focus mode used
            "🛡️": "Distraction Shield"  # No distractions detected
        }
        self.earned_badges = []
        
        # Initialize voice assistant (ElevenLabs)
        self.voice_engine = None
        self.voice_id = "Charlie"  # Default voice ID
        self.api_key = None
        
        try:
            # Load API key from config file
            try:
                from elevenlabs_config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
                self.api_key = ELEVENLABS_API_KEY
                self.voice_id = ELEVENLABS_VOICE_ID
                print(f"🔧 Loaded API key and voice ID: {self.voice_id}")
            except ImportError:
                self.api_key = "sk_13b7039f184db48b15ee5f12f8249e78d01edd41b17e6b5a"
                self.voice_id = "Charlie"
                print(f"🔧 Using fallback API key and voice ID: {self.voice_id}")
            
            # Set API key
            set_api_key(self.api_key)
            print("🔧 API key set successfully")
            
            # Test voice generation
            test_audio = generate(text="Voice assistant ready", voice=self.voice_id)
            if test_audio:
                self.voice_engine = True  # Mark as available
                print("✅ Voice assistant initialized successfully")
                print(f"🔧 Voice engine status: {self.voice_engine}")
            else:
                print("❌ Failed to generate test audio")
        except Exception as e:
            print(f"❌ Failed to initialize voice assistant: {e}")
            self.voice_engine = None
        
        # Register exit handler
        import atexit
        atexit.register(self.save_progress_on_exit)
        
        print(f"🎨 Theme: {self.current_theme}")
        print(f"📱 Screen: {self.width}x{self.height}")
        print(f"🔤 Font sizes: Large={self.large_font_size}, Base={self.base_font_size}, Small={self.small_font_size}")
    
    def save_progress_on_exit(self):
        """Save progress when the simulation exits."""
        try:
            if hasattr(self, 'progress_db') and self.progress_db:
                # Get today's date
                today = datetime.now().strftime("%Y-%m-%d")
                
                # Count completed and skipped tasks
                completed_count = len([t for t in self.today_tasks if t.get('completed', False)])
                skipped_count = len([t for t in self.today_tasks if t.get('skipped', False)])
                total_count = len(self.today_tasks)
                
                # Save to database
                self.progress_db.save_daily_summary(today, total_count, completed_count, skipped_count)
                print(f"✅ Progress saved: {completed_count}/{total_count} completed, {skipped_count} skipped")
        except Exception as e:
            print(f"❌ Error saving progress on exit: {e}")
        
        print(f"🎨 Theme: {self.current_theme}")
        print(f"📱 Screen: {self.width}x{self.height}")
        print(f"🔤 Font sizes: Large={self.large_font_size}, Base={self.base_font_size}, Small={self.small_font_size}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.colors = self.themes[self.current_theme]
        print(f"🎨 Switched to {self.current_theme} theme")
    
    def get_theme_color(self, color_name):
        """Get color from current theme."""
        return self.themes[self.current_theme].get(color_name, (255, 255, 255))
    
    def format_time_for_display(self, time_str):
        """Convert 24-hour time format to 12-hour format for display."""
        try:
            # Parse the time string (HH:MM format)
            hour, minute = map(int, time_str.split(':'))
            
            # Convert to 12-hour format
            if hour == 0:
                return f"12:{minute:02d} AM"
            elif hour < 12:
                return f"{hour}:{minute:02d} AM"
            elif hour == 12:
                return f"12:{minute:02d} PM"
            else:
                return f"{hour - 12}:{minute:02d} PM"
        except:
            # If parsing fails, return the original string
            return time_str
    
    def responsive_rect(self, x_ratio, y_ratio, width_ratio, height_ratio):
        """Create responsive rectangle based on screen ratios."""
        x = int(self.width * x_ratio)
        y = int(self.height * y_ratio)
        width = int(self.width * width_ratio)
        height = int(self.height * height_ratio)
        return pygame.Rect(x, y, width, height)
    
    def responsive_text(self, text, font, color, x_ratio, y_ratio, center=False):
        """Render text with responsive positioning."""
        text_surface = font.render(text, True, color)
        x = int(self.width * x_ratio)
        y = int(self.height * y_ratio)
        
        if center:
            x -= text_surface.get_width() // 2
            y -= text_surface.get_height() // 2
        
        return text_surface, (x, y)
    
    def speak_message(self, message):
        """Speak a message using ElevenLabs voice."""
        if not self.voice_engine or not self.api_key:
            return
        
        try:
            # Generate audio
            audio = generate(text=message, voice=self.voice_id)
            if audio:
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(audio)
                    temp_file_path = temp_file.name
                
                # Play audio using pygame mixer
                pygame.mixer.init()
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()
                
                # Clean up temp file after a delay
                def cleanup():
                    import time
                    time.sleep(5)  # Wait for audio to finish
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
                
                print(f"🔊 Voice: {message}")
            else:
                print(f"❌ Failed to generate audio for: {message}")
        except Exception as e:
            print(f"❌ Error speaking message: {e}")
    
    def list_available_voices(self):
        """List available ElevenLabs voices."""
        if voices:
            try:
                available_voices = voices()
                print("🎤 Available ElevenLabs voices:")
                for voice in available_voices:
                    print(f"  - {voice.name} (ID: {voice.voice_id})")
                return available_voices
            except Exception as e:
                print(f"❌ DEBUG: Failed to list voices: {e}")
                return []
        else:
            print("❌ DEBUG: ElevenLabs voices module not available")
            return []
    
    def change_voice(self, voice_id):
        """Change the voice ID for speech synthesis."""
        if self.voice_engine:
            self.voice_id = voice_id
            print(f"🎤 Voice changed to: {voice_id}")
            return True
        else:
            print("❌ DEBUG: Voice engine not available")
            return False
    
    def announce_next_task(self, task):
        """Announce the next task using voice."""
        if task:
            task_title = task.get('title', 'Unknown task')
            task_notes = task.get('notes', '')
            
            if task_notes:
                message = f"You need to start on: {task_title}. {task_notes}"
            else:
                message = f"You need to start on: {task_title}"
            
            self.speak_message(message)
    
    def offer_encouragement(self):
        """Offer encouragement when 3+ tasks are completed."""
        current_time = datetime.now()
        
        # Check if we should offer encouragement (3+ tasks completed and not recently)
        if (self.completed_tasks_count >= 3 and 
            (self.last_encouragement_time is None or 
             (current_time - self.last_encouragement_time).seconds > 300)):  # 5 minutes cooldown
            
            message = "You're crushing it today!"
            self.speak_message(message)
            self.last_encouragement_time = current_time
            print(f"🎉 Encouragement offered! Completed tasks: {self.completed_tasks_count}")
    
    def save_mood_data(self, mood, notes=""):
        """Save mood data to file."""
        try:
            date_str = self.current_time.strftime("%Y-%m-%d")
            mood_entry = {
                "date": date_str,
                "mood": mood,
                "notes": notes,
                "timestamp": self.current_time.isoformat(),
                "completed_tasks": len([t for t in self.today_tasks if t.get('completed', False)]),
                "skipped_tasks": len([t for t in self.today_tasks if t.get('skipped', False)]),
                "total_tasks": len(self.today_tasks)
            }
            
            # Load existing mood data
            mood_file = "mood_data.json"
            try:
                with open(mood_file, 'r') as f:
                    self.mood_data = json.load(f)
            except FileNotFoundError:
                self.mood_data = {}
            
            # Add new mood entry
            self.mood_data[date_str] = mood_entry
            
            # Save to file
            with open(mood_file, 'w') as f:
                json.dump(self.mood_data, f, indent=2)
            
            print(f"📝 Mood saved: {mood} - {notes}")
            
            # Correlate mood with task performance
            completion_rate = (mood_entry["completed_tasks"] / mood_entry["total_tasks"]) * 100 if mood_entry["total_tasks"] > 0 else 0
            print(f"📊 Task completion rate: {completion_rate:.1f}%")
            
        except Exception as e:
            print(f"❌ Error saving mood data: {e}")
    
    def draw_mood_prompt(self):
        """Draw the mood tracking prompt screen."""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = "How did you feel today?"
        title_surface = self.large_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.width//2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Mood options
        moods = [
            ("😄", "Great", self.GREEN),
            ("🙂", "Good", self.GREEN),
            ("😐", "Okay", self.YELLOW),
            ("😞", "Bad", self.RED),
            ("😡", "Terrible", self.RED)
        ]
        
        button_width = 120
        button_height = 80
        spacing = 20
        start_x = (self.width - (len(moods) * (button_width + spacing) - spacing)) // 2
        start_y = 200
        
        self.mood_buttons = []
        
        for i, (emoji, label, color) in enumerate(moods):
            x = start_x + i * (button_width + spacing)
            y = start_y
            
            # Mood button
            button_rect = pygame.Rect(x, y, button_width, button_height)
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.WHITE, button_rect, 3)
            
            # Highlight selected mood
            if self.current_mood == label:
                pygame.draw.rect(self.screen, self.WHITE, button_rect, 5)
            
            # Emoji
            emoji_surface = self.medium_font.render(emoji, True, self.BLACK)
            emoji_rect = emoji_surface.get_rect(center=(x + button_width//2, y + 25))
            self.screen.blit(emoji_surface, emoji_rect)
            
            # Label
            label_surface = self.small_font.render(label, True, self.BLACK)
            label_rect = label_surface.get_rect(center=(x + button_width//2, y + 55))
            self.screen.blit(label_surface, label_rect)
            
            self.mood_buttons.append((button_rect, label))
        
        # Notes section
        notes_y = start_y + button_height + 50
        notes_text = "Notes (optional):"
        notes_surface = self.medium_font.render(notes_text, True, self.WHITE)
        notes_rect = notes_surface.get_rect(center=(self.width//2, notes_y))
        self.screen.blit(notes_surface, notes_rect)
        
        # Notes input box
        notes_box_rect = pygame.Rect(100, notes_y + 30, self.width - 200, 60)
        pygame.draw.rect(self.screen, self.DARK_GRAY, notes_box_rect)
        pygame.draw.rect(self.screen, self.WHITE, notes_box_rect, 2)
        
        # Display current notes
        if self.mood_notes:
            notes_surface = self.small_font.render(self.mood_notes, True, self.WHITE)
            notes_rect = notes_surface.get_rect(x=110, y=notes_y + 45)
            self.screen.blit(notes_surface, notes_rect)
        else:
            placeholder_surface = self.small_font.render("Type your notes here...", True, self.GRAY)
            placeholder_rect = placeholder_surface.get_rect(x=110, y=notes_y + 45)
            self.screen.blit(placeholder_surface, placeholder_rect)
        
        self.notes_box_rect = notes_box_rect
        
        # Save button
        save_button_rect = pygame.Rect(self.width//2 - 100, notes_y + 120, 200, 50)
        pygame.draw.rect(self.screen, self.GREEN, save_button_rect)
        pygame.draw.rect(self.screen, self.WHITE, save_button_rect, 2)
        
        save_text = "Save Mood"
        save_surface = self.medium_font.render(save_text, True, self.BLACK)
        save_rect = save_surface.get_rect(center=save_button_rect.center)
        self.screen.blit(save_surface, save_rect)
        
        self.save_mood_button_rect = save_button_rect
        
        # Skip button
        skip_button_rect = pygame.Rect(self.width//2 - 100, notes_y + 180, 200, 50)
        pygame.draw.rect(self.screen, self.GRAY, skip_button_rect)
        pygame.draw.rect(self.screen, self.WHITE, skip_button_rect, 2)
        
        skip_text = "Skip"
        skip_surface = self.medium_font.render(skip_text, True, self.BLACK)
        skip_rect = skip_surface.get_rect(center=skip_button_rect.center)
        self.screen.blit(skip_surface, skip_rect)
        
        self.skip_mood_button_rect = skip_button_rect
    
    def handle_mood_input(self, event):
        """Handle keyboard input for mood notes."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.mood_notes = self.mood_notes[:-1]
            elif event.key == pygame.K_RETURN:
                # Save mood
                if self.current_mood:
                    self.save_mood_data(self.current_mood, self.mood_notes)
                    self.show_mood_prompt = False
                    self.current_mood = None
                    self.mood_notes = ""
            elif event.unicode.isprintable():
                # Add character to notes (limit length)
                if len(self.mood_notes) < 100:
                    self.mood_notes += event.unicode
    
    def _check_daily_save(self):
        """Check if it's time for daily save (23:59) and perform it."""
        try:
            current_time = datetime.now()
            current_date = current_time.strftime('%Y-%m-%d')
            
            # Check if it's 23:59 and we haven't saved today
            if (current_time.hour == 23 and current_time.minute == 59 and 
                self.last_daily_save_date != current_date):
                
                if self.progress_db and self.today_tasks:
                    # Calculate today's statistics
                    completed_count = len([t for t in self.today_tasks if t.get('completed', False)])
                    skipped_count = len([t for t in self.today_tasks if t.get('skipped', False)])
                    total_count = len(self.today_tasks)
                    
                    # Save to database
                    today = current_time.strftime('%Y-%m-%d')
                    self.progress_db.save_daily_summary(
                        today, total_count, completed_count, skipped_count
                    )
                    self.progress_db.save_task_details(today, self.today_tasks)
                    
                    print(f"📊 Daily progress saved at 23:59: {completed_count}/{total_count} completed, {skipped_count} skipped")
                    
                    # Update last save date
                    self.last_daily_save_date = current_date
                    
        except Exception as e:
            print(f"❌ Error in daily save check: {e}")
    
    def load_schedule(self):
        """Load schedule from YAML file."""
        try:
            schedule_path = Path("config/schedule.yaml")
            if schedule_path.exists():
                with open(schedule_path, 'r', encoding='utf-8') as file:
                    schedule = yaml.safe_load(file)
                    print(f"✅ Loaded schedule from {schedule_path}")
                    return schedule
            else:
                print(f"⚠️ Schedule file not found at {schedule_path}")
                return self.get_default_schedule()
        except Exception as e:
            print(f"❌ Error loading schedule: {e}")
            return self.get_default_schedule()

    def get_default_schedule(self):
        """Get default schedule if file not found."""
        return {
            "morning_tasks": [
                {"title": "Morning Routine", "time": "06:00", "notes": "Wake up, stretch, drink water"},
                {"title": "Breakfast", "time": "06:30", "notes": "Healthy breakfast with protein"},
                {"title": "Workout", "time": "07:00", "notes": "30 minutes of exercise"}
            ],
            "afternoon_tasks": [
                {"title": "Lunch", "time": "12:00", "notes": "Nutritious lunch"},
                {"title": "Work Session", "time": "13:00", "notes": "Focus on important tasks"}
            ],
            "evening_tasks": [
                {"title": "Dinner", "time": "18:00", "notes": "Light dinner"},
                {"title": "Evening Routine", "time": "21:00", "notes": "Prepare for tomorrow"}
            ]
        }

    def get_todays_tasks(self):
        """Get all tasks for today."""
        tasks = []
        if self.schedule:
            # Combine all task categories
            for category in ["morning_tasks", "afternoon_tasks", "evening_tasks"]:
                if category in self.schedule:
                    tasks.extend(self.schedule[category])
        return tasks

    def get_catch_up_tasks(self):
        """Get missed tasks from the original task list."""
        # Only check for missed tasks once per day or if not initialized
        if not self.catch_up_tasks_initialized:
            current_time = datetime.now()
            current_hour = current_time.hour
            current_minute = current_time.minute
            current_time_minutes = current_hour * 60 + current_minute
            
            # Mark original tasks as missed instead of creating duplicates
            for task in self.today_tasks:
                task_time = task.get('time', '06:00')
                try:
                    # Parse task time
                    task_hour, task_minute = map(int, task_time.split(':'))
                    task_time_minutes = task_hour * 60 + task_minute
                    
                    # If task was scheduled for more than 30 minutes ago, mark it as missed
                    if current_time_minutes - task_time_minutes > 30:
                        task['was_missed'] = True
                        task['is_catch_up'] = True
                        task['original_time'] = task_time  # Store original time for display
                    else:
                        task['was_missed'] = False
                        task['is_catch_up'] = False
                except:
                    # If time parsing fails, assume it's not missed
                    task['was_missed'] = False
                    task['is_catch_up'] = False
            
            self.catch_up_tasks_initialized = True
        
        # Return only the missed tasks from the original list
        return [task for task in self.today_tasks if task.get('was_missed', False)]

    def get_next_task(self):
        """Get the next uncompleted task, prioritizing catch-up tasks."""
        # First, check for catch-up tasks
        catch_up_tasks = self.get_catch_up_tasks()
        if catch_up_tasks:
            print(f"🔍 DEBUG: Found {len(catch_up_tasks)} catch-up tasks")
            # Return the first uncompleted catch-up task
            for task in catch_up_tasks:
                if not task.get('completed', False) and not task.get('skipped', False):
                    print(f"🔍 DEBUG: Returning catch-up task: {task['title']} (completed: {task.get('completed', False)}, skipped: {task.get('skipped', False)})")
                    return task
            # If all catch-up tasks are completed/skipped, return None
            print(f"🔍 DEBUG: All catch-up tasks completed/skipped")
            return None
        
        # If no catch-up tasks, return the next regular uncompleted task
        for task in self.today_tasks:
            if not task.get('completed', False) and not task.get('skipped', False) and not task.get('was_missed', False):
                return task
        
        return None
    
    def _create_catch_up_notes(self, missed_tasks):
        """Create detailed notes for catch-up task."""
        notes = f"URGENT: You have {len(missed_tasks)} missed tasks to complete:\n\n"
        
        for i, task in enumerate(missed_tasks, 1):
            notes += f"{i}. {task['title']} ({task.get('time', 'Unknown')})\n"
            notes += f"   Duration: {task.get('duration', 0)} minutes\n"
            notes += f"   Instructions: {task.get('notes', 'No details')}\n\n"
        
        notes += "Complete these tasks as soon as possible to catch up with your schedule!"
        return notes
    
    def draw_catch_up_tasks(self):
        """Draw the catch-up screen for missed tasks with color-coded cards."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Get all catch-up tasks
        catch_up_tasks = self.get_catch_up_tasks()
        
        # Header Title: CATCH UP: X Missed Tasks
        header_text = f"CATCH UP: {len(catch_up_tasks)} Missed Tasks"
        header_surface, header_pos = self.responsive_text(header_text, self.large_font, 
                                                       self.get_theme_color("warning"), 0.5, 0.05, center=True)
        self.screen.blit(header_surface, header_pos)
        
        # Real-time clock
        time_text = f"Time: {self.current_time.strftime('%H:%M')}"
        time_surface, time_pos = self.responsive_text(time_text, self.font, 
                                                   self.get_theme_color("text"), 0.5, 0.12, center=True)
        self.screen.blit(time_surface, time_pos)
        
        if catch_up_tasks:
            # Display catch-up tasks with pagination
            tasks_per_page = 4
            start_idx = self.catch_up_page * tasks_per_page
            end_idx = start_idx + tasks_per_page
            current_page_tasks = catch_up_tasks[start_idx:end_idx]
            
            # Draw task cards
            y_offset = 0.2
            self.catch_up_task_rects = []
            self.catch_up_detail_rects = []
            
            for i, task in enumerate(current_page_tasks):
                task_y = y_offset + (i * 0.18)
                task_number = start_idx + i + 1
                
                # Determine card color based on status
                if task.get('completed', False):
                    card_color = self.get_theme_color("success")
                    status_text = "COMPLETED"
                elif task.get('skipped', False):
                    card_color = self.get_theme_color("error")
                    status_text = "SKIPPED"
                else:
                    card_color = self.get_theme_color("button")
                    status_text = "PENDING"
                
                # Task card
                task_rect = self.responsive_rect(0.05, task_y, 0.9, 0.15)
                pygame.draw.rect(self.screen, card_color, task_rect)
                pygame.draw.rect(self.screen, self.get_theme_color("border"), task_rect, 2)
                self.catch_up_task_rects.append(task_rect)
                
                # Task number and title
                title_text = f"{task_number}. {task['title']} ({task['original_time']})"
                title_surface, title_pos = self.responsive_text(title_text, self.font, 
                                                             self.get_theme_color("text"), 0.08, task_y + 0.02, center=False)
                self.screen.blit(title_surface, title_pos)
                
                # Task notes (truncated)
                notes = task['notes'][:60] + "..." if len(task['notes']) > 60 else task['notes']
                notes_surface, notes_pos = self.responsive_text(notes, self.small_font, 
                                                             self.get_theme_color("text"), 0.08, task_y + 0.06, center=False)
                self.screen.blit(notes_surface, notes_pos)
                
                # Status label on far right
                status_surface, status_pos = self.responsive_text(status_text, self.small_font, 
                                                               self.get_theme_color("text"), 0.75, task_y + 0.02, center=False)
                self.screen.blit(status_surface, status_pos)
                
                # View Details button (blue)
                detail_rect = self.responsive_rect(0.75, task_y + 0.06, 0.15, 0.06)
                pygame.draw.rect(self.screen, self.get_theme_color("accent"), detail_rect)
                detail_text, detail_pos = self.responsive_text("View Details", self.tiny_font, 
                                                            self.get_theme_color("text"), 0.825, task_y + 0.09, center=True)
                self.screen.blit(detail_text, detail_pos)
                self.catch_up_detail_rects.append(detail_rect)
            
            # Pagination controls
            total_pages = (len(catch_up_tasks) + tasks_per_page - 1) // tasks_per_page
            if total_pages > 1:
                page_y = 0.85
                
                # Page indicator
                page_text = f"Page {self.catch_up_page + 1} of {total_pages}"
                page_surface, page_pos = self.responsive_text(page_text, self.font, 
                                                           self.get_theme_color("text"), 0.5, page_y, center=True)
                self.screen.blit(page_surface, page_pos)
                
                # Previous page button
                if self.catch_up_page > 0:
                    prev_rect = self.responsive_rect(0.3, page_y + 0.05, 0.15, 0.08)
                    pygame.draw.rect(self.screen, self.get_theme_color("button"), prev_rect)
                    prev_text, prev_pos = self.responsive_text("← Previous", self.font, 
                                                             self.get_theme_color("text"), 0.375, page_y + 0.09, center=True)
                    self.screen.blit(prev_text, prev_pos)
                    self.catch_up_page_rects = [prev_rect]
                
                # Next page button
                if self.catch_up_page < total_pages - 1:
                    next_rect = self.responsive_rect(0.55, page_y + 0.05, 0.15, 0.08)
                    pygame.draw.rect(self.screen, self.get_theme_color("accent"), next_rect)
                    next_text, next_pos = self.responsive_text("Next →", self.font, 
                                                             self.get_theme_color("text"), 0.625, page_y + 0.09, center=True)
                    self.screen.blit(next_text, next_pos)
                    if hasattr(self, 'catch_up_page_rects'):
                        self.catch_up_page_rects.append(next_rect)
                    else:
                        self.catch_up_page_rects = [next_rect]
            
            # Bulk action buttons
            button_y = 0.95
            button_width = 0.25
            
            # ALL COMPLETE button (Green)
            complete_rect = self.responsive_rect(0.05, button_y, button_width, 0.08)
            pygame.draw.rect(self.screen, self.get_theme_color("success"), complete_rect)
            complete_text, complete_pos = self.responsive_text("ALL COMPLETE", self.font, 
                                                             self.get_theme_color("text"), 0.175, button_y + 0.04, center=True)
            self.screen.blit(complete_text, complete_pos)
            
            # DONE MARKED button (Blue)
            marked_rect = self.responsive_rect(0.35, button_y, button_width, 0.08)
            pygame.draw.rect(self.screen, self.get_theme_color("accent"), marked_rect)
            marked_text, marked_pos = self.responsive_text("DONE MARKED", self.font, 
                                                         self.get_theme_color("text"), 0.475, button_y + 0.04, center=True)
            self.screen.blit(marked_text, marked_pos)
            
            # ALL SKIP button (Red)
            skip_rect = self.responsive_rect(0.65, button_y, button_width, 0.08)
            pygame.draw.rect(self.screen, self.get_theme_color("error"), skip_rect)
            skip_text, skip_pos = self.responsive_text("ALL SKIP", self.font, 
                                                     self.get_theme_color("text"), 0.775, button_y + 0.04, center=True)
            self.screen.blit(skip_text, skip_pos)
            
            # Store bulk action rects
            self.catch_up_bulk_rects = [complete_rect, marked_rect, skip_rect]
        else:
            # No catch-up tasks message
            no_tasks_text = "No missed tasks to catch up on"
            no_tasks_surface, no_tasks_pos = self.responsive_text(no_tasks_text, self.font, 
                                                               self.get_theme_color("text"), 0.5, 0.5, center=True)
            self.screen.blit(no_tasks_surface, no_tasks_pos)
        
        # Back button
        self.catch_up_back_rect = self.responsive_rect(0.4, 0.02, 0.2, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.catch_up_back_rect)
        back_text, back_pos = self.responsive_text("← Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.05, center=True)
        self.screen.blit(back_text, back_pos)
    
    def export_progress(self):
        """Export progress to a file."""
        try:
            timestamp = self.current_time.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"progress_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("RASPBERRY PI DAY PLANNER - PROGRESS REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Date: {self.current_time.strftime('%A, %B %d, %Y')}\n")
                f.write(f"Time: {self.current_time.strftime('%H:%M:%S')}\n\n")
                
                # Summary
                completed_count = len([t for t in self.today_tasks if t.get('completed', False)])
                skipped_count = len([t for t in self.today_tasks if t.get('skipped', False)])
                total_count = len(self.today_tasks)
                
                f.write(f"SUMMARY:\n")
                f.write(f"Total Tasks: {total_count}\n")
                f.write(f"Completed: {completed_count}\n")
                f.write(f"Skipped: {skipped_count}\n")
                f.write(f"Remaining: {total_count - completed_count - skipped_count}\n\n")
                
                # Completed tasks
                if self.completed_tasks:
                    f.write("COMPLETED TASKS:\n")
                    f.write("-" * 20 + "\n")
                    for task in self.completed_tasks:
                        f.write(f"✅ {task['title']} ({task['time']}) - Completed at {task['completed_at']}\n")
                    f.write("\n")
                
                # Skipped tasks
                if self.skipped_tasks:
                    f.write("SKIPPED TASKS:\n")
                    f.write("-" * 20 + "\n")
                    for task in self.skipped_tasks:
                        f.write(f"⏭️ {task['title']} ({task['time']}) - Skipped at {task['skipped_at']}\n")
                    f.write("\n")
                
                # Remaining tasks
                remaining_tasks = [t for t in self.today_tasks if not t.get('completed', False) and not t.get('skipped', False)]
                if remaining_tasks:
                    f.write("REMAINING TASKS:\n")
                    f.write("-" * 20 + "\n")
                    for task in remaining_tasks:
                        f.write(f"⏳ {task['title']} ({task.get('time', 'Unknown')}) - {task.get('notes', 'No details')}\n")
            
            print(f"📄 Progress exported to {filename}")
            
            # PHASE 4: Show mood prompt after export
            self.show_mood_prompt = True
            
        except Exception as e:
            print(f"❌ Error exporting progress: {e}")
    
    def draw_idle_screen(self):
        """Draw the idle screen with responsive design."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Current time with responsive positioning
        time_text = self.current_time.strftime("%H:%M:%S")
        time_surface, time_pos = self.responsive_text(time_text, self.large_font, 
                                                    self.get_theme_color("text"), 0.5, 0.1, center=True)
        self.screen.blit(time_surface, time_pos)
        
        # Date
        date_text = self.current_time.strftime("%A, %B %d, %Y")
        date_surface, date_pos = self.responsive_text(date_text, self.font, 
                                                    self.get_theme_color("text"), 0.5, 0.15, center=True)
        self.screen.blit(date_surface, date_pos)
        
        # Next task info (cached to prevent infinite loop)
        if not hasattr(self, 'cached_next_task') or self.cached_next_task is None:
            self.cached_next_task = self.get_next_task()
        
        next_task = self.cached_next_task
        if next_task:
            if next_task.get('is_catch_up'):
                # Get actual catch-up tasks count
                catch_up_tasks = self.get_catch_up_tasks()
                next_text = f"CATCH UP: {len(catch_up_tasks)} Missed Tasks"
                next_surface, next_pos = self.responsive_text(next_text, self.font, 
                                                            self.get_theme_color("warning"), 0.5, 0.25, center=True)
                self.screen.blit(next_surface, next_pos)
                
                time_text = "ASAP - Complete missed morning tasks"
                time_surface, time_pos = self.responsive_text(time_text, self.small_font, 
                                                            self.get_theme_color("warning"), 0.5, 0.28, center=True)
                self.screen.blit(time_surface, time_pos)
            else:
                next_text = f"Next: {next_task['title']}"
                next_surface, next_pos = self.responsive_text(next_text, self.font, 
                                                            self.get_theme_color("text"), 0.5, 0.25, center=True)
                self.screen.blit(next_surface, next_pos)
                
                time_text = f"at {self.format_time_for_display(next_task['time'])}"
                time_surface, time_pos = self.responsive_text(time_text, self.small_font, 
                                                            self.get_theme_color("warning"), 0.5, 0.28, center=True)
                self.screen.blit(time_surface, time_pos)
        else:
            done_text = "All tasks completed for today!"
            done_surface, done_pos = self.responsive_text(done_text, self.font, 
                                                        self.get_theme_color("warning"), 0.5, 0.25, center=True)
            self.screen.blit(done_surface, done_pos)
        
        # Progress info
        completed_count = len([t for t in self.today_tasks if t.get('completed', False)])
        skipped_count = len([t for t in self.today_tasks if t.get('skipped', False)])
        total_count = len(self.today_tasks)
        
        progress_text = f"Progress: {completed_count}/{total_count} completed, {skipped_count} skipped"
        progress_surface, progress_pos = self.responsive_text(progress_text, self.small_font, 
                                                           self.get_theme_color("text"), 0.5, 0.32, center=True)
        self.screen.blit(progress_surface, progress_pos)
        
        # Instructions with better spacing
        instructions = [
            "Press SPACE to simulate task notification",
            "Press T to toggle theme",
            "Press V for voice settings",
            "Press S for stats"
        ]
        
        instruction_y = 0.45
        instruction_spacing = 0.06
        for i, instruction in enumerate(instructions):
            instruction_surface, instruction_pos = self.responsive_text(instruction, self.small_font, 
                                                                     self.get_theme_color("text"), 0.5, 
                                                                     instruction_y + i * instruction_spacing, center=True)
            self.screen.blit(instruction_surface, instruction_pos)
        
        # Buttons with responsive positioning
        button_y = 0.75
        button_spacing = 0.12
        
        # Start Task button
        start_rect = self.responsive_rect(0.1, button_y, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), start_rect)
        start_text, start_pos = self.responsive_text("Start Task", self.font, 
                                                   self.get_theme_color("text"), 0.175, button_y + 0.04, center=True)
        self.screen.blit(start_text, start_pos)
        
        # View Backlog button
        backlog_rect = self.responsive_rect(0.3, button_y, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), backlog_rect)
        backlog_text, backlog_pos = self.responsive_text("View Backlog", self.font, 
                                                       self.get_theme_color("text"), 0.375, button_y + 0.04, center=True)
        self.screen.blit(backlog_text, backlog_pos)
        
        # View Skipped Tasks button
        skipped_rect = self.responsive_rect(0.5, button_y, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("warning"), skipped_rect)
        skipped_text, skipped_pos = self.responsive_text("Skipped Tasks", self.font, 
                                                       self.get_theme_color("text"), 0.575, button_y + 0.04, center=True)
        self.screen.blit(skipped_text, skipped_pos)
        
        # View Stats button
        stats_rect = self.responsive_rect(0.7, button_y, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), stats_rect)
        stats_text, stats_pos = self.responsive_text("View Stats", self.font, 
                                                   self.get_theme_color("text"), 0.775, button_y + 0.04, center=True)
        self.screen.blit(stats_text, stats_pos)
        
        # Voice Settings button
        voice_rect = self.responsive_rect(0.1, button_y + button_spacing, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), voice_rect)
        voice_text, voice_pos = self.responsive_text("Voice Settings", self.font, 
                                                   self.get_theme_color("text"), 0.175, button_y + button_spacing + 0.04, center=True)
        self.screen.blit(voice_text, voice_pos)
        
        # NEW: Focus Mode button
        focus_rect = self.responsive_rect(0.3, button_y + button_spacing, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("focus"), focus_rect)
        focus_text, focus_pos = self.responsive_text("Focus Mode", self.font, 
                                                   self.get_theme_color("text"), 0.375, button_y + button_spacing + 0.04, center=True)
        self.screen.blit(focus_text, focus_pos)
        
        # NEW: View All Tasks button
        all_tasks_rect = self.responsive_rect(0.5, button_y + button_spacing, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("accent"), all_tasks_rect)
        all_tasks_text, all_tasks_pos = self.responsive_text("All Tasks", self.font, 
                                                            self.get_theme_color("text"), 0.575, button_y + button_spacing + 0.04, center=True)
        self.screen.blit(all_tasks_text, all_tasks_pos)
        
        # NEW: Achievements button
        achievements_rect = self.responsive_rect(0.7, button_y + button_spacing, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), achievements_rect)
        achievements_text, achievements_pos = self.responsive_text("Achievements", self.font, 
                                                                self.get_theme_color("text"), 0.775, button_y + button_spacing + 0.04, center=True)
        self.screen.blit(achievements_text, achievements_pos)
        
        # NEW: Add Task button (Phase 6)
        add_task_rect = self.responsive_rect(0.1, button_y + button_spacing * 2, 0.15, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("success"), add_task_rect)
        add_task_text, add_task_pos = self.responsive_text("Add Task", self.font, 
                                                          self.get_theme_color("text"), 0.175, button_y + button_spacing * 2 + 0.04, center=True)
        self.screen.blit(add_task_text, add_task_pos)
        
        return start_rect, backlog_rect, skipped_rect, stats_rect, voice_rect, focus_rect, all_tasks_rect, achievements_rect, add_task_rect

    def draw_focus_mode_screen(self):
        """Draw the focus mode screen with Pomodoro timer."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Title
        title_text, title_pos = self.responsive_text("🎯 Focus Mode", self.large_font, 
                                                   self.get_theme_color("focus"), 0.5, 0.1, center=True)
        self.screen.blit(title_text, title_pos)
        
        # Task being focused on
        if self.focus_task:
            task_text = f"Focusing on: {self.focus_task.get('title', 'task')}"
            task_surface, task_pos = self.responsive_text(task_text, self.font, 
                                                        self.get_theme_color("text"), 0.5, 0.2, center=True)
            self.screen.blit(task_surface, task_pos)
        
        # Pomodoro timer
        remaining = self.get_pomodoro_time_remaining()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        timer_text = f"{minutes:02d}:{seconds:02d}"
        
        # Timer color based on remaining time
        if remaining > 600:  # More than 10 minutes
            timer_color = self.get_theme_color("success")
        elif remaining > 300:  # More than 5 minutes
            timer_color = self.get_theme_color("warning")
        else:
            timer_color = self.get_theme_color("error")
        
        timer_surface, timer_pos = self.responsive_text(timer_text, self.large_font, 
                                                      timer_color, 0.5, 0.35, center=True)
        self.screen.blit(timer_surface, timer_pos)
        
        # Status text
        if self.pomodoro_paused:
            status_text = "⏸️ PAUSED"
            status_color = self.get_theme_color("warning")
        else:
            status_text = "▶️ RUNNING"
            status_color = self.get_theme_color("success")
        
        status_surface, status_pos = self.responsive_text(status_text, self.font, 
                                                        status_color, 0.5, 0.45, center=True)
        self.screen.blit(status_surface, status_pos)
        
        # Control buttons
        button_y = 0.6
        
        # Pause/Resume button
        if self.pomodoro_paused:
            pause_text = "▶️ Resume"
        else:
            pause_text = "⏸️ Pause"
        
        pause_rect = self.responsive_rect(0.2, button_y, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), pause_rect)
        pause_surface, pause_pos = self.responsive_text(pause_text, self.font, 
                                                      self.get_theme_color("text"), 0.3, button_y + 0.04, center=True)
        self.screen.blit(pause_surface, pause_pos)
        
        # End Focus button
        end_rect = self.responsive_rect(0.6, button_y, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("error"), end_rect)
        end_surface, end_pos = self.responsive_text("End Focus", self.font, 
                                                  self.get_theme_color("text"), 0.7, button_y + 0.04, center=True)
        self.screen.blit(end_surface, end_pos)
        
        return pause_rect, end_rect

    def draw_distraction_alert_screen(self):
        """Draw the distraction alert screen."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Warning icon and title
        warning_text, warning_pos = self.responsive_text("⚠️ DISTRACTION ALERT", self.large_font, 
                                                       self.get_theme_color("distraction"), 0.5, 0.2, center=True)
        self.screen.blit(warning_text, warning_pos)
        
        # Message
        message_text = "You've been inactive for a while.\nAre you getting distracted?"
        message_surface, message_pos = self.responsive_text(message_text, self.font, 
                                                         self.get_theme_color("text"), 0.5, 0.35, center=True)
        self.screen.blit(message_surface, message_pos)
        
        # Time since last interaction
        time_since = int(time.time() - self.last_interaction_time)
        time_text = f"Inactive for {time_since} seconds"
        time_surface, time_pos = self.responsive_text(time_text, self.small_font, 
                                                    self.get_theme_color("warning"), 0.5, 0.45, center=True)
        self.screen.blit(time_surface, time_pos)
        
        # Dismiss button
        dismiss_rect = self.responsive_rect(0.4, 0.7, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), dismiss_rect)
        dismiss_surface, dismiss_pos = self.responsive_text("I'm Back!", self.font, 
                                                          self.get_theme_color("text"), 0.5, 0.74, center=True)
        self.screen.blit(dismiss_surface, dismiss_pos)
        
        return dismiss_rect

    def draw_notification_screen(self):
        """Draw the task notification screen with theme support."""
        if not self.current_task:
            return
        
        self.screen.fill(self.get_theme_color("background"))
        
        # Back button (top left) with responsive sizing
        back_rect = self.responsive_rect(0.02, 0.02, 0.08, 0.04)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), back_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), back_rect, 2)
        back_text = self.small_font.render("< Back", True, self.get_theme_color("text"))
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        self.notification_back_button_rect = back_rect
        
        # Task title with responsive text
        title_text = self.current_task['title']
        title_lines = self.responsive_text(title_text, "large", self.WHITE, 0.5, 0.1)
        title_y = self.height * 0.1
        for i, line in enumerate(title_lines):
            line_rect = line.get_rect(center=(self.width//2, title_y + i * self.large_font_size))
            self.screen.blit(line, line_rect)
        
        # Timer overlay if active
        if self.task_timer and self.task_timer.timer_running:
            self._draw_timer_overlay()
        
        # Task time - use dynamic current time for catch-up tasks
        if self.current_task.get('is_catch_up', False):
            time_text = f"Time: {self.current_time.strftime('%H:%M')}"
        else:
            time_text = f"Time: {self.current_task.get('time', 'Unknown')}"
        time_lines = self.responsive_text(time_text, "base", self.YELLOW, 0.5, 0.15)
        time_y = self.height * 0.15
        for i, line in enumerate(time_lines):
            line_rect = line.get_rect(center=(self.width//2, time_y + i * self.base_font_size))
            self.screen.blit(line, line_rect)
        
        if self.current_task.get('is_catch_up', False):
            # Draw catch-up tasks with individual controls (includes its own buttons)
            self.draw_catch_up_tasks()
        else:
            # Task notes (wrapped) with responsive positioning
            notes = self.current_task.get('notes', 'No details available')
            notes_lines = self.responsive_text(notes, "base", self.WHITE, 0.5, 0.2)
            notes_y = self.height * 0.2
            for i, line in enumerate(notes_lines):
                line_rect = line.get_rect(center=(self.width//2, notes_y + i * self.base_font_size))
                self.screen.blit(line, line_rect)
            
            # Buttons - only for non-catch-up tasks with responsive sizing
            button_y = self.height * 0.85
            button_width = self.width * 0.12
            button_height = self.height * 0.06
            button_spacing = self.width * 0.02
            
            # DONE button
            done_rect = self.responsive_rect(0.35, 0.85, 0.12, 0.06)
            pygame.draw.rect(self.screen, self.get_theme_color("success"), done_rect)
            pygame.draw.rect(self.screen, self.get_theme_color("border"), done_rect, 2)
            done_text = self.font.render("DONE", True, self.get_theme_color("text"))
            done_text_rect = done_text.get_rect(center=done_rect.center)
            self.screen.blit(done_text, done_text_rect)
            
            # SKIP button
            skip_rect = self.responsive_rect(0.53, 0.85, 0.12, 0.06)
            pygame.draw.rect(self.screen, self.get_theme_color("error"), skip_rect)
            pygame.draw.rect(self.screen, self.get_theme_color("border"), skip_rect, 2)
            skip_text = self.font.render("SKIP", True, self.get_theme_color("text"))
            skip_text_rect = skip_text.get_rect(center=skip_rect.center)
            self.screen.blit(skip_text, skip_text_rect)
            
            # Store button rects for click detection
            self.done_button_rect = done_rect
            self.skip_button_rect = skip_rect
    
    def draw_skipped_tasks_screen(self):
        """Draw the skipped tasks screen."""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = "Skipped Tasks"
        title_surface = self.large_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.width//2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Back button
        back_rect = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, self.GRAY, back_rect)
        back_text = self.small_font.render("< Back", True, self.WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        self.skipped_back_button_rect = back_rect
        
        # Get skipped tasks
        skipped_tasks = [task for task in self.today_tasks if task.get('skipped', False)]
        
        if not skipped_tasks:
            no_tasks_text = "No skipped tasks"
            no_tasks_surface = self.medium_font.render(no_tasks_text, True, self.GRAY)
            no_tasks_rect = no_tasks_surface.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(no_tasks_surface, no_tasks_rect)
            return
        
        # Display skipped tasks
        start_y = 120
        task_height = 80
        self.skipped_task_buttons = []  # Clear to prevent accumulation
        
        for i, task in enumerate(skipped_tasks):
            y_pos = start_y + (i * (task_height + 10))
            
            if y_pos + task_height > self.height - 100:  # Leave space for back button
                break
            
            # Task box
            task_rect = pygame.Rect(50, y_pos, self.width - 100, task_height)
            pygame.draw.rect(self.screen, self.DARK_GRAY, task_rect)
            pygame.draw.rect(self.screen, self.GRAY, task_rect, 2)
            
            # Task title
            title_text = task.get('title', 'Unknown Task')
            title_surface = self.medium_font.render(title_text, True, self.WHITE)
            title_rect = title_surface.get_rect(x=60, y=y_pos + 10)
            self.screen.blit(title_surface, title_rect)
            
            # Task time
            time_text = f"Time: {task.get('time', 'Unknown')}"
            time_surface = self.small_font.render(time_text, True, self.YELLOW)
            time_rect = time_surface.get_rect(x=60, y=y_pos + 35)
            self.screen.blit(time_surface, time_rect)
            
            # Complete button
            complete_button_rect = pygame.Rect(self.width - 150, y_pos + 20, 80, 40)
            pygame.draw.rect(self.screen, self.GREEN, complete_button_rect)
            complete_text = self.small_font.render("Complete", True, self.BLACK)
            complete_text_rect = complete_text.get_rect(center=complete_button_rect.center)
            self.screen.blit(complete_text, complete_text_rect)
            
            # Store button info for click handling
            self.skipped_task_buttons.append({
                'task': task,
                'complete_button': complete_button_rect
            })

    def draw_backlog_screen(self):
        """Draw the backlog screen showing incomplete tasks from last 7 days."""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = "Task Backlog"
        title_surface = self.large_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.width//2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Back button
        back_rect = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, self.GRAY, back_rect)
        back_text = self.small_font.render("< Back", True, self.WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        self.backlog_back_button_rect = back_rect
        
        if not self.backlog_manager:
            no_backlog_text = "Backlog manager not available"
            no_backlog_surface = self.medium_font.render(no_backlog_text, True, self.GRAY)
            no_backlog_rect = no_backlog_surface.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(no_backlog_surface, no_backlog_rect)
            return
        
        # Get backlog tasks
        backlog_tasks = self.backlog_manager.get_backlog_tasks()
        
        if not backlog_tasks:
            no_tasks_text = "No backlog tasks"
            no_tasks_surface = self.medium_font.render(no_tasks_text, True, self.GRAY)
            no_tasks_rect = no_tasks_surface.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(no_tasks_surface, no_tasks_rect)
            return
        
        # Display backlog tasks
        start_y = 120
        task_height = 100
        self.backlog_task_buttons = []  # Clear to prevent accumulation
        
        for i, task in enumerate(backlog_tasks):
            y_pos = start_y + (i * (task_height + 10))
            
            if y_pos + task_height > self.height - 100:  # Leave space for back button
                break
            
            # Task box
            task_rect = pygame.Rect(50, y_pos, self.width - 100, task_height)
            pygame.draw.rect(self.screen, self.DARK_GRAY, task_rect)
            pygame.draw.rect(self.screen, self.GRAY, task_rect, 2)
            
            # Task title
            title_text = task.get('task_title', 'Unknown Task')
            title_surface = self.medium_font.render(title_text, True, self.WHITE)
            title_rect = title_surface.get_rect(x=60, y=y_pos + 10)
            self.screen.blit(title_surface, title_rect)
            
            # Original date
            original_date = task.get('original_date', 'Unknown')
            date_text = f"Original Date: {original_date}"
            date_surface = self.small_font.render(date_text, True, self.YELLOW)
            date_rect = date_surface.get_rect(x=60, y=y_pos + 35)
            self.screen.blit(date_surface, date_rect)
            
            # Reason (truncated if too long)
            reason = task.get('reason', 'No reason provided')
            if len(reason) > 50:
                reason = reason[:47] + "..."
            reason_text = f"Reason: {reason}"
            reason_surface = self.small_font.render(reason_text, True, self.GRAY)
            reason_rect = reason_surface.get_rect(x=60, y=y_pos + 55)
            self.screen.blit(reason_surface, reason_rect)
            
            # Priority indicator
            priority = task.get('priority', 3)
            priority_color = self.RED if priority <= 2 else self.YELLOW if priority == 3 else self.GREEN
            priority_text = f"Priority: {priority}"
            priority_surface = self.small_font.render(priority_text, True, priority_color)
            priority_rect = priority_surface.get_rect(x=60, y=y_pos + 75)
            self.screen.blit(priority_surface, priority_rect)
            
            # Redeem button
            redeem_button_rect = pygame.Rect(self.width - 150, y_pos + 30, 80, 40)
            pygame.draw.rect(self.screen, self.GREEN, redeem_button_rect)
            redeem_text = self.small_font.render("Redeem", True, self.BLACK)
            redeem_text_rect = redeem_text.get_rect(center=redeem_button_rect.center)
            self.screen.blit(redeem_text, redeem_text_rect)
            
            # Store button info for click handling
            self.backlog_task_buttons.append({
                'task': task,
                'redeem_button': redeem_button_rect
            })
    
    def draw_detail_screen(self):
        """Draw the detail view screen for a specific task."""
        if not self.detail_task:
            return
        
        self.screen.fill(self.BLACK)
        
        # Back button
        back_rect = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, self.GRAY, back_rect)
        back_text = self.medium_font.render("< Back", True, self.WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        self.back_button_rect = back_rect
        
        # Task title
        title_text = self.detail_task['title']
        title_surface = self.large_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.width//2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Task time
        time_text = f"Time: {self.detail_task.get('time', 'Unknown')}"
        time_surface = self.medium_font.render(time_text, True, self.YELLOW)
        time_rect = time_surface.get_rect(center=(self.width//2, 150))
        self.screen.blit(time_surface, time_rect)
        
        # Full task details (wrapped)
        notes = self.detail_task.get('notes', 'No details available')
        self.draw_wrapped_text(notes, self.medium_font, self.WHITE, 
                             self.width//2, 200, self.width - 100)
        
        # Action buttons at bottom
        button_y = self.height - 80
        button_width = 120
        button_height = 50
        spacing = 20
        
        # Complete button
        complete_rect = pygame.Rect(self.width//2 - button_width - spacing//2, button_y, 
                                   button_width, button_height)
        pygame.draw.rect(self.screen, self.GREEN, complete_rect)
        complete_text = self.medium_font.render("Complete", True, self.BLACK)
        complete_text_rect = complete_text.get_rect(center=complete_rect.center)
        self.screen.blit(complete_text, complete_text_rect)
        
        # Skip button
        skip_rect = pygame.Rect(self.width//2 + spacing//2, button_y, 
                               button_width, button_height)
        pygame.draw.rect(self.screen, self.RED, skip_rect)
        skip_text = self.medium_font.render("Skip", True, self.WHITE)
        skip_text_rect = skip_text.get_rect(center=skip_rect.center)
        self.screen.blit(skip_text, skip_text_rect)
        
        # Store button rects
        self.detail_complete_rect = complete_rect
        self.detail_skip_rect = skip_rect

    def draw_analytics_screen(self):
        """Draw the analytics screen showing progress charts and statistics."""
        self.screen.fill(self.BLACK)
        
        # Back button
        back_rect = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, self.GRAY, back_rect)
        back_text = self.small_font.render("< Back", True, self.WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        self.analytics_back_button_rect = back_rect
        
        # Title
        title_text = "Today's Progress Chart"
        title_surface = self.large_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.width//2, 80))
        self.screen.blit(title_surface, title_rect)
        
        try:
            # Calculate current session data
            if self.today_tasks:
                total_tasks = len(self.today_tasks)
                completed_tasks = len([t for t in self.today_tasks if t.get('completed', False)])
                skipped_tasks = len([t for t in self.today_tasks if t.get('skipped', False)])
                completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                skip_rate = (skipped_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                # Create current session data
                today = datetime.now().strftime('%Y-%m-%d')
                current_session_data = {
                    'dates': [today],
                    'completion_percentages': [completion_rate],
                    'skip_percentages': [skip_rate],
                    'total_tasks': [total_tasks],
                    'completed_tasks': [completed_tasks],
                    'skipped_tasks': [skipped_tasks],
                    'average_completion': completion_rate,
                    'total_days': 1
                }
                
                # Use current session data instead of database data
                analytics_data = current_session_data
            
            if analytics_data and analytics_data.get('total_days', 0) > 0:
                # Calculate statistics
                completion_rates = analytics_data.get('completion_percentages', [])
                skip_rates = analytics_data.get('skip_percentages', [])
                dates = analytics_data.get('dates', [])
                
                # Calculate streaks and missed days
                current_streak = 0
                longest_streak = 0
                missed_days = 0
                temp_streak = 0
                
                for rate in completion_rates:
                    if rate >= 80:  # Consider 80%+ as a "good" day
                        temp_streak += 1
                        current_streak = temp_streak
                        longest_streak = max(longest_streak, temp_streak)
                    else:
                        if temp_streak > 0:
                            missed_days += 1
                        temp_streak = 0
                
                # Display summary stats
                y_pos = 150
                spacing = 25
                
                # Total focus percentage (average completion)
                avg_completion = analytics_data.get('average_completion', 0)
                focus_text = f"Total Focus: {avg_completion:.1f}%"
                focus_surface = self.medium_font.render(focus_text, True, self.GREEN)
                focus_rect = focus_surface.get_rect(center=(self.width//2, y_pos))
                self.screen.blit(focus_surface, focus_rect)
                y_pos += spacing
                
                # Current streak
                streak_text = f"Current Streak: {current_streak} days"
                streak_surface = self.medium_font.render(streak_text, True, self.YELLOW)
                streak_rect = streak_surface.get_rect(center=(self.width//2, y_pos))
                self.screen.blit(streak_surface, streak_rect)
                y_pos += spacing
                
                # Longest streak
                longest_text = f"Longest Streak: {longest_streak} days"
                longest_surface = self.medium_font.render(longest_text, True, self.BLUE)
                longest_rect = longest_surface.get_rect(center=(self.width//2, y_pos))
                self.screen.blit(longest_surface, longest_rect)
                y_pos += spacing
                
                # Missed days
                missed_text = f"Missed Days: {missed_days}"
                missed_surface = self.medium_font.render(missed_text, True, self.RED)
                missed_rect = missed_surface.get_rect(center=(self.width//2, y_pos))
                self.screen.blit(missed_surface, missed_rect)
                y_pos += spacing + 20
                
                # Draw horizontal bar chart
                chart_title = "Today's Completion vs Skip Rate"
                chart_surface = self.small_font.render(chart_title, True, self.WHITE)
                chart_rect = chart_surface.get_rect(center=(self.width//2, y_pos))
                self.screen.blit(chart_surface, chart_rect)
                y_pos += 30
                
                # Chart dimensions
                chart_width = self.width - 100
                chart_height = 200
                chart_x = 50
                chart_y = y_pos
                
                # Draw chart background
                chart_bg_rect = pygame.Rect(chart_x, chart_y, chart_width, chart_height)
                pygame.draw.rect(self.screen, self.DARK_GRAY, chart_bg_rect)
                pygame.draw.rect(self.screen, self.GRAY, chart_bg_rect, 2)
                
                # Calculate bar dimensions
                bar_height = chart_height // len(completion_rates) if completion_rates else 20
                bar_spacing = 5
                
                # Draw bars for each day
                for i, (completion_rate, skip_rate, date) in enumerate(zip(completion_rates, skip_rates, dates)):
                    bar_y = chart_y + (i * (bar_height + bar_spacing))
                    
                    # Day label
                    day_label = date[-5:] if len(date) > 5 else date  # Show MM-DD
                    day_surface = self.tiny_font.render(day_label, True, self.WHITE)
                    day_rect = day_surface.get_rect(midright=(chart_x - 10, bar_y + bar_height//2))
                    self.screen.blit(day_surface, day_rect)
                    
                    # Completion bar (green)
                    completion_width = int((completion_rate / 100) * chart_width)
                    if completion_width > 0:
                        completion_rect = pygame.Rect(chart_x, bar_y, completion_width, bar_height)
                        pygame.draw.rect(self.screen, self.GREEN, completion_rect)
                    
                    # Skip bar (red) - on top of completion bar
                    skip_width = int((skip_rate / 100) * chart_width)
                    if skip_width > 0:
                        skip_rect = pygame.Rect(chart_x + completion_width, bar_y, skip_width, bar_height)
                        pygame.draw.rect(self.screen, self.RED, skip_rect)
                    
                    # Percentage labels
                    if completion_rate > 0:
                        comp_label = f"{completion_rate:.0f}%"
                        comp_surface = self.tiny_font.render(comp_label, True, self.BLACK)
                        comp_rect = comp_surface.get_rect(center=(chart_x + completion_width//2, bar_y + bar_height//2))
                        self.screen.blit(comp_surface, comp_rect)
                    
                    if skip_rate > 0:
                        skip_label = f"{skip_rate:.0f}%"
                        skip_surface = self.tiny_font.render(skip_label, True, self.WHITE)
                        skip_rect = skip_surface.get_rect(center=(chart_x + completion_width + skip_width//2, bar_y + bar_height//2))
                        self.screen.blit(skip_surface, skip_rect)
                
                # Chart legend
                legend_y = chart_y + chart_height + 20
                
                # Completion legend
                comp_legend_rect = pygame.Rect(chart_x, legend_y, 20, 15)
                pygame.draw.rect(self.screen, self.GREEN, comp_legend_rect)
                comp_legend_text = self.tiny_font.render("Completed", True, self.WHITE)
                comp_legend_text_rect = comp_legend_text.get_rect(midleft=(chart_x + 30, legend_y + 7))
                self.screen.blit(comp_legend_text, comp_legend_text_rect)
                
                # Skip legend
                skip_legend_rect = pygame.Rect(chart_x + 150, legend_y, 20, 15)
                pygame.draw.rect(self.screen, self.RED, skip_legend_rect)
                skip_legend_text = self.tiny_font.render("Skipped", True, self.WHITE)
                skip_legend_text_rect = skip_legend_text.get_rect(midleft=(chart_x + 180, legend_y + 7))
                self.screen.blit(skip_legend_text, skip_legend_text_rect)
                
                # Instructions
                inst_text = "Press S to save current progress to database"
                inst_surface = self.small_font.render(inst_text, True, self.GRAY)
                inst_rect = inst_surface.get_rect(center=(self.width//2, self.height - 50))
                self.screen.blit(inst_surface, inst_rect)
                
            else:
                # No data available
                no_data_text = "No analytics data available yet."
                no_data_surface = self.medium_font.render(no_data_text, True, self.YELLOW)
                no_data_rect = no_data_surface.get_rect(center=(self.width//2, 200))
                self.screen.blit(no_data_surface, no_data_rect)
                
                help_text = "Complete some tasks and save progress to see the burn chart."
                help_surface = self.small_font.render(help_text, True, self.GRAY)
                help_rect = help_surface.get_rect(center=(self.width//2, 250))
                self.screen.blit(help_surface, help_rect)
                
        except Exception as e:
            # Error handling
            error_text = f"Error loading analytics: {str(e)}"
            error_surface = self.small_font.render(error_text, True, self.RED)
            error_rect = error_surface.get_rect(center=(self.width//2, 200))
            self.screen.blit(error_surface, error_rect)

    def draw_popup(self):
        """Draw a popup message overlay with theme support."""
        if not self.show_popup:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(self.get_theme_color("background"))
        self.screen.blit(overlay, (0, 0))
        
        # Popup box with responsive sizing (larger for details)
        popup_width = self.width * 0.6
        popup_height = self.height * 0.5
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        
        # Background color based on type
        if self.popup_type == "warning":
            bg_color = self.get_theme_color("warning")
        elif self.popup_type == "error":
            bg_color = self.get_theme_color("error")
        else:
            bg_color = self.get_theme_color("accent")
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, bg_color, popup_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), popup_rect, 3)
        
        # Title with responsive text
        title_surface, title_pos = self.responsive_text(self.popup_title, self.font, 
                                                      self.get_theme_color("text"), 0.5, (popup_y + 20) / self.height, center=True)
        self.screen.blit(title_surface, title_pos)
        
        # Draw wrapped message text within popup boundaries
        text_start_y = popup_y + 80
        text_end_y = popup_y + popup_height - 80  # Leave space for close button
        self.draw_wrapped_text(self.popup_message, self.small_font, self.get_theme_color("text"), 
                              popup_x + 20, text_start_y, popup_width - 40, text_end_y)
        
        # Handle different popup types
        if self.popup_type == "exit_confirmation":
            # Yes/No buttons for exit confirmation
            yes_rect = self.responsive_rect(0.35, 0.75, 0.1, 0.05)
            no_rect = self.responsive_rect(0.55, 0.75, 0.1, 0.05)
            
            # Yes button (red for exit)
            pygame.draw.rect(self.screen, self.get_theme_color("error"), yes_rect)
            pygame.draw.rect(self.screen, self.get_theme_color("border"), yes_rect, 2)
            yes_text, yes_pos = self.responsive_text("Yes", self.font, 
                                                   self.get_theme_color("text"), 0.4, 0.775, center=True)
            self.screen.blit(yes_text, yes_pos)
            self.popup_yes_rect = yes_rect
            
            # No button (green for cancel)
            pygame.draw.rect(self.screen, self.get_theme_color("success"), no_rect)
            pygame.draw.rect(self.screen, self.get_theme_color("border"), no_rect, 2)
            no_text, no_pos = self.responsive_text("No", self.font, 
                                                  self.get_theme_color("text"), 0.6, 0.775, center=True)
            self.screen.blit(no_text, no_pos)
            self.popup_no_rect = no_rect
        else:
            # Regular close button
            close_rect = self.responsive_rect(0.45, 0.75, 0.1, 0.05)
            pygame.draw.rect(self.screen, self.get_theme_color("button"), close_rect)
            pygame.draw.rect(self.screen, self.get_theme_color("border"), close_rect, 2)
            close_text, close_pos = self.responsive_text("Close", self.font, 
                                                       self.get_theme_color("text"), 0.5, 0.775, center=True)
            self.screen.blit(close_text, close_pos)
            self.popup_close_rect = close_rect
    
    def show_warning_popup(self, title, message):
        """Show a warning popup."""
        self.show_popup = True
        self.popup_title = title
        self.popup_message = message
        self.popup_type = "warning"
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width, max_height=None):
        """Draw text with word wrapping within specified boundaries."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        line_height = 30
        for i, line in enumerate(lines):
            # Check if we've exceeded max height
            if max_height and (y + i * line_height) > max_height:
                break
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect(left=x, top=y + i * line_height)
            self.screen.blit(line_surface, line_rect)
    
    def _draw_timer_overlay(self):
        """Draw the timer overlay on the notification screen."""
        if not self.task_timer or not self.task_timer.is_running:
            return
        
        # Timer background (semi-transparent)
        timer_bg = pygame.Surface((200, 80))
        timer_bg.set_alpha(200)
        timer_bg.fill(self.DARK_GRAY)
        
        # Position timer in top-right corner
        timer_x = self.width - 220
        timer_y = 20
        self.screen.blit(timer_bg, (timer_x, timer_y))
        
        # Timer border
        timer_rect = pygame.Rect(timer_x, timer_y, 200, 80)
        pygame.draw.rect(self.screen, self.GRAY, timer_rect, 2)
        
        # Timer label
        timer_label = self.small_font.render("TIME REMAINING", True, self.WHITE)
        timer_label_rect = timer_label.get_rect(center=(timer_x + 100, timer_y + 20))
        self.screen.blit(timer_label, timer_label_rect)
        
        # Timer display
        time_remaining = self.task_timer.get_formatted_time()
        time_color = self.GREEN if self.task_timer.get_time_remaining() > 60 else self.RED
        
        timer_display = self.medium_font.render(time_remaining, True, time_color)
        timer_display_rect = timer_display.get_rect(center=(timer_x + 100, timer_y + 50))
        self.screen.blit(timer_display, timer_display_rect)
    
    def handle_click(self, pos):
        """Handle mouse clicks on buttons."""
        # Handle popup clicks first
        if self.show_popup:
            if hasattr(self, 'popup_close_rect') and self.popup_close_rect.collidepoint(pos):
                self.show_popup = False
                return True
            return True  # Block other clicks when popup is shown
        
        if self.current_screen == "detail":
            # Handle detail screen clicks
            if hasattr(self, 'back_button_rect') and self.back_button_rect.collidepoint(pos):
                self.showing_details = False
                self.detail_task = None
                self.current_screen = "notification"
                return True
            
            if hasattr(self, 'detail_complete_rect') and self.detail_complete_rect.collidepoint(pos):
                if self.detail_task:
                    self.detail_task['completed'] = True
                    self.completed_tasks.append({
                        'title': self.detail_task['title'],
                        'time': self.detail_task.get('time', 'Unknown'),
                        'completed_at': self.current_time.strftime("%H:%M:%S"),
                        'was_catch_up': True
                    })
                    
                    # PHASE 4: Track completed tasks for encouragement
                    self.completed_tasks_count += 1
                    self.offer_encouragement()
                    
                    print(f"✅ Task completed from detail view: {self.detail_task['title']}")
                    self.showing_details = False
                    self.detail_task = None
                    self.current_screen = "notification"
                return True
            
            if hasattr(self, 'detail_skip_rect') and self.detail_skip_rect.collidepoint(pos):
                if self.detail_task:
                    self.detail_task['skipped'] = True
                    self.skipped_tasks.append({
                        'title': self.detail_task['title'],
                        'time': self.detail_task.get('time', 'Unknown'),
                        'skipped_at': self.current_time.strftime("%H:%M:%S"),
                        'was_catch_up': True
                    })
                    print(f"⏭️ Task skipped from detail view: {self.detail_task['title']}")
                    self.showing_details = False
                    self.detail_task = None
                    self.current_screen = "notification"
                return True
        
        elif self.current_screen == "notification":
            # Handle notification screen clicks
            if hasattr(self, 'notification_back_button_rect') and self.notification_back_button_rect.collidepoint(pos):
                self.current_screen = "idle"
                self.current_task = None
                self.catch_up_page = 0  # Reset page when returning to main
                print("🔙 Returning to main screen")
                return True
            
            # Check for page navigation buttons
            if hasattr(self, 'prev_page_rect') and self.prev_page_rect and self.prev_page_rect.collidepoint(pos):
                self.catch_up_page -= 1
                print(f"🔙 Previous page: {self.catch_up_page + 1}")
                return True
            
            if hasattr(self, 'next_page_rect') and self.next_page_rect and self.next_page_rect.collidepoint(pos):
                self.catch_up_page += 1
                print(f"➡️ Next page: {self.catch_up_page + 1}")
                return True
            
            # Check for individual catch-up task clicks
            if self.current_task.get('is_catch_up', False) and hasattr(self, 'view_details_rects') and hasattr(self, 'catch_up_task_rects'):
                print(f"🔍 DEBUG: Catch-up task detected, checking {len(self.view_details_rects)} view details buttons")
                # Check View Details button first (using separate storage)
                for view_rect, task in self.view_details_rects:
                    print(f"🔍 DEBUG: Checking click {pos} against View Details rect {view_rect} for task {task.get('title', 'Unknown')}")
                    # Check if click is within the View Details button area
                    if (view_rect.left <= pos[0] <= view_rect.right and 
                        view_rect.top <= pos[1] <= view_rect.bottom):
                        print(f"🔍 DEBUG: View Details clicked for task: {task['title']} at {pos}")
                        self.detail_task = task
                        self.showing_details = True
                        self.current_screen = "detail"
                        print(f"📋 Viewing details for: {task['title']}")
                        return True
                
                # Check clicking on the task itself (for quick toggle)
                for task_rect, task in self.catch_up_task_rects:
                    if task_rect.collidepoint(pos):
                        if not task.get('completed', False) and not task.get('skipped', False):
                            # First click: mark as completed
                            task['completed'] = True
                            self.completed_tasks.append({
                                'title': task['title'],
                                'time': task.get('time', 'Unknown'),
                                'completed_at': self.current_time.strftime("%H:%M:%S"),
                                'was_catch_up': True
                            })
                            
                            # PHASE 4: Track completed tasks for encouragement
                            self.completed_tasks_count += 1
                            self.offer_encouragement()
                            
                            print(f"✅ Individual task completed (click): {task['title']}")
                        elif task.get('completed', False):
                            # Second click: mark as skipped
                            task['completed'] = False
                            task['skipped'] = True
                            self.skipped_tasks.append({
                                'title': task['title'],
                                'time': task.get('time', 'Unknown'),
                                'skipped_at': self.current_time.strftime("%H:%M:%S"),
                                'was_catch_up': True
                            })
                            print(f"⏭️ Individual task skipped (click): {task['title']}")
                        else:
                            # Third click: back to pending
                            task['skipped'] = False
                            print(f"⏳ Individual task reset (click): {task['title']}")
                        return True
                
                # Check bulk action buttons
                if hasattr(self, 'all_complete_button_rect') and self.all_complete_button_rect.collidepoint(pos):
                    # Mark ALL tasks on current page as completed (regardless of current status)
                    catch_up_tasks = self.get_catch_up_tasks()
                    total_tasks = len(catch_up_tasks)
                    start_index = self.catch_up_page * self.tasks_per_page
                    end_index = min(start_index + self.tasks_per_page, total_tasks)
                    current_page_tasks = catch_up_tasks[start_index:end_index]
                    
                    completed_count = 0
                    for task in current_page_tasks:
                        # Mark as completed regardless of current status
                        if not task.get('completed', False):
                            task['completed'] = True
                            task['skipped'] = False  # Clear skip status
                            completed_count += 1
                            self.completed_tasks.append({
                                'title': task['title'],
                                'time': task.get('time', 'Unknown'),
                                'completed_at': self.current_time.strftime("%H:%M:%S"),
                                'was_catch_up': True
                            })
                    
                    # PHASE 4: Track completed tasks for encouragement
                    self.completed_tasks_count += completed_count
                    self.offer_encouragement()
                    
                    print(f"✅ ALL COMPLETE: Marked {completed_count} tasks as completed on page {self.catch_up_page + 1}")
                    
                    # Move to next page or complete all
                    self._handle_page_navigation_after_bulk_action(catch_up_tasks, total_tasks)
                    return True
                
                elif hasattr(self, 'done_marked_button_rect') and self.done_marked_button_rect.collidepoint(pos):
                    # Complete only tasks that are already marked as complete/skip, warn if missed
                    catch_up_tasks = self.get_catch_up_tasks()
                    total_tasks = len(catch_up_tasks)
                    start_index = self.catch_up_page * self.tasks_per_page
                    end_index = min(start_index + self.tasks_per_page, total_tasks)
                    current_page_tasks = catch_up_tasks[start_index:end_index]
                    
                    # Count marked vs unmarked tasks
                    marked_tasks = [task for task in current_page_tasks 
                                  if task.get('completed', False) or task.get('skipped', False)]
                    unmarked_tasks = [task for task in current_page_tasks 
                                    if not task.get('completed', False) and not task.get('skipped', False)]
                    
                    if unmarked_tasks:
                        # Warn about unmarked tasks
                        unmarked_names = [task['title'] for task in unmarked_tasks]
                        warning_title = "⚠️ MISSED TASKS!"
                        warning_message = f"You forgot to mark {len(unmarked_tasks)} tasks!\n\nUnmarked: {', '.join(unmarked_names)}\n\nPlease mark them as complete/skip before using DONE MARKED"
                        self.show_warning_popup(warning_title, warning_message)
                        return True
                    
                    # All tasks are marked, proceed with completion
                    completed_count = 0
                    skipped_count = 0
                    for task in current_page_tasks:
                        if task.get('completed', False):
                            completed_count += 1
                        elif task.get('skipped', False):
                            skipped_count += 1
                    
                    print(f"✅ DONE MARKED: {completed_count} completed, {skipped_count} skipped on page {self.catch_up_page + 1}")
                    
                    # Move to next page or complete all
                    self._handle_page_navigation_after_bulk_action(catch_up_tasks, total_tasks)
                    return True
                
                elif hasattr(self, 'all_skip_button_rect') and self.all_skip_button_rect.collidepoint(pos):
                    # Mark ALL tasks on current page as skipped (regardless of current status)
                    catch_up_tasks = self.get_catch_up_tasks()
                    total_tasks = len(catch_up_tasks)
                    start_index = self.catch_up_page * self.tasks_per_page
                    end_index = min(start_index + self.tasks_per_page, total_tasks)
                    current_page_tasks = catch_up_tasks[start_index:end_index]
                    
                    skipped_count = 0
                    for task in current_page_tasks:
                        # Mark as skipped regardless of current status
                        if not task.get('skipped', False):
                            task['skipped'] = True
                            task['completed'] = False  # Clear complete status
                            skipped_count += 1
                            self.skipped_tasks.append({
                                'title': task['title'],
                                'time': task.get('time', 'Unknown'),
                                'skipped_at': self.current_time.strftime("%H:%M:%S"),
                                'was_catch_up': True
                            })
                    
                    print(f"⏭️ ALL SKIP: Marked {skipped_count} tasks as skipped on page {self.catch_up_page + 1}")
                    
                    # Move to next page or complete all
                    self._handle_page_navigation_after_bulk_action(catch_up_tasks, total_tasks)
                    return True
            
            # Check main buttons (for non-catch-up tasks)
            if hasattr(self, 'done_button_rect') and self.done_button_rect.collidepoint(pos):
                print(f"✅ Task completed: {self.current_task['title']}")
                
                # Check if this is a catch-up task
                is_catch_up = self.current_task.get('is_catch_up', False)
                
                if is_catch_up:
                    # Update the task in the persistent catch-up tasks list
                    catch_up_tasks = self.get_catch_up_tasks()
                    for task in catch_up_tasks:
                        if task['title'] == self.current_task['title']:
                            task['completed'] = True
                            task['skipped'] = False
                            print(f"🔍 DEBUG: Updated catch-up task '{task['title']}' as completed")
                            break
                
                self.current_task['completed'] = True
                self.completed_tasks.append({
                    'title': self.current_task['title'],
                    'time': self.current_task.get('time', 'Unknown'),
                    'completed_at': self.current_time.strftime("%H:%M:%S"),
                    'was_catch_up': is_catch_up
                })
                
                # PHASE 4: Track completed tasks for encouragement
                self.completed_tasks_count += 1
                self.offer_encouragement()
                
                self.current_screen = "idle"
                self.current_task = None
                return True
            
            elif hasattr(self, 'skip_button_rect') and self.skip_button_rect.collidepoint(pos):
                print(f"⏭️ Task skipped: {self.current_task['title']}")
                
                # Check if this is a catch-up task
                is_catch_up = self.current_task.get('is_catch_up', False)
                
                if is_catch_up:
                    # Update the task in the persistent catch-up tasks list
                    catch_up_tasks = self.get_catch_up_tasks()
                    for task in catch_up_tasks:
                        if task['title'] == self.current_task['title']:
                            task['skipped'] = True
                            task['completed'] = False
                            print(f"🔍 DEBUG: Updated catch-up task '{task['title']}' as skipped")
                            break
                
                self.current_task['skipped'] = True
                self.skipped_tasks.append({
                    'title': self.current_task['title'],
                    'time': self.current_task.get('time', 'Unknown'),
                    'skipped_at': self.current_time.strftime("%H:%M:%S"),
                    'was_catch_up': is_catch_up
                })
                
                self.current_screen = "idle"
                self.current_task = None
                return True
        
        elif self.current_screen == "idle":
            # Handle idle screen clicks
            if hasattr(self, 'skipped_button_rect') and self.skipped_button_rect.collidepoint(pos):
                self.current_screen = "skipped_tasks"
                print("📋 Opening skipped tasks screen")
                return True
            
            if hasattr(self, 'analytics_button_rect') and self.analytics_button_rect.collidepoint(pos):
                self.current_screen = "analytics"
                print("📊 Opening analytics screen")
                return True
            
            if hasattr(self, 'backlog_button_rect') and self.backlog_button_rect.collidepoint(pos):
                self.current_screen = "backlog"
                print("📋 Opening backlog screen")
                return True
            
            if hasattr(self, 'voice_button_rect') and self.voice_button_rect.collidepoint(pos):
                self.current_screen = "voice_settings"
                print("🎤 Opening voice settings screen")
                return True
        
        elif self.current_screen == "skipped_tasks":
            # Handle skipped tasks screen clicks
            if hasattr(self, 'skipped_back_button_rect') and self.skipped_back_button_rect.collidepoint(pos):
                self.current_screen = "idle"
                self.current_task = None
                self.catch_up_page = 0 # Reset page when returning to main
                print("🔙 Returning to main screen")
                return True
            
            # Handle individual skipped task completion
            if hasattr(self, 'skipped_task_buttons'):
                for button_rect, task in self.skipped_task_buttons:
                    if button_rect.collidepoint(pos):
                        # Mark as completed and clear skipped status
                        task['completed'] = True
                        task['skipped'] = False  # Clear the skipped status
                        self.completed_tasks.append({
                            'title': task['title'],
                            'time': task.get('time', 'Unknown'),
                            'completed_at': self.current_time.strftime("%H:%M:%S"),
                            'was_catch_up': True
                        })
                        
                        # PHASE 4: Track completed tasks for encouragement
                        self.completed_tasks_count += 1
                        self.offer_encouragement()
                        
                        print(f"✅ Individual skipped task completed: {task['title']}")
                        # Re-render the screen to update the list
                        self.current_screen = "skipped_tasks"
                        return True
        
        elif self.current_screen == "analytics":
            # Handle analytics screen clicks
            if hasattr(self, 'analytics_back_button_rect') and self.analytics_back_button_rect.collidepoint(pos):
                self.current_screen = "idle"
        
        elif self.current_screen == "mood_prompt":
            # Handle mood prompt screen clicks
            if hasattr(self, 'save_mood_button_rect') and self.save_mood_button_rect.collidepoint(pos):
                if self.current_mood:
                    self.save_mood_data(self.current_mood, self.mood_notes)
                    self.show_mood_prompt = False
                    self.current_mood = None
                    self.mood_notes = ""
                    self.current_screen = "idle"
                    print("📝 Mood saved successfully")
                return True
            
            elif hasattr(self, 'skip_mood_button_rect') and self.skip_mood_button_rect.collidepoint(pos):
                self.show_mood_prompt = False
                self.current_mood = None
                self.mood_notes = ""
                self.current_screen = "idle"
                print("⏭️ Mood tracking skipped")
                return True
            
            # Handle mood button clicks
            if hasattr(self, 'mood_buttons'):
                for button_rect, mood_label in self.mood_buttons:
                    if button_rect.collidepoint(pos):
                        self.current_mood = mood_label
                        print(f"😊 Mood selected: {mood_label}")
                        return True
            
            # Handle notes box click
            if hasattr(self, 'notes_box_rect') and self.notes_box_rect.collidepoint(pos):
                # Focus on notes input (this will be handled by keyboard events)
                print("📝 Notes box clicked - ready for input")
                return True
                print("🔙 Returning to main screen from analytics")
                return True
        
        elif self.current_screen == "backlog":
            # Handle backlog screen clicks
            if hasattr(self, 'backlog_back_button_rect') and self.backlog_back_button_rect.collidepoint(pos):
                self.current_screen = "idle"
                print("🔙 Returning to main screen from backlog")
                return True
            
            # Handle backlog task redeem buttons
            if hasattr(self, 'backlog_task_buttons'):
                for button_info in self.backlog_task_buttons:
                    if button_info['redeem_button'].collidepoint(pos):
                        task = button_info['task']
                        task_id = task.get('task_id')
                        if task_id and self.backlog_manager:
                            success = self.backlog_manager.redeem_task(task_id)
                            if success:
                                self.show_warning_popup("Task Redeemed", f"'{task.get('task_title')}' marked as completed!")
                                print(f"🔍 DEBUG: Redeemed task: {task.get('task_title')}")
                            else:
                                self.show_warning_popup("Error", "Failed to redeem task")
                        return True
        
        elif self.current_screen == "voice_settings":
            # Handle voice settings screen clicks
            if hasattr(self, 'voice_back_button_rect') and self.voice_back_button_rect.collidepoint(pos):
                self.current_screen = "idle"
                print("🔙 Returning to main screen from voice settings")
                return True
            
            if hasattr(self, 'voice_test_button_rect') and self.voice_test_button_rect.collidepoint(pos):
                # Test the current voice
                test_message = f"Hello! This is {self.voice_id} speaking. How does this voice sound to you?"
                self.speak_message(test_message)
                print(f"🎤 Testing voice: {self.voice_id}")
                return True
            
            # Handle voice option clicks
            if hasattr(self, 'voice_option_rects'):
                for button_rect, voice_id in self.voice_option_rects:
                    if button_rect.collidepoint(pos):
                        if self.change_voice(voice_id):
                            print(f"🎤 Voice changed to: {voice_id}")
                            # Test the new voice
                            test_message = f"Voice changed to {voice_id}. How does this sound?"
                            self.speak_message(test_message)
                        return True
        
        elif self.current_screen == "catch_up":
            # Handle catch-up screen
            if hasattr(self, 'catch_up_back_rect') and self.catch_up_back_rect.collidepoint(mouse_pos):
                self.current_view = "idle"
            elif hasattr(self, 'catch_up_page_rects'):
                for i, rect in enumerate(self.catch_up_page_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0:  # Previous page
                            self.catch_up_page = max(0, self.catch_up_page - 1)
                        else:  # Next page
                            catch_up_task = self.get_next_task()
                            if catch_up_task and catch_up_task.get('is_catch_up'):
                                missed_tasks = catch_up_task.get('missed_tasks', [])
                                total_pages = (len(missed_tasks) + 4 - 1) // 4
                                self.catch_up_page = min(self.catch_up_page + 1, total_pages - 1)
                        break
            elif hasattr(self, 'catch_up_bulk_rects'):
                for i, rect in enumerate(self.catch_up_bulk_rects):
                    if rect.collidepoint(mouse_pos):
                        self.handle_bulk_action(i)
                        break
            elif hasattr(self, 'catch_up_detail_rects'):
                # Handle View Details button clicks
                for i, rect in enumerate(self.catch_up_detail_rects):
                    if rect.collidepoint(mouse_pos):
                        catch_up_task = self.get_next_task()
                        if catch_up_task and catch_up_task.get('is_catch_up'):
                            missed_tasks = catch_up_task.get('missed_tasks', [])
                            tasks_per_page = 4
                            start_idx = self.catch_up_page * tasks_per_page
                            task_index = start_idx + i
                            
                            if task_index < len(missed_tasks):
                                task = missed_tasks[task_index]
                                # Show task details popup
                                self.show_popup = True
                                self.popup_title = f"Task Details: {task['title']}"
                                self.popup_message = f"Original Time: {task['original_time']}\n\n{task['notes']}"
                                self.popup_type = "info"
                        break
            elif hasattr(self, 'catch_up_task_rects'):
                # Handle individual task clicks (toggle status)
                for i, rect in enumerate(self.catch_up_task_rects):
                    if rect.collidepoint(mouse_pos):
                        # Get the persistent catch-up tasks list
                        catch_up_tasks = self.get_catch_up_tasks()
                        tasks_per_page = 4
                        start_idx = self.catch_up_page * tasks_per_page
                        task_index = start_idx + i
                        
                        if task_index < len(catch_up_tasks):
                            task = catch_up_tasks[task_index]
                            print(f"🔍 DEBUG: Clicked on catch-up task: {task['title']} (completed: {task.get('completed', False)}, skipped: {task.get('skipped', False)})")
                            # Toggle completion status
                            if task.get('completed', False):
                                task['completed'] = False
                                task['skipped'] = True
                                print(f"🔍 DEBUG: Marked as skipped: {task['title']}")
                            elif task.get('skipped', False):
                                task['skipped'] = False
                                print(f"🔍 DEBUG: Reset to pending: {task['title']}")
                            else:
                                task['completed'] = True
                                print(f"🔍 DEBUG: Marked as completed: {task['title']}")
                            
                            if self.voice_engine:
                                if task.get('completed', False):
                                    self.speak_message(f"Marked {task['title']} as completed")
                                elif task.get('skipped', False):
                                    self.speak_message(f"Marked {task['title']} as skipped")
                                else:
                                    self.speak_message(f"Unmarked {task['title']}")
                        break
        
        elif self.current_screen == "skipped_tasks":
            # Handle skipped tasks screen
            if hasattr(self, 'skipped_back_rect') and self.skipped_back_rect.collidepoint(mouse_pos):
                self.current_view = "idle"
            elif hasattr(self, 'skipped_complete_rects'):
                # Handle Complete button clicks for skipped tasks
                for i, rect in enumerate(self.skipped_complete_rects):
                    if rect.collidepoint(mouse_pos):
                        skipped_tasks = self.backlog_manager.get_backlog_tasks()
                        tasks_per_page = 6
                        start_idx = self.backlog_page * tasks_per_page
                        task_index = start_idx + i
                        
                        if task_index < len(skipped_tasks):
                            task = skipped_tasks[task_index]
                            # Mark as completed in backlog
                            self.backlog_manager.complete_backlog_task(task['id'])
                            if self.voice_engine:
                                self.speak_message(f"Redeemed skipped task: {task.get('task_title', 'Unknown')}")
                        break
        
        return False
    
    def _handle_page_navigation_after_bulk_action(self, catch_up_tasks, total_tasks):
        """Handle navigation after bulk actions (complete/skip all)."""
        total_pages = (total_tasks + self.tasks_per_page - 1) // self.tasks_per_page
        
        # Check if there are more pages with incomplete tasks
        remaining_incomplete = sum(1 for task in catch_up_tasks 
                                if not task.get('completed', False) and not task.get('skipped', False))
        
        if remaining_incomplete > 0:
            # Find next page with incomplete tasks
            next_page = self.catch_up_page + 1
            found_page = False
            while next_page < total_pages:
                page_start = next_page * self.tasks_per_page
                page_end = min(page_start + self.tasks_per_page, total_tasks)
                page_tasks = catch_up_tasks[page_start:page_end]
                incomplete_on_page = sum(1 for task in page_tasks 
                                       if not task.get('completed', False) and not task.get('skipped', False))
                
                if incomplete_on_page > 0:
                    self.catch_up_page = next_page
                    print(f"➡️ Moving to page {self.catch_up_page + 1} ({incomplete_on_page} tasks remaining on this page)")
                    found_page = True
                    break
                next_page += 1
            
            if not found_page:
                # No more pages with incomplete tasks, but some tasks still pending
                # Go back to first page with incomplete tasks
                for page in range(total_pages):
                    page_start = page * self.tasks_per_page
                    page_end = min(page_start + self.tasks_per_page, total_tasks)
                    page_tasks = catch_up_tasks[page_start:page_end]
                    incomplete_on_page = sum(1 for task in page_tasks 
                                           if not task.get('completed', False) and not task.get('skipped', False))
                    
                    if incomplete_on_page > 0:
                        self.catch_up_page = page
                        print(f"🔄 Returning to page {self.catch_up_page + 1} ({incomplete_on_page} tasks still pending)")
                        break
        else:
            # All catch-up tasks completed, move to next regular task
            print(f"🎉 All catch-up tasks completed! Moving to next task...")
            self.current_screen = "idle"
            self.current_task = None
            self.catch_up_page = 0
    
    def simulate_task_notification(self):
        """Simulate a task notification appearing."""
        next_task = self.get_next_task()
        if next_task:
            # For catch-up tasks, they're always available
            if next_task.get('is_catch_up', False):
                self.current_task = next_task
                self.current_screen = "notification"
                self.catch_up_page = 0  # Reset to first page for new catch-up
                print(f"🚨 Catch-up notification: {next_task['title']}")
                return True
            # For regular tasks, check if not completed/skipped
            elif not next_task.get('completed', False) and not next_task.get('skipped', False):
                self.current_task = next_task
                self.current_screen = "notification"
                
                # PHASE 4: Announce next task using voice
                self.announce_next_task(next_task)
                
                # Start timer for the task
                if self.task_timer and next_task.get('duration', 0) > 0:
                    duration = next_task.get('duration', 15)  # Default 15 minutes
                    self.task_timer.start_timer(
                        next_task, 
                        duration,
                        callback=self._on_task_timer_complete
                    )
                    print(f"⏰ Started timer for '{next_task.get('title')}' - {duration} minutes")
                
                print(f"🔔 Task notification: {next_task['title']}")
                return True
        else:
            print(f"🔍 DEBUG: No next task found. Current time: {self.current_time.strftime('%H:%M')}")
            print(f"🔍 DEBUG: Available tasks: {len([t for t in self.today_tasks if not t.get('completed', False) and not t.get('skipped', False)])}")
        return False
    
    def run(self):
        """Main simulation loop."""
        running = True
        
        while running:
            # Update current time
            self.current_time = datetime.now()
            
            # Check for distraction
            self.check_distraction()
            
            # Check for Pomodoro completion
            if self.focus_mode:
                self.check_pomodoro_completion()
            
            # Check for emoji badges
            self.check_emoji_badges()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.show_popup:
                            self.show_popup = False
                        elif self.current_view == "idle":
                            # Show exit confirmation on main screen
                            self.show_popup = True
                            self.popup_title = "Exit Confirmation"
                            
                            # Check for unsaved progress
                            completed_tasks = len([t for t in self.today_tasks if t.get('completed', False)])
                            total_tasks = len(self.today_tasks)
                            unsaved_progress = completed_tasks > 0
                            
                            if unsaved_progress:
                                self.popup_message = f"You have {completed_tasks}/{total_tasks} completed tasks.\nUnsaved progress will be lost.\n\nAre you sure you want to exit? (Press Enter to confirm)"
                            else:
                                self.popup_message = "Are you sure you want to exit? (Press Enter to confirm)"
                            
                            self.popup_type = "exit_confirmation"
                            self.exit_confirmation_active = True
                        else:
                            # Exit from any other screen back to idle
                            self.current_view = "idle"
                    
                    elif event.key == pygame.K_RETURN:
                        # Handle Enter key for exit confirmation
                        if self.show_popup and self.popup_type == "exit_confirmation":
                            self.show_popup = False
                            running = False
                            continue
                    
                    elif event.key == pygame.K_t:
                        self.toggle_theme()
                    
                    elif event.key == pygame.K_SPACE:
                        self.update_interaction_time()
                        if self.current_view == "idle":
                            next_task = self.get_next_task()
                            if next_task:
                                self.current_task = next_task
                                self.current_view = "task"
                                self.announce_next_task(next_task)
                    
                    elif event.key == pygame.K_v:
                        self.update_interaction_time()
                        if self.current_view == "idle":
                            self.current_view = "voice_settings"
                    
                    elif event.key == pygame.K_s:
                        self.update_interaction_time()
                        if self.current_view == "idle":
                            self.current_view = "stats"
                    
                    # Phase 6: Add Task keyboard input handling
                    elif self.current_view == "add_task" and self.active_input_field:
                        if event.key == pygame.K_RETURN:
                            # Move to next field or submit
                            if self.active_input_field == "title":
                                self.active_input_field = "date"
                            elif self.active_input_field == "date":
                                self.active_input_field = "time"
                            elif self.active_input_field == "time":
                                self.active_input_field = "notes"
                            elif self.active_input_field == "notes":
                                # Submit the task
                                if self.new_task_title and self.new_task_time and self.new_task_date:
                                    # Create new task
                                    new_task = {
                                        'title': self.new_task_title,
                                        'time': self.new_task_time,
                                        'date': self.new_task_date,
                                        'notes': self.new_task_notes,
                                        'priority': 2,
                                        'audio_alert': True,
                                        'snooze_duration': 5,
                                        'duration': 30,
                                        'completed': False,
                                        'skipped': False
                                    }
                                    
                                    # Add to today's tasks
                                    self.today_tasks.append(new_task)
                                    
                                    # Sort tasks by time
                                    self.today_tasks.sort(key=lambda x: x.get('time', '23:59'))
                                    
                                    print(f"✅ Added new task: {self.new_task_title} at {self.new_task_time} on {self.new_task_date}")
                                    
                                    # Clear form and return to idle
                                    self.new_task_title = ""
                                    self.new_task_time = ""
                                    self.new_task_date = datetime.now().strftime("%Y-%m-%d")
                                    self.new_task_notes = ""
                                    self.active_input_field = None
                                    self.current_view = "idle"
                                else:
                                    # Show error popup
                                    self.show_popup = True
                                    self.popup_title = "Missing Information"
                                    self.popup_message = "Please enter task title, time, and date."
                                    self.popup_type = "info"
                        
                        elif event.key == pygame.K_TAB:
                            # Move to next field
                            if self.active_input_field == "title":
                                self.active_input_field = "date"
                            elif self.active_input_field == "date":
                                self.active_input_field = "time"
                            elif self.active_input_field == "time":
                                self.active_input_field = "notes"
                            elif self.active_input_field == "notes":
                                self.active_input_field = "title"
                        
                        elif event.key == pygame.K_BACKSPACE:
                            # Handle backspace
                            if self.active_input_field == "title":
                                self.new_task_title = self.new_task_title[:-1] if self.new_task_title else ""
                            elif self.active_input_field == "date":
                                # Date is handled by calendar picker, no backspace needed
                                pass
                            elif self.active_input_field == "time":
                                self.new_task_time = self.new_task_time[:-1] if self.new_task_time else ""
                            elif self.active_input_field == "notes":
                                self.new_task_notes = self.new_task_notes[:-1] if self.new_task_notes else ""
                        
                        elif event.unicode.isprintable():
                            # Handle printable characters
                            if self.active_input_field == "title":
                                if len(self.new_task_title) < 50:  # Limit title length
                                    self.new_task_title += event.unicode
                            elif self.active_input_field == "date":
                                # Date is handled by calendar picker, no direct typing
                                pass
                            elif self.active_input_field == "time":
                                if len(self.new_task_time) < 5:  # Limit time length (HH:MM)
                                    self.new_task_time += event.unicode
                            elif self.active_input_field == "notes":
                                if len(self.new_task_notes) < 200:  # Limit notes length
                                    self.new_task_notes += event.unicode
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.update_interaction_time()
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Handle popup clicks first
                    if self.show_popup:
                        if self.popup_type == "exit_confirmation":
                            # Handle exit confirmation buttons
                            if hasattr(self, 'popup_yes_rect') and self.popup_yes_rect.collidepoint(mouse_pos):
                                # User confirmed exit
                                self.show_popup = False
                                running = False
                                continue
                            elif hasattr(self, 'popup_no_rect') and self.popup_no_rect.collidepoint(mouse_pos):
                                # User cancelled exit
                                self.show_popup = False
                                continue
                        elif hasattr(self, 'popup_close_rect') and self.popup_close_rect.collidepoint(mouse_pos):
                            self.show_popup = False
                            continue
                        continue  # Block other clicks when popup is shown
                    
                    # Handle different screens
                    if self.current_view == "idle":
                        # Get button rectangles from idle screen
                        start_rect, backlog_rect, skipped_rect, stats_rect, voice_rect, focus_rect, all_tasks_rect, achievements_rect, add_task_rect = self.draw_idle_screen()
                        
                        if start_rect.collidepoint(mouse_pos):
                            next_task = self.get_next_task()
                            if next_task:
                                self.current_task = next_task
                                self.current_view = "task"
                                self.announce_next_task(next_task)
                                
                                # Start timer for the task automatically
                                if self.task_timer and next_task.get('duration', 0) > 0:
                                    duration = next_task.get('duration', 15)  # Default 15 minutes
                                    self.task_timer.start_timer(
                                        next_task, 
                                        duration,
                                        callback=self._on_task_timer_complete
                                    )
                                    print(f"⏰ Started timer for '{next_task.get('title')}' - {duration} minutes")
                        
                        elif backlog_rect.collidepoint(mouse_pos):
                            self.current_view = "backlog"
                        
                        elif skipped_rect.collidepoint(mouse_pos):
                            self.current_view = "skipped_tasks"
                        
                        elif stats_rect.collidepoint(mouse_pos):
                            self.current_view = "stats"
                        
                        elif voice_rect.collidepoint(mouse_pos):
                            self.current_view = "voice_settings"
                        
                        elif focus_rect.collidepoint(mouse_pos):
                            # Start focus mode with next task
                            next_task = self.get_next_task()
                            if next_task:
                                self.start_focus_mode(next_task)
                            else:
                                # Show popup if no tasks available
                                self.show_popup = True
                                self.popup_title = "No Tasks Available"
                                self.popup_message = "All tasks are completed or there are no tasks scheduled for today."
                                self.popup_type = "info"
                        
                        elif all_tasks_rect.collidepoint(mouse_pos):
                            # Initialize all tasks view
                            self.all_tasks_page = 0
                            self.current_view = "all_tasks"
                        
                        elif achievements_rect.collidepoint(mouse_pos):
                            self.current_view = "achievements"
                        
                        elif add_task_rect.collidepoint(mouse_pos):
                            # Initialize add task screen
                            self.new_task_title = ""
                            self.new_task_time = ""
                            self.new_task_notes = ""
                            self.active_input_field = None
                            self.current_view = "add_task"
                            print("➕ Opening add task screen")
                    
                    elif self.current_view == "focus":
                        # Get button rectangles from focus screen
                        pause_rect, end_rect = self.draw_focus_mode_screen()
                        
                        if pause_rect.collidepoint(mouse_pos):
                            if self.pomodoro_paused:
                                self.resume_focus_mode()
                            else:
                                self.pause_focus_mode()
                        
                        elif end_rect.collidepoint(mouse_pos):
                            self.end_focus_mode()
                    
                    elif self.current_view == "distraction":
                        # Get button rectangle from distraction screen
                        dismiss_rect = self.draw_distraction_alert_screen()
                        
                        if dismiss_rect.collidepoint(mouse_pos):
                            self.dismiss_distraction_warning()
                    
                    elif self.current_view == "achievements":
                        # Get button rectangle from achievements screen
                        back_rect = self.draw_badges_screen()
                        
                        if back_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                    
                    elif self.current_view == "add_task":
                        # Get button rectangles from add task screen
                        add_rect, cancel_rect = self.draw_add_task_screen()
                        
                        if add_rect.collidepoint(mouse_pos):
                            # Add the new task
                            if self.new_task_title and self.new_task_time and self.new_task_date:
                                # Create new task
                                new_task = {
                                    'title': self.new_task_title,
                                    'time': self.new_task_time,
                                    'date': self.new_task_date,
                                    'notes': self.new_task_notes,
                                    'priority': 2,  # Default medium priority
                                    'audio_alert': True,
                                    'snooze_duration': 5,
                                    'duration': 30,  # Default 30 minutes
                                    'completed': False,
                                    'skipped': False
                                }
                                
                                # Add to today's tasks
                                self.today_tasks.append(new_task)
                                
                                # Sort tasks by time
                                self.today_tasks.sort(key=lambda x: x.get('time', '23:59'))
                                
                                print(f"✅ Added new task: {self.new_task_title} at {self.new_task_time} on {self.new_task_date}")
                                
                                # Clear form and return to idle
                                self.new_task_title = ""
                                self.new_task_time = ""
                                self.new_task_date = datetime.now().strftime("%Y-%m-%d")
                                self.new_task_notes = ""
                                self.active_input_field = None
                                self.current_view = "idle"
                            else:
                                # Show error popup
                                self.show_popup = True
                                self.popup_title = "Missing Information"
                                self.popup_message = "Please enter task title, time, and date."
                                self.popup_type = "info"
                        
                        elif cancel_rect.collidepoint(mouse_pos):
                            # Cancel and return to idle
                            self.new_task_title = ""
                            self.new_task_time = ""
                            self.new_task_date = datetime.now().strftime("%Y-%m-%d")
                            self.new_task_notes = ""
                            self.active_input_field = None
                            self.current_view = "idle"
                            print("❌ Cancelled adding task")
                        
                        # Handle input field clicks
                        elif hasattr(self, 'title_input_rect') and self.title_input_rect.collidepoint(mouse_pos):
                            self.active_input_field = "title"
                            print("📝 Focus on title input")
                        
                        elif hasattr(self, 'date_input_rect') and self.date_input_rect.collidepoint(mouse_pos):
                            # Open calendar picker
                            self.show_calendar = True
                            self.active_input_field = "date"
                            print("📅 Opening calendar picker")
                        
                        elif hasattr(self, 'time_input_rect') and self.time_input_rect.collidepoint(mouse_pos):
                            # Open time picker
                            self.show_time_picker = True
                            self.active_input_field = "time"
                            # Initialize time picker with current time
                            current_time = datetime.now()
                            self.time_picker_hour = current_time.hour
                            self.time_picker_minute = current_time.minute
                            if self.time_picker_hour > 12:
                                self.time_picker_hour -= 12
                                self.time_picker_am_pm = "PM"
                            else:
                                self.time_picker_am_pm = "AM"
                            if self.time_picker_hour == 0:
                                self.time_picker_hour = 12
                            print("⏰ Opening time picker")
                        
                        elif hasattr(self, 'notes_input_rect') and self.notes_input_rect.collidepoint(mouse_pos):
                            self.active_input_field = "notes"
                            print("📝 Focus on notes input")
                    
                    # Handle time picker clicks
                    elif self.show_time_picker:
                        if hasattr(self, 'time_picker_rects'):
                            if self.time_picker_rects['hour_up'].collidepoint(mouse_pos):
                                self.time_picker_hour = (self.time_picker_hour % 12) + 1
                                if self.time_picker_hour == 13:
                                    self.time_picker_hour = 1
                                print(f"⏰ Hour up: {self.time_picker_hour}")
                            
                            elif self.time_picker_rects['hour_down'].collidepoint(mouse_pos):
                                self.time_picker_hour = (self.time_picker_hour - 2) % 12 + 1
                                print(f"⏰ Hour down: {self.time_picker_hour}")
                            
                            elif self.time_picker_rects['minute_up'].collidepoint(mouse_pos):
                                self.time_picker_minute = (self.time_picker_minute + 5) % 60
                                print(f"⏰ Minute up: {self.time_picker_minute}")
                            
                            elif self.time_picker_rects['minute_down'].collidepoint(mouse_pos):
                                self.time_picker_minute = (self.time_picker_minute - 5) % 60
                                print(f"⏰ Minute down: {self.time_picker_minute}")
                            
                            elif self.time_picker_rects['ampm'].collidepoint(mouse_pos):
                                self.time_picker_am_pm = "PM" if self.time_picker_am_pm == "AM" else "AM"
                                print(f"⏰ AM/PM toggle: {self.time_picker_am_pm}")
                            
                            elif self.time_picker_rects['ok'].collidepoint(mouse_pos):
                                # Convert to 24-hour format and set time
                                hour_24 = self.time_picker_hour
                                if self.time_picker_am_pm == "PM" and hour_24 != 12:
                                    hour_24 += 12
                                elif self.time_picker_am_pm == "AM" and hour_24 == 12:
                                    hour_24 = 0
                                
                                self.new_task_time = f"{hour_24:02d}:{self.time_picker_minute:02d}"
                                self.show_time_picker = False
                                self.active_input_field = None
                                print(f"✅ Time selected: {self.new_task_time}")
                            
                            elif self.time_picker_rects['cancel'].collidepoint(mouse_pos):
                                self.show_time_picker = False
                                self.active_input_field = None
                                print("❌ Time picker cancelled")
                    
                    # Handle calendar clicks
                    elif self.show_calendar:
                        if hasattr(self, 'calendar_rects'):
                            if self.calendar_rects['prev'].collidepoint(mouse_pos):
                                # Previous month
                                self.calendar_month -= 1
                                if self.calendar_month < 1:
                                    self.calendar_month = 12
                                    self.calendar_year -= 1
                                print(f"📅 Previous month: {self.calendar_month}/{self.calendar_year}")
                            
                            elif self.calendar_rects['next'].collidepoint(mouse_pos):
                                # Next month
                                self.calendar_month += 1
                                if self.calendar_month > 12:
                                    self.calendar_month = 1
                                    self.calendar_year += 1
                                print(f"📅 Next month: {self.calendar_month}/{self.calendar_year}")
                            
                            elif self.calendar_rects['ok'].collidepoint(mouse_pos):
                                # Set selected date
                                self.new_task_date = f"{self.calendar_year:04d}-{self.calendar_month:02d}-{self.calendar_selected_day:02d}"
                                self.show_calendar = False
                                self.active_input_field = None
                                print(f"✅ Date selected: {self.new_task_date}")
                            
                            elif self.calendar_rects['cancel'].collidepoint(mouse_pos):
                                self.show_calendar = False
                                self.active_input_field = None
                                print("❌ Calendar cancelled")
                            
                            else:
                                # Check for day clicks
                                for day, rect in self.calendar_rects['days'].items():
                                    if rect.collidepoint(mouse_pos):
                                        self.calendar_selected_day = day
                                        print(f"📅 Day selected: {day}")
                                        break
                    
                    elif self.current_view == "task":
                        # Handle task completion/skip
                        if hasattr(self, 'complete_rect') and self.complete_rect.collidepoint(mouse_pos):
                            self.complete_current_task()
                        elif hasattr(self, 'skip_rect') and self.skip_rect.collidepoint(mouse_pos):
                            self.skip_current_task()
                        elif hasattr(self, 'back_rect') and self.back_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                    
                    elif self.current_view == "stats":
                        # Handle stats screen back button
                        if hasattr(self, 'stats_back_rect') and self.stats_back_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                    
                    elif self.current_view == "voice_settings":
                        # Handle voice settings screen
                        if hasattr(self, 'voice_back_button_rect') and self.voice_back_button_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                        elif hasattr(self, 'voice_test_button_rect') and self.voice_test_button_rect.collidepoint(mouse_pos):
                            if self.voice_engine:
                                self.speak_message("Voice test successful!")
                    
                    elif self.current_view == "backlog":
                        # Handle backlog screen
                        if hasattr(self, 'backlog_back_rect') and self.backlog_back_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                        elif hasattr(self, 'backlog_page_rects'):
                            for i, rect in enumerate(self.backlog_page_rects):
                                if rect.collidepoint(mouse_pos):
                                    self.backlog_page = i
                                    break
                    
                    elif self.current_view == "catch_up":
                        # Handle catch-up screen
                        if hasattr(self, 'catch_up_back_rect') and self.catch_up_back_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                        elif hasattr(self, 'catch_up_page_rects'):
                            for i, rect in enumerate(self.catch_up_page_rects):
                                if rect.collidepoint(mouse_pos):
                                    if i == 0:  # Previous page
                                        self.catch_up_page = max(0, self.catch_up_page - 1)
                                    else:  # Next page
                                        catch_up_tasks = self.get_catch_up_tasks()
                                        total_pages = (len(catch_up_tasks) + 4 - 1) // 4
                                        self.catch_up_page = min(self.catch_up_page + 1, total_pages - 1)
                                    break
                        elif hasattr(self, 'catch_up_bulk_rects'):
                            for i, rect in enumerate(self.catch_up_bulk_rects):
                                if rect.collidepoint(mouse_pos):
                                    self.handle_bulk_action(i)
                                    break
                        elif hasattr(self, 'catch_up_detail_rects'):
                            # Handle View Details button clicks
                            for i, rect in enumerate(self.catch_up_detail_rects):
                                if rect.collidepoint(mouse_pos):
                                    catch_up_tasks = self.get_catch_up_tasks()
                                    tasks_per_page = 4
                                    start_idx = self.catch_up_page * tasks_per_page
                                    task_index = start_idx + i
                                    
                                    if task_index < len(catch_up_tasks):
                                        task = catch_up_tasks[task_index]
                                        # Show task details popup
                                        self.show_popup = True
                                        self.popup_title = f"Task Details: {task['title']}"
                                        self.popup_message = f"Original Time: {task['original_time']}\n\n{task['notes']}"
                                        self.popup_type = "info"
                                    break
                        elif hasattr(self, 'catch_up_task_rects'):
                            # Handle individual task clicks (toggle status)
                            for i, rect in enumerate(self.catch_up_task_rects):
                                if rect.collidepoint(mouse_pos):
                                    catch_up_tasks = self.get_catch_up_tasks()
                                    tasks_per_page = 4
                                    start_idx = self.catch_up_page * tasks_per_page
                                    task_index = start_idx + i
                                    
                                    if task_index < len(catch_up_tasks):
                                        task = catch_up_tasks[task_index]
                                        # Toggle completion status
                                        if task.get('completed', False):
                                            task['completed'] = False
                                            task['skipped'] = True
                                        elif task.get('skipped', False):
                                            task['skipped'] = False
                                        else:
                                            task['completed'] = True
                                        
                                        if self.voice_engine:
                                            if task.get('completed', False):
                                                self.speak_message(f"Marked {task['title']} as completed")
                                            elif task.get('skipped', False):
                                                self.speak_message(f"Marked {task['title']} as skipped")
                                            else:
                                                self.speak_message(f"Unmarked {task['title']}")
                                    break
                    
                    elif self.current_view == "skipped_tasks":
                        # Handle skipped tasks screen
                        if hasattr(self, 'skipped_back_rect') and self.skipped_back_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                        elif hasattr(self, 'skipped_complete_rects'):
                            # Handle Complete button clicks for skipped tasks
                            for i, rect in enumerate(self.skipped_complete_rects):
                                if rect.collidepoint(mouse_pos):
                                    skipped_tasks = self.backlog_manager.get_backlog_tasks()
                                    tasks_per_page = 6
                                    start_idx = self.backlog_page * tasks_per_page
                                    task_index = start_idx + i
                                    
                                    if task_index < len(skipped_tasks):
                                        task = skipped_tasks[task_index]
                                        # Mark as completed in backlog
                                        self.backlog_manager.complete_backlog_task(task['id'])
                                        if self.voice_engine:
                                            self.speak_message(f"Redeemed skipped task: {task.get('task_title', 'Unknown')}")
                        break
                    
                    elif self.current_view == "all_tasks":
                        # Handle all tasks screen
                        if hasattr(self, 'all_tasks_back_rect') and self.all_tasks_back_rect.collidepoint(mouse_pos):
                            self.current_view = "idle"
                        elif hasattr(self, 'all_tasks_prev_rect') and self.all_tasks_prev_rect.collidepoint(mouse_pos):
                            self.all_tasks_page = max(0, self.all_tasks_page - 1)
                        elif hasattr(self, 'all_tasks_next_rect') and self.all_tasks_next_rect.collidepoint(mouse_pos):
                            # Get all tasks to calculate total pages
                            all_tasks = []
                            for task in self.today_tasks:
                                task['is_regular'] = True
                                all_tasks.append(task)
                            catch_up_tasks = self.get_catch_up_tasks()
                            for task in catch_up_tasks:
                                task['is_catch_up'] = True
                                all_tasks.append(task)
                            total_pages = (len(all_tasks) + 4 - 1) // 4
                            self.all_tasks_page = min(self.all_tasks_page + 1, total_pages - 1)
                        # Handle button clicks (check all handlers)
                        clicked = False
                        
                        if hasattr(self, 'all_details_rects'):
                            # Handle View Details button clicks
                            for rect, task in self.all_details_rects:
                                if rect.collidepoint(mouse_pos):
                                    # Show task details in a popup
                                    details_title = f"Task Details: {task['title']}"
                                    details_message = f"Time: {self.format_time_for_display(task.get('time', 'Unknown'))}\n"
                                    details_message += f"Duration: {task.get('duration', 0)} minutes\n"
                                    details_message += f"Status: {task.get('completed', False) and 'Completed' or task.get('skipped', False) and 'Skipped' or 'Pending'}\n\n"
                                    details_message += f"Notes:\n{task.get('notes', 'No details available')}"
                                    self.show_warning_popup(details_title, details_message)
                                    clicked = True
                                    break
                        
                        if not clicked and hasattr(self, 'all_complete_rects'):
                            # Handle Complete button clicks
                            for rect, task in self.all_complete_rects:
                                if rect.collidepoint(mouse_pos):
                                    task['completed'] = True
                                    # Clear cached next task so it will be recalculated
                                    self.cached_next_task = None
                                    if self.voice_engine:
                                        self.speak_message(f"Completed {task['title']}!")
                                    clicked = True
                                    break
                        
                        if not clicked and hasattr(self, 'all_skip_rects'):
                            # Handle Skip button clicks
                            for rect, task in self.all_skip_rects:
                                if rect.collidepoint(mouse_pos):
                                    task['skipped'] = True
                                    # Clear cached next task so it will be recalculated
                                    self.cached_next_task = None
                                    if self.voice_engine:
                                        self.speak_message(f"Skipped {task['title']}!")
                                    break
        
            # Draw current screen
            if self.current_view == "idle":
                self.draw_idle_screen()
            elif self.current_view == "task":
                self.draw_task_screen()
            elif self.current_view == "focus":
                self.draw_focus_mode_screen()
            elif self.current_view == "distraction":
                self.draw_distraction_alert_screen()
            elif self.current_view == "achievements":
                self.draw_badges_screen()
            elif self.current_view == "stats":
                self.draw_stats_screen()
            elif self.current_view == "voice_settings":
                self.draw_voice_settings_screen()
            elif self.current_view == "backlog":
                self.draw_backlog_screen()
            elif self.current_view == "catch_up":
                self.draw_catch_up_screen()
            elif self.current_view == "skipped_tasks":
                self.draw_skipped_tasks_screen()
            elif self.current_view == "all_tasks":
                self.draw_all_tasks_screen()
            elif self.current_view == "add_task":
                self.draw_add_task_screen()
            
            # Draw time picker if active
            if self.show_time_picker:
                self.draw_time_picker()
            
            # Draw calendar if active
            if self.show_calendar:
                self.draw_calendar()
            
            # Draw popup if active
            if self.show_popup:
                self.draw_popup()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def _save_progress_on_exit(self):
        """Save progress data when simulation exits."""
        if self.progress_db and self.today_tasks:
            try:
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Calculate totals
                total_tasks = len(self.today_tasks)
                completed_tasks = len([t for t in self.today_tasks if t.get('completed', False)])
                skipped_tasks = len([t for t in self.today_tasks if t.get('skipped', False)])
                
                # Save daily summary
                success1 = self.progress_db.save_daily_summary(today, total_tasks, completed_tasks, skipped_tasks)
                
                # Save task details
                success2 = self.progress_db.save_task_details(today, self.today_tasks)
                
                if success1 and success2:
                    print(f"📊 Progress saved: {completed_tasks}/{total_tasks} completed ({completed_tasks/total_tasks*100:.1f}%)")
                else:
                    print("❌ Failed to save progress data")
                    
            except Exception as e:
                print(f"❌ Error saving progress: {e}")
    
    def _save_progress_manually(self):
        """Manually save progress data during simulation."""
        if self.progress_db and self.today_tasks:
            try:
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Calculate totals
                total_tasks = len(self.today_tasks)
                completed_tasks = len([t for t in self.today_tasks if t.get('completed', False)])
                skipped_tasks = len([t for t in self.today_tasks if t.get('skipped', False)])
                
                # Save daily summary
                success1 = self.progress_db.save_daily_summary(today, total_tasks, completed_tasks, skipped_tasks)
                
                # Save task details
                success2 = self.progress_db.save_task_details(today, self.today_tasks)
                
                if success1 and success2:
                    print(f"📊 Progress manually saved: {completed_tasks}/{total_tasks} completed ({completed_tasks/total_tasks*100:.1f}%)")
                else:
                    print("❌ Failed to save progress data manually")
                    
            except Exception as e:
                print(f"❌ Error saving progress manually: {e}")
    
    def _on_task_timer_complete(self, task):
        """Handle task timer completion."""
        if not task:
            return
        
        task_title = task.get('title', 'Unknown')
        
        # Check if task was completed
        if task.get('completed', False):
            print(f"✅ Timer completed - Task '{task_title}' was completed on time!")
            self.show_warning_popup("Great Job!", f"Completed '{task_title}' on time!")
        else:
            print(f"⏰ Timer completed - Task '{task_title}' was not completed")
            
            # Show distraction warning when timer runs out
            if self.voice_engine:
                self.speak_message(f"Time's up for {task_title}! Are you getting distracted?")
            
            # Show popup asking if user is distracted
            self.show_warning_popup("Time's Up!", 
                                  f"Time allocated for '{task_title}' has run out.\n"
                                  f"Are you getting distracted?\n\n"
                                  f"Click 'Complete' if you're done, or 'Skip' if you need to move on.")
            
            # Apply adaptive time adjustment (only if manager exists)
            if hasattr(self, 'adaptive_time_manager') and self.adaptive_time_manager:
                remaining_tasks = [t for t in self.today_tasks 
                                 if not t.get('completed', False) and not t.get('skipped', False)
                                 and t != task]
                
                adjusted_tasks = self.adaptive_time_manager.adjust_task_times(remaining_tasks, task)
                
                # Update the original tasks with adjusted times
                for i, original_task in enumerate(self.today_tasks):
                    for adjusted_task in adjusted_tasks:
                        if original_task.get('title') == adjusted_task.get('title'):
                            if adjusted_task.get('time_adjusted'):
                                original_task['duration'] = adjusted_task['duration']
                                original_task['original_duration'] = adjusted_task['original_duration']
                                original_task['time_adjusted'] = True
                                
                                # Show adjustment alert
                                adjustment = self.adaptive_time_manager.get_recent_adjustments(1)[0]
                                alert_msg = self.adaptive_time_manager.create_adjustment_alert(adjustment)
                                self.show_warning_popup("Time Adjusted", alert_msg)
                                print(f"⏰ Time adjustment: {alert_msg}")
                                break
            
            # Show backlog info
            if self.task_timer:
                backlog = self.task_timer.get_backlog()
                if backlog:
                    backlog_count = len(backlog)
                    self.show_warning_popup("Task Overdue", 
                                          f"'{task_title}' was not completed.\n"
                                          f"Reason saved to backlog.\n"
                                          f"Total overdue tasks: {backlog_count}")
        
        # Stop the timer
        if self.task_timer:
            self.task_timer.stop_timer()

    # BONUS FEATURE 1: Focus Mode Methods
    def start_focus_mode(self, task):
        """Start focus mode with Pomodoro timer for a specific task."""
        self.focus_mode = True
        self.focus_task = task
        self.pomodoro_start_time = time.time()
        self.pomodoro_timer = 25 * 60  # Reset to 25 minutes
        self.pomodoro_paused = False
        self.current_view = "focus"
        
        # Announce focus mode start
        if self.voice_engine:
            self.speak_message(f"Focus mode activated for {task.get('title', 'task')}. 25 minutes on the clock.")
        
        print(f"🎯 Focus mode started for: {task.get('title', 'task')}")

    def pause_focus_mode(self):
        """Pause the Pomodoro timer."""
        if self.focus_mode and not self.pomodoro_paused:
            self.pomodoro_paused = True
            self.pomodoro_pause_start = time.time()
            print("⏸️ Focus mode paused")

    def resume_focus_mode(self):
        """Resume the Pomodoro timer."""
        if self.focus_mode and self.pomodoro_paused:
            self.pomodoro_paused = False
            if self.pomodoro_pause_start:
                pause_duration = time.time() - self.pomodoro_pause_start
                self.pomodoro_start_time += pause_duration
            self.pomodoro_pause_start = None
            print("▶️ Focus mode resumed")

    def end_focus_mode(self):
        """End focus mode and return to idle."""
        self.focus_mode = False
        self.focus_task = None
        self.pomodoro_start_time = None
        self.pomodoro_paused = False
        self.pomodoro_pause_start = None
        self.current_view = "idle"
        
        # Award badge for using focus mode
        if "💎" not in self.earned_badges:
            self.earned_badges.append("💎")
            if self.voice_engine:
                self.speak_message("Congratulations! You've earned the Diamond Focus badge.")
        
        print("🎯 Focus mode ended")

    def get_pomodoro_time_remaining(self):
        """Get remaining time in Pomodoro timer."""
        if not self.focus_mode or not self.pomodoro_start_time:
            return 0
        
        if self.pomodoro_paused:
            elapsed = self.pomodoro_pause_start - self.pomodoro_start_time
        else:
            elapsed = time.time() - self.pomodoro_start_time
        
        remaining = self.pomodoro_timer - elapsed
        return max(0, remaining)

    def check_pomodoro_completion(self):
        """Check if Pomodoro timer is complete."""
        remaining = self.get_pomodoro_time_remaining()
        if remaining <= 0 and self.focus_mode:
            if self.voice_engine:
                self.speak_message("Time's up! Great work on your focus session.")
            self.show_popup = True
            self.popup_title = "Focus Session Complete!"
            self.popup_message = f"Great job staying focused on: {self.focus_task.get('title', 'task')}\n\nTake a 5-minute break, then continue with your day."
            self.popup_type = "success"
            return True
        return False

    # BONUS FEATURE 2: Distraction Alert Methods
    def update_interaction_time(self):
        """Update the last interaction time."""
        self.last_interaction_time = time.time()
        if self.distraction_warning_shown:
            self.distraction_warning_shown = False
            self.distraction_warning_time = None

    def check_distraction(self):
        """Check if user has been inactive for too long."""
        # Don't show distraction warnings when actively working on a task
        if (self.focus_mode or 
            self.current_view in ["focus", "distraction", "task"] or
            self.current_task is not None):
            return False
        
        time_since_interaction = time.time() - self.last_interaction_time
        
        if time_since_interaction > self.distraction_threshold and not self.distraction_warning_shown:
            self.distraction_warning_shown = True
            self.distraction_warning_time = time.time()
            self.current_view = "distraction"
            
            if self.voice_engine:
                self.speak_message("Hey! You've been inactive for a while. Are you getting distracted?")
            
            print("⚠️ Distraction alert triggered")
            return True
        
        # Hide warning after duration
        if (self.distraction_warning_shown and 
            self.distraction_warning_time and 
            time.time() - self.distraction_warning_time > self.distraction_warning_duration):
            self.distraction_warning_shown = False
            self.distraction_warning_time = None
            self.current_view = "idle"
        
        return False

    def dismiss_distraction_warning(self):
        """Dismiss the distraction warning."""
        self.distraction_warning_shown = False
        self.distraction_warning_time = None
        self.current_view = "idle"
        self.update_interaction_time()
        
        # Award badge for handling distraction
        if "🛡️" not in self.earned_badges:
            self.earned_badges.append("🛡️")
            if self.voice_engine:
                self.speak_message("Great job staying focused! You've earned the Distraction Shield badge.")

    # BONUS FEATURE 3: Emoji Analytics Methods
    def check_emoji_badges(self):
        """Check and award emoji badges based on performance."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's stats
        completed_count = len([t for t in self.today_tasks if t.get('completed', False)])
        total_count = len(self.today_tasks)
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        
        # Check for badges
        new_badges = []
        
        # 🚀 Rocket Start (first 3 tasks completed)
        if completed_count >= 3 and "🚀" not in self.earned_badges:
            new_badges.append("🚀")
        
        # 🔥 Focus Fire (5+ tasks completed)
        if completed_count >= 5 and "🔥" not in self.earned_badges:
            new_badges.append("🔥")
        
        # 🎯 Precision Player (100% completion)
        if completion_rate >= 100 and "🎯" not in self.earned_badges:
            new_badges.append("🎯")
        
        # ⏰ Time Master (all tasks on time - simplified check)
        if completed_count == total_count and total_count > 0 and "⏰" not in self.earned_badges:
            new_badges.append("⏰")
        
        # Add new badges
        for badge in new_badges:
            if badge not in self.earned_badges:
                self.earned_badges.append(badge)
                badge_name = self.emoji_analytics.get(badge, "Unknown Badge")
                if self.voice_engine:
                    self.speak_message(f"Congratulations! You've earned the {badge_name} badge!")
                print(f"🏆 Earned badge: {badge} - {badge_name}")
        
        return new_badges

    def get_badge_description(self, emoji):
        """Get description for a badge emoji."""
        return self.emoji_analytics.get(emoji, "Unknown Badge")

    def draw_badges_screen(self):
        """Draw the achievements/badges screen."""
        # Clear screen
        self.screen.fill(self.get_theme_color("background"))
        
        # Title
        title_text = "Achievements"
        title_surface, title_pos = self.responsive_text(title_text, self.large_font, 
                                                      self.get_theme_color("text"), 0.5, 0.1, center=True)
        self.screen.blit(title_surface, title_pos)
        
        # Earned badges
        earned_badges = [
            ("🏆", "Champion", "Complete 7 days in a row"),
            ("💎", "Diamond Focus", "Complete 30 tasks without skipping"),
            ("⚡", "Speed Demon", "Complete 5 tasks in one day"),
            ("🎯", "Precision Master", "Complete all tasks for 3 consecutive days")
        ]
        
        y_offset = 0.15
        for emoji, title, description in earned_badges:
            # Badge emoji and title
            badge_text = f"{emoji} {title}"
            badge_surface, badge_pos = self.responsive_text(badge_text, self.font, 
                                                          self.get_theme_color("success"), 0.3, y_offset, center=True)
            self.screen.blit(badge_surface, badge_pos)
            
            # Description
            desc_surface, desc_pos = self.responsive_text(description, self.small_font, 
                                                        self.get_theme_color("text"), 0.3, y_offset + 0.04, center=True)
            self.screen.blit(desc_surface, desc_pos)
            
            y_offset += 0.12
        
        # Available badges
        available_badges = [
            ("🌟", "Rising Star", "Complete your first task"),
            ("🔥", "On Fire", "Complete 10 tasks in a row"),
            ("🏅", "Gold Medal", "Complete all tasks for a week"),
            ("🚀", "Rocket", "Complete 50 total tasks")
        ]
        
        y_offset = 0.45
        for emoji, title, description in available_badges:
            # Badge emoji and title
            badge_text = f"{emoji} {title}"
            badge_surface, badge_pos = self.responsive_text(badge_text, self.font, 
                                                          self.get_theme_color("border"), 0.7, y_offset, center=True)
            self.screen.blit(badge_surface, badge_pos)
            
            # Description
            desc_surface, desc_pos = self.responsive_text(description, self.small_font, 
                                                        self.get_theme_color("text"), 0.7, y_offset + 0.04, center=True)
            self.screen.blit(desc_surface, desc_pos)
            
            y_offset += 0.12
        
        # Back button
        back_rect = self.responsive_rect(0.4, 0.85, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), back_rect)
        back_text, back_pos = self.responsive_text("Back", self.font, 
                                                  self.get_theme_color("text"), 0.5, 0.89, center=True)
        self.screen.blit(back_text, back_pos)
        
        return back_rect

    def draw_add_task_screen(self):
        """Draw the add task screen (Phase 6)."""
        # Clear screen
        self.screen.fill(self.get_theme_color("background"))
        
        # Title
        title_text = "Add New Task"
        title_surface, title_pos = self.responsive_text(title_text, self.large_font, 
                                                      self.get_theme_color("text"), 0.5, 0.1, center=True)
        self.screen.blit(title_surface, title_pos)
        
        # Task title input
        title_label_text = "Task Title:"
        title_label_surface, title_label_pos = self.responsive_text(title_label_text, self.font, 
                                                                  self.get_theme_color("text"), 0.2, 0.25, center=True)
        self.screen.blit(title_label_surface, title_label_pos)
        
        # Title input box
        title_input_rect = self.responsive_rect(0.25, 0.3, 0.5, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), title_input_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), title_input_rect, 2)
        
        # Display current title input
        if hasattr(self, 'new_task_title'):
            title_surface, title_pos = self.responsive_text(self.new_task_title, self.font, 
                                                          self.get_theme_color("text"), 0.5, 0.33, center=True)
            self.screen.blit(title_surface, title_pos)
        
        # Date input
        date_label_text = "Date:"
        date_label_surface, date_label_pos = self.responsive_text(date_label_text, self.font, 
                                                                 self.get_theme_color("text"), 0.2, 0.45, center=True)
        self.screen.blit(date_label_surface, date_label_pos)
        
        # Date input box (clickable)
        date_input_rect = self.responsive_rect(0.25, 0.5, 0.5, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("accent"), date_input_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), date_input_rect, 2)
        
        # Display current date input
        if hasattr(self, 'new_task_date'):
            # Format date for display
            try:
                date_obj = datetime.strptime(self.new_task_date, "%Y-%m-%d")
                display_date = date_obj.strftime("%B %d, %Y")
            except:
                display_date = self.new_task_date
            date_surface, date_pos = self.responsive_text(display_date, self.font, 
                                                        self.get_theme_color("text"), 0.5, 0.53, center=True)
            self.screen.blit(date_surface, date_pos)
        
        # Time input
        time_label_text = "Time:"
        time_label_surface, time_label_pos = self.responsive_text(time_label_text, self.font, 
                                                                self.get_theme_color("text"), 0.2, 0.6, center=True)
        self.screen.blit(time_label_surface, time_label_pos)
        
        # Time input box (clickable)
        time_input_rect = self.responsive_rect(0.25, 0.65, 0.5, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("accent"), time_input_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), time_input_rect, 2)
        
        # Display current time input
        if hasattr(self, 'new_task_time'):
            time_surface, time_pos = self.responsive_text(self.new_task_time, self.font, 
                                                        self.get_theme_color("text"), 0.5, 0.68, center=True)
            self.screen.blit(time_surface, time_pos)
        
        # Notes input
        notes_label_text = "Notes (optional):"
        notes_label_surface, notes_label_pos = self.responsive_text(notes_label_text, self.font, 
                                                                  self.get_theme_color("text"), 0.2, 0.75, center=True)
        self.screen.blit(notes_label_surface, notes_label_pos)
        
        # Notes input box
        notes_input_rect = self.responsive_rect(0.25, 0.8, 0.5, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), notes_input_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), notes_input_rect, 2)
        
        # Display current notes input
        if hasattr(self, 'new_task_notes'):
            notes_surface, notes_pos = self.responsive_text(self.new_task_notes, self.small_font, 
                                                          self.get_theme_color("text"), 0.5, 0.84, center=True)
            self.screen.blit(notes_surface, notes_pos)
        
        # Buttons
        # Add Task button
        add_rect = self.responsive_rect(0.25, 0.92, 0.2, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("success"), add_rect)
        add_text, add_pos = self.responsive_text("Add Task", self.font, 
                                                self.get_theme_color("text"), 0.35, 0.95, center=True)
        self.screen.blit(add_text, add_pos)
        
        # Cancel button
        cancel_rect = self.responsive_rect(0.55, 0.92, 0.2, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("error"), cancel_rect)
        cancel_text, cancel_pos = self.responsive_text("Cancel", self.font, 
                                                     self.get_theme_color("text"), 0.65, 0.95, center=True)
        self.screen.blit(cancel_text, cancel_pos)
        
        # Store input rectangles for click detection
        self.title_input_rect = title_input_rect
        self.date_input_rect = date_input_rect
        self.time_input_rect = time_input_rect
        self.notes_input_rect = notes_input_rect
        
        return add_rect, cancel_rect

    def draw_time_picker(self):
        """Draw a clickable clock interface for time selection."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(self.get_theme_color("background"))
        self.screen.blit(overlay, (0, 0))
        
        # Time picker container
        picker_rect = self.responsive_rect(0.2, 0.2, 0.6, 0.6)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), picker_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), picker_rect, 3)
        
        # Title
        title_text = "Select Time"
        title_surface, title_pos = self.responsive_text(title_text, self.large_font, 
                                                      self.get_theme_color("text"), 0.5, 0.25, center=True)
        self.screen.blit(title_surface, title_pos)
        
        # Clock face
        clock_center_x = int(self.width * 0.5)
        clock_center_y = int(self.height * 0.45)
        clock_radius = min(self.width, self.height) // 8
        
        # Draw clock face
        pygame.draw.circle(self.screen, self.get_theme_color("border"), 
                          (clock_center_x, clock_center_y), clock_radius, 2)
        pygame.draw.circle(self.screen, self.get_theme_color("background"), 
                          (clock_center_x, clock_center_y), clock_radius - 2)
        
        # Draw hour markers
        for hour in range(1, 13):
            angle = (hour - 3) * 30  # Start at 3 o'clock (90 degrees)
            angle_rad = math.radians(angle)
            marker_x = clock_center_x + int((clock_radius - 20) * math.cos(angle_rad))
            marker_y = clock_center_y + int((clock_radius - 20) * math.sin(angle_rad))
            
            # Draw hour marker
            pygame.draw.circle(self.screen, self.get_theme_color("text"), 
                              (marker_x, marker_y), 3)
            
            # Draw hour number
            hour_text = str(hour)
            hour_surface = self.font.render(hour_text, True, self.get_theme_color("text"))
            hour_pos = (marker_x - hour_surface.get_width() // 2, 
                       marker_y - hour_surface.get_height() // 2)
            self.screen.blit(hour_surface, hour_pos)
        
        # Draw current time hands
        current_hour = self.time_picker_hour
        if current_hour > 12:
            current_hour -= 12
        if current_hour == 0:
            current_hour = 12
            
        # Hour hand
        hour_angle = (current_hour - 3) * 30 + (self.time_picker_minute / 60) * 30
        hour_angle_rad = math.radians(hour_angle)
        hour_hand_x = clock_center_x + int((clock_radius - 40) * 0.6 * math.cos(hour_angle_rad))
        hour_hand_y = clock_center_y + int((clock_radius - 40) * 0.6 * math.sin(hour_angle_rad))
        pygame.draw.line(self.screen, self.get_theme_color("text"), 
                        (clock_center_x, clock_center_y), (hour_hand_x, hour_hand_y), 4)
        
        # Minute hand
        minute_angle = (self.time_picker_minute - 15) * 6  # 15 minutes = 90 degrees
        minute_angle_rad = math.radians(minute_angle)
        minute_hand_x = clock_center_x + int((clock_radius - 20) * 0.8 * math.cos(minute_angle_rad))
        minute_hand_y = clock_center_y + int((clock_radius - 20) * 0.8 * math.sin(minute_angle_rad))
        pygame.draw.line(self.screen, self.get_theme_color("accent"), 
                        (clock_center_x, clock_center_y), (minute_hand_x, minute_hand_y), 2)
        
        # Center dot
        pygame.draw.circle(self.screen, self.get_theme_color("text"), 
                          (clock_center_x, clock_center_y), 5)
        
        # Time display
        time_display = f"{self.time_picker_hour:02d}:{self.time_picker_minute:02d} {self.time_picker_am_pm}"
        time_surface, time_pos = self.responsive_text(time_display, self.large_font, 
                                                    self.get_theme_color("text"), 0.5, 0.6, center=True)
        self.screen.blit(time_surface, time_pos)
        
        # Control buttons
        # Hour up/down
        hour_up_rect = self.responsive_rect(0.35, 0.7, 0.08, 0.05)
        hour_down_rect = self.responsive_rect(0.35, 0.76, 0.08, 0.05)
        
        pygame.draw.rect(self.screen, self.get_theme_color("button"), hour_up_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), hour_up_rect, 2)
        hour_up_text, hour_up_pos = self.responsive_text("▲", self.font, 
                                                        self.get_theme_color("text"), 0.39, 0.725, center=True)
        self.screen.blit(hour_up_text, hour_up_pos)
        
        pygame.draw.rect(self.screen, self.get_theme_color("button"), hour_down_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), hour_down_rect, 2)
        hour_down_text, hour_down_pos = self.responsive_text("▼", self.font, 
                                                            self.get_theme_color("text"), 0.39, 0.785, center=True)
        self.screen.blit(hour_down_text, hour_down_pos)
        
        # Minute up/down
        minute_up_rect = self.responsive_rect(0.57, 0.7, 0.08, 0.05)
        minute_down_rect = self.responsive_rect(0.57, 0.76, 0.08, 0.05)
        
        pygame.draw.rect(self.screen, self.get_theme_color("button"), minute_up_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), minute_up_rect, 2)
        minute_up_text, minute_up_pos = self.responsive_text("▲", self.font, 
                                                            self.get_theme_color("text"), 0.61, 0.725, center=True)
        self.screen.blit(minute_up_text, minute_up_pos)
        
        pygame.draw.rect(self.screen, self.get_theme_color("button"), minute_down_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), minute_down_rect, 2)
        minute_down_text, minute_down_pos = self.responsive_text("▼", self.font, 
                                                                self.get_theme_color("text"), 0.61, 0.785, center=True)
        self.screen.blit(minute_down_text, minute_down_pos)
        
        # AM/PM toggle
        ampm_rect = self.responsive_rect(0.45, 0.7, 0.1, 0.05)
        pygame.draw.rect(self.screen, self.get_theme_color("accent"), ampm_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), ampm_rect, 2)
        ampm_text, ampm_pos = self.responsive_text(self.time_picker_am_pm, self.font, 
                                                   self.get_theme_color("text"), 0.5, 0.725, center=True)
        self.screen.blit(ampm_text, ampm_pos)
        
        # OK and Cancel buttons
        ok_rect = self.responsive_rect(0.35, 0.85, 0.1, 0.06)
        cancel_rect = self.responsive_rect(0.55, 0.85, 0.1, 0.06)
        
        pygame.draw.rect(self.screen, self.get_theme_color("success"), ok_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), ok_rect, 2)
        ok_text, ok_pos = self.responsive_text("OK", self.font, 
                                              self.get_theme_color("text"), 0.4, 0.88, center=True)
        self.screen.blit(ok_text, ok_pos)
        
        pygame.draw.rect(self.screen, self.get_theme_color("error"), cancel_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), cancel_rect, 2)
        cancel_text, cancel_pos = self.responsive_text("Cancel", self.font, 
                                                      self.get_theme_color("text"), 0.6, 0.88, center=True)
        self.screen.blit(cancel_text, cancel_pos)
        
        # Store rectangles for click detection
        self.time_picker_rects = {
            'hour_up': hour_up_rect,
            'hour_down': hour_down_rect,
            'minute_up': minute_up_rect,
            'minute_down': minute_down_rect,
            'ampm': ampm_rect,
            'ok': ok_rect,
            'cancel': cancel_rect
        }

    def draw_calendar(self):
        """Draw a calendar popup for date selection."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(self.get_theme_color("background"))
        self.screen.blit(overlay, (0, 0))
        
        # Calendar container
        calendar_rect = self.responsive_rect(0.15, 0.15, 0.7, 0.7)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), calendar_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), calendar_rect, 3)
        
        # Title with month/year
        month_names = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        title_text = f"{month_names[self.calendar_month - 1]} {self.calendar_year}"
        title_surface, title_pos = self.responsive_text(title_text, self.large_font, 
                                                      self.get_theme_color("text"), 0.5, 0.2, center=True)
        self.screen.blit(title_surface, title_pos)
        
        # Navigation buttons
        prev_rect = self.responsive_rect(0.2, 0.2, 0.08, 0.05)
        next_rect = self.responsive_rect(0.72, 0.2, 0.08, 0.05)
        
        pygame.draw.rect(self.screen, self.get_theme_color("button"), prev_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), prev_rect, 2)
        prev_text, prev_pos = self.responsive_text("◀", self.font, 
                                                  self.get_theme_color("text"), 0.24, 0.225, center=True)
        self.screen.blit(prev_text, prev_pos)
        
        pygame.draw.rect(self.screen, self.get_theme_color("button"), next_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), next_rect, 2)
        next_text, next_pos = self.responsive_text("▶", self.font, 
                                                  self.get_theme_color("text"), 0.76, 0.225, center=True)
        self.screen.blit(next_text, next_pos)
        
        # Day headers
        day_headers = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(day_headers):
            x_ratio = 0.2 + (i * 0.085)
            header_surface, header_pos = self.responsive_text(day, self.small_font, 
                                                            self.get_theme_color("text"), x_ratio, 0.3, center=True)
            self.screen.blit(header_surface, header_pos)
        
        # Calculate calendar grid
        first_day = datetime(self.calendar_year, self.calendar_month, 1)
        first_weekday = first_day.weekday()
        if first_weekday == 6:  # Sunday
            first_weekday = 0
        else:
            first_weekday += 1
            
        days_in_month = (datetime(self.calendar_year, self.calendar_month + 1, 1) - 
                        timedelta(days=1)).day
        
        # Draw calendar days
        day_rects = {}
        day = 1
        for week in range(6):
            for weekday in range(7):
                if week == 0 and weekday < first_weekday:
                    continue
                if day > days_in_month:
                    break
                    
                x_ratio = 0.2 + (weekday * 0.085)
                y_ratio = 0.35 + (week * 0.08)
                
                # Day rectangle
                day_rect = self.responsive_rect(x_ratio - 0.035, y_ratio - 0.025, 0.07, 0.06)
                
                # Highlight selected day
                if day == self.calendar_selected_day:
                    pygame.draw.rect(self.screen, self.get_theme_color("accent"), day_rect)
                else:
                    pygame.draw.rect(self.screen, self.get_theme_color("background"), day_rect)
                pygame.draw.rect(self.screen, self.get_theme_color("border"), day_rect, 1)
                
                # Day number
                day_surface, day_pos = self.responsive_text(str(day), self.font, 
                                                          self.get_theme_color("text"), x_ratio, y_ratio, center=True)
                self.screen.blit(day_surface, day_pos)
                
                day_rects[day] = day_rect
                day += 1
        
        # OK and Cancel buttons
        ok_rect = self.responsive_rect(0.35, 0.85, 0.1, 0.06)
        cancel_rect = self.responsive_rect(0.55, 0.85, 0.1, 0.06)
        
        pygame.draw.rect(self.screen, self.get_theme_color("success"), ok_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), ok_rect, 2)
        ok_text, ok_pos = self.responsive_text("OK", self.font, 
                                              self.get_theme_color("text"), 0.4, 0.88, center=True)
        self.screen.blit(ok_text, ok_pos)
        
        pygame.draw.rect(self.screen, self.get_theme_color("error"), cancel_rect)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), cancel_rect, 2)
        cancel_text, cancel_pos = self.responsive_text("Cancel", self.font, 
                                                      self.get_theme_color("text"), 0.6, 0.88, center=True)
        self.screen.blit(cancel_text, cancel_pos)
        
        # Store rectangles for click detection
        self.calendar_rects = {
            'prev': prev_rect,
            'next': next_rect,
            'ok': ok_rect,
            'cancel': cancel_rect,
            'days': day_rects
        }

    def draw_task_screen(self):
        """Draw the task screen with completion options and timer."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Task title with responsive text
        title_text = self.current_task['title']
        title_surface, title_pos = self.responsive_text(title_text, self.large_font, 
                                                      self.get_theme_color("text"), 0.5, 0.1, center=True)
        self.screen.blit(title_surface, title_pos)
        
        # Task time and duration
        if self.current_task.get('time'):
            time_text = f"Scheduled: {self.format_time_for_display(self.current_task['time'])}"
        else:
            time_text = f"Time: {self.current_task.get('time', 'Unknown')}"
        time_surface, time_pos = self.responsive_text(time_text, self.font, 
                                                    self.get_theme_color("warning"), 0.5, 0.15, center=True)
        self.screen.blit(time_surface, time_pos)
        
        # Duration info
        duration = self.current_task.get('duration', 0)
        if duration > 0:
            duration_text = f"Allocated Time: {duration} minutes"
            duration_surface, duration_pos = self.responsive_text(duration_text, self.small_font, 
                                                                self.get_theme_color("text"), 0.5, 0.18, center=True)
            self.screen.blit(duration_surface, duration_pos)
        
        # Task notes (wrapped) with responsive positioning
        notes = self.current_task.get('notes', 'No details available')
        notes_surface, notes_pos = self.responsive_text(notes, self.font, 
                                                      self.get_theme_color("text"), 0.5, 0.25, center=True)
        self.screen.blit(notes_surface, notes_pos)
        
        # Timer display (if timer is running)
        if self.task_timer and self.task_timer.is_running:
            # Timer background
            timer_bg_rect = self.responsive_rect(0.3, 0.35, 0.4, 0.1)
            pygame.draw.rect(self.screen, self.get_theme_color("accent"), timer_bg_rect)
            pygame.draw.rect(self.screen, self.get_theme_color("border"), timer_bg_rect, 3)
            
            # Timer label
            timer_label = "TIME REMAINING"
            timer_label_surface, timer_label_pos = self.responsive_text(timer_label, self.small_font, 
                                                                      self.get_theme_color("text"), 0.5, 0.37, center=True)
            self.screen.blit(timer_label_surface, timer_label_pos)
            
            # Timer display
            time_remaining = self.task_timer.get_formatted_time()
            time_color = self.get_theme_color("success") if self.task_timer.get_time_remaining() > 60 else self.get_theme_color("error")
            timer_surface, timer_pos = self.responsive_text(time_remaining, self.large_font, 
                                                          time_color, 0.5, 0.42, center=True)
            self.screen.blit(timer_surface, timer_pos)
        
        # Buttons
        button_y = 0.6
        
        # Complete button
        self.complete_rect = self.responsive_rect(0.2, button_y, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("success"), self.complete_rect)
        complete_text, complete_pos = self.responsive_text("✅ Complete", self.font, 
                                                         self.get_theme_color("text"), 0.3, button_y + 0.04, center=True)
        self.screen.blit(complete_text, complete_pos)
        
        # Skip button
        self.skip_rect = self.responsive_rect(0.6, button_y, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("warning"), self.skip_rect)
        skip_text, skip_pos = self.responsive_text("⏭️ Skip", self.font, 
                                                 self.get_theme_color("text"), 0.7, button_y + 0.04, center=True)
        self.screen.blit(skip_text, skip_pos)
        
        # Back button
        self.back_rect = self.responsive_rect(0.4, button_y + 0.12, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.back_rect)
        back_text, back_pos = self.responsive_text("← Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, button_y + 0.16, center=True)
        self.screen.blit(back_text, back_pos)

    def draw_stats_screen(self):
        """Draw the statistics screen with charts."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Title
        title_text, title_pos = self.responsive_text("Your Progress", self.large_font, 
                                                   self.get_theme_color("text"), 0.5, 0.05, center=True)
        self.screen.blit(title_text, title_pos)
        
        # Get today's stats
        completed_count = len([t for t in self.today_tasks if t.get('completed', False)])
        skipped_count = len([t for t in self.today_tasks if t.get('skipped', False)])
        total_count = len(self.today_tasks)
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        
        # Basic stats text
        stats_texts = [
            f"Tasks Completed: {completed_count}/{total_count}",
            f"Completion Rate: {completion_rate:.1f}%",
            f"Tasks Skipped: {skipped_count}",
            f"Badges Earned: {len(self.earned_badges)}"
        ]
        
        # Draw basic stats
        y_offset = 0.15
        for i, stat_text in enumerate(stats_texts):
            stat_surface, stat_pos = self.responsive_text(stat_text, self.font, 
                                                        self.get_theme_color("text"), 0.5, y_offset + (i * 0.06), center=True)
            self.screen.blit(stat_surface, stat_pos)
        
        # Draw progress bar chart
        self.draw_progress_bar(completion_rate, 0.4, 0.45, 0.2, 0.08)
        
        # Draw pie chart for task distribution
        self.draw_pie_chart(completed_count, skipped_count, total_count, 0.75, 0.45, 0.15)
        
        # Draw weekly trend (simulated data)
        self.draw_weekly_trend(0.5, 0.65, 0.4, 0.15)
        
        # Back button
        self.stats_back_rect = self.responsive_rect(0.4, 0.85, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.stats_back_rect)
        back_text, back_pos = self.responsive_text("Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.89, center=True)
        self.screen.blit(back_text, back_pos)
    
    def draw_progress_bar(self, percentage, x_ratio, y_ratio, width_ratio, height_ratio):
        """Draw a progress bar chart."""
        # Background bar
        bg_rect = self.responsive_rect(x_ratio, y_ratio, width_ratio, height_ratio)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), bg_rect)
        
        # Progress bar
        progress_width = (percentage / 100) * width_ratio
        if progress_width > 0:
            progress_rect = self.responsive_rect(x_ratio, y_ratio, progress_width, height_ratio)
            color = self.get_theme_color("success") if percentage >= 80 else self.get_theme_color("warning") if percentage >= 50 else self.get_theme_color("error")
            pygame.draw.rect(self.screen, color, progress_rect)
        
        # Percentage text
        text_surface, text_pos = self.responsive_text(f"{percentage:.1f}%", self.small_font, 
                                                    self.get_theme_color("text"), x_ratio + width_ratio/2, y_ratio + height_ratio/2, center=True)
        self.screen.blit(text_surface, text_pos)
        
        # Label
        label_surface, label_pos = self.responsive_text("Today's Progress", self.small_font, 
                                                      self.get_theme_color("text"), x_ratio + width_ratio/2, y_ratio - 0.02, center=True)
        self.screen.blit(label_surface, label_pos)
    
    def draw_pie_chart(self, completed, skipped, total, x_ratio, y_ratio, radius_ratio):
        """Draw a simple pie chart for task distribution."""
        if total == 0:
            return
        
        center_x = int(x_ratio * self.width)
        center_y = int(y_ratio * self.height)
        radius = int(radius_ratio * self.width)
        
        # Calculate angles
        completed_angle = (completed / total) * 360 if total > 0 else 0
        skipped_angle = (skipped / total) * 360 if total > 0 else 0
        
        # Draw completed slice
        if completed_angle > 0:
            start_angle = 0
            end_angle = completed_angle
            points = [(center_x, center_y)]
            for angle in range(int(start_angle), int(end_angle) + 1, 5):
                x = center_x + radius * math.cos(math.radians(angle))
                y = center_y - radius * math.sin(math.radians(angle))
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.polygon(self.screen, self.get_theme_color("success"), points)
        
        # Draw skipped slice
        if skipped_angle > 0:
            start_angle = completed_angle
            end_angle = completed_angle + skipped_angle
            points = [(center_x, center_y)]
            for angle in range(int(start_angle), int(end_angle) + 1, 5):
                x = center_x + radius * math.cos(math.radians(angle))
                y = center_y - radius * math.sin(math.radians(angle))
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.polygon(self.screen, self.get_theme_color("error"), points)
        
        # Draw remaining slice (incomplete)
        remaining_angle = 360 - completed_angle - skipped_angle
        if remaining_angle > 0:
            start_angle = completed_angle + skipped_angle
            end_angle = 360
            points = [(center_x, center_y)]
            for angle in range(int(start_angle), int(end_angle) + 1, 5):
                x = center_x + radius * math.cos(math.radians(angle))
                y = center_y - radius * math.sin(math.radians(angle))
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.polygon(self.screen, self.get_theme_color("border"), points)
        
        # Draw border
        pygame.draw.circle(self.screen, self.get_theme_color("text"), (center_x, center_y), radius, 2)
        
        # Legend
        legend_y = y_ratio + radius_ratio + 0.05
        legend_items = [
            ("Completed", self.get_theme_color("success")),
            ("Skipped", self.get_theme_color("error")),
            ("Remaining", self.get_theme_color("border"))
        ]
        
        for i, (label, color) in enumerate(legend_items):
            # Color box
            box_rect = self.responsive_rect(x_ratio - 0.05 + i * 0.08, legend_y, 0.02, 0.02)
            pygame.draw.rect(self.screen, color, box_rect)
            # Label
            label_surface, label_pos = self.responsive_text(label, self.small_font, 
                                                          self.get_theme_color("text"), 
                                                          x_ratio + i * 0.08, legend_y + 0.01, center=True)
            self.screen.blit(label_surface, label_pos)
    
    def draw_weekly_trend(self, x_ratio, y_ratio, width_ratio, height_ratio):
        """Draw a simple weekly trend chart."""
        # Chart background
        chart_rect = self.responsive_rect(x_ratio, y_ratio, width_ratio, height_ratio)
        pygame.draw.rect(self.screen, self.get_theme_color("border"), chart_rect, 2)
        
        # Simulated weekly data (in real app, this would come from database)
        weekly_data = [65, 72, 58, 85, 78, 90, 82]  # Completion rates for last 7 days
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        # Calculate bar positions
        bar_width = width_ratio / len(weekly_data) * 0.8
        bar_spacing = width_ratio / len(weekly_data) * 0.2
        
        for i, (day, rate) in enumerate(zip(days, weekly_data)):
            # Bar
            bar_height = (rate / 100) * height_ratio * 0.8
            bar_x = x_ratio + i * (bar_width + bar_spacing) + bar_spacing/2
            bar_y = y_ratio + height_ratio * 0.8 - bar_height
            bar_rect = self.responsive_rect(bar_x, bar_y, bar_width, bar_height)
            color = self.get_theme_color("success") if rate >= 80 else self.get_theme_color("warning") if rate >= 50 else self.get_theme_color("error")
            pygame.draw.rect(self.screen, color, bar_rect)
            
            # Day label
            day_surface, day_pos = self.responsive_text(day, self.small_font, 
                                                      self.get_theme_color("text"), 
                                                      bar_x + bar_width/2, y_ratio + height_ratio * 0.9, center=True)
            self.screen.blit(day_surface, day_pos)
        
        # Chart title
        title_surface, title_pos = self.responsive_text("Weekly Trend", self.small_font, 
                                                      self.get_theme_color("text"), 
                                                      x_ratio + width_ratio/2, y_ratio - 0.02, center=True)
        self.screen.blit(title_surface, title_pos)

    def draw_voice_settings_screen(self):
        """Draw the voice settings screen."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Title
        title_text, title_pos = self.responsive_text("🎤 Voice Settings", self.large_font, 
                                                   self.get_theme_color("text"), 0.5, 0.1, center=True)
        self.screen.blit(title_text, title_pos)
        
        # Current voice info
        current_voice_text = f"Current Voice: {self.voice_id}"
        current_voice_surface, current_voice_pos = self.responsive_text(current_voice_text, self.font, 
                                                                      self.get_theme_color("accent"), 0.5, 0.25, center=True)
        self.screen.blit(current_voice_surface, current_voice_pos)
        
        # Test voice button
        self.voice_test_button_rect = self.responsive_rect(0.35, 0.4, 0.3, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.voice_test_button_rect)
        test_text, test_pos = self.responsive_text("Test Voice", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.44, center=True)
        self.screen.blit(test_text, test_pos)
        
        # Back button
        self.voice_back_button_rect = self.responsive_rect(0.4, 0.8, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.voice_back_button_rect)
        back_text, back_pos = self.responsive_text("← Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.84, center=True)
        self.screen.blit(back_text, back_pos)

    def draw_backlog_screen(self):
        """Draw the backlog screen."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Title
        title_text, title_pos = self.responsive_text("📋 Task Backlog", self.large_font, 
                                                   self.get_theme_color("text"), 0.5, 0.1, center=True)
        self.screen.blit(title_text, title_pos)
        
        # Back button
        self.backlog_back_rect = self.responsive_rect(0.4, 0.8, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.backlog_back_rect)
        back_text, back_pos = self.responsive_text("← Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.84, center=True)
        self.screen.blit(back_text, back_pos)

    def draw_catch_up_screen(self):
        """Draw the catch-up screen for missed tasks with color-coded cards."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Get all catch-up tasks
        catch_up_tasks = self.get_catch_up_tasks()
        
        # Header Title: CATCH UP: X Missed Tasks
        header_text = f"CATCH UP: {len(catch_up_tasks)} Missed Tasks"
        header_surface, header_pos = self.responsive_text(header_text, self.large_font, 
                                                       self.get_theme_color("warning"), 0.5, 0.05, center=True)
        self.screen.blit(header_surface, header_pos)
        
        # Real-time clock
        time_text = f"Time: {self.current_time.strftime('%H:%M')}"
        time_surface, time_pos = self.responsive_text(time_text, self.font, 
                                                   self.get_theme_color("text"), 0.5, 0.12, center=True)
        self.screen.blit(time_surface, time_pos)
        
        if catch_up_tasks:
            # Display catch-up tasks with pagination
            tasks_per_page = 4
            start_idx = self.catch_up_page * tasks_per_page
            end_idx = start_idx + tasks_per_page
            current_page_tasks = catch_up_tasks[start_idx:end_idx]
            
            # Draw task cards
            y_offset = 0.2
            self.catch_up_task_rects = []
            self.catch_up_detail_rects = []
            
            for i, task in enumerate(current_page_tasks):
                task_y = y_offset + (i * 0.18)
                task_number = start_idx + i + 1
                
                # Determine card color based on status
                if task.get('completed', False):
                    card_color = self.get_theme_color("success")
                    status_text = "COMPLETED"
                elif task.get('skipped', False):
                    card_color = self.get_theme_color("error")
                    status_text = "SKIPPED"
                else:
                    card_color = self.get_theme_color("button")
                    status_text = "PENDING"
                
                # Task card
                task_rect = self.responsive_rect(0.05, task_y, 0.9, 0.15)
                pygame.draw.rect(self.screen, card_color, task_rect)
                pygame.draw.rect(self.screen, self.get_theme_color("border"), task_rect, 2)
                self.catch_up_task_rects.append(task_rect)
                
                # Task number and title
                title_text = f"{task_number}. {task['title']} ({task['original_time']})"
                title_surface, title_pos = self.responsive_text(title_text, self.font, 
                                                             self.get_theme_color("text"), 0.08, task_y + 0.02, center=False)
                self.screen.blit(title_surface, title_pos)
                
                # Task notes (truncated)
                notes = task['notes'][:60] + "..." if len(task['notes']) > 60 else task['notes']
                notes_surface, notes_pos = self.responsive_text(notes, self.small_font, 
                                                             self.get_theme_color("text"), 0.08, task_y + 0.06, center=False)
                self.screen.blit(notes_surface, notes_pos)
                
                # Status label on far right
                status_surface, status_pos = self.responsive_text(status_text, self.small_font, 
                                                               self.get_theme_color("text"), 0.75, task_y + 0.02, center=False)
                self.screen.blit(status_surface, status_pos)
                
                # View Details button (blue)
                detail_rect = self.responsive_rect(0.75, task_y + 0.06, 0.15, 0.06)
                pygame.draw.rect(self.screen, self.get_theme_color("accent"), detail_rect)
                detail_text, detail_pos = self.responsive_text("View Details", self.tiny_font, 
                                                            self.get_theme_color("text"), 0.825, task_y + 0.09, center=True)
                self.screen.blit(detail_text, detail_pos)
                self.catch_up_detail_rects.append(detail_rect)
            
            # Pagination controls
            total_pages = (len(catch_up_tasks) + tasks_per_page - 1) // tasks_per_page
            if total_pages > 1:
                page_y = 0.85
                
                # Page indicator
                page_text = f"Page {self.catch_up_page + 1} of {total_pages}"
                page_surface, page_pos = self.responsive_text(page_text, self.font, 
                                                           self.get_theme_color("text"), 0.5, page_y, center=True)
                self.screen.blit(page_surface, page_pos)
                
                # Previous page button
                if self.catch_up_page > 0:
                    prev_rect = self.responsive_rect(0.3, page_y + 0.05, 0.15, 0.08)
                    pygame.draw.rect(self.screen, self.get_theme_color("button"), prev_rect)
                    prev_text, prev_pos = self.responsive_text("← Previous", self.font, 
                                                             self.get_theme_color("text"), 0.375, page_y + 0.09, center=True)
                    self.screen.blit(prev_text, prev_pos)
                    self.catch_up_page_rects = [prev_rect]
                
                # Next page button
                if self.catch_up_page < total_pages - 1:
                    next_rect = self.responsive_rect(0.55, page_y + 0.05, 0.15, 0.08)
                    pygame.draw.rect(self.screen, self.get_theme_color("accent"), next_rect)
                    next_text, next_pos = self.responsive_text("Next →", self.font, 
                                                             self.get_theme_color("text"), 0.625, page_y + 0.09, center=True)
                    self.screen.blit(next_text, next_pos)
                    if hasattr(self, 'catch_up_page_rects'):
                        self.catch_up_page_rects.append(next_rect)
                    else:
                        self.catch_up_page_rects = [next_rect]
            
            # Bulk action buttons
            button_y = 0.95
            button_width = 0.25
            
            # ALL COMPLETE button (Green)
            complete_rect = self.responsive_rect(0.05, button_y, button_width, 0.08)
            pygame.draw.rect(self.screen, self.get_theme_color("success"), complete_rect)
            complete_text, complete_pos = self.responsive_text("ALL COMPLETE", self.font, 
                                                             self.get_theme_color("text"), 0.175, button_y + 0.04, center=True)
            self.screen.blit(complete_text, complete_pos)
            
            # DONE MARKED button (Blue)
            marked_rect = self.responsive_rect(0.35, button_y, button_width, 0.08)
            pygame.draw.rect(self.screen, self.get_theme_color("accent"), marked_rect)
            marked_text, marked_pos = self.responsive_text("DONE MARKED", self.font, 
                                                         self.get_theme_color("text"), 0.475, button_y + 0.04, center=True)
            self.screen.blit(marked_text, marked_pos)
            
            # ALL SKIP button (Red)
            skip_rect = self.responsive_rect(0.65, button_y, button_width, 0.08)
            pygame.draw.rect(self.screen, self.get_theme_color("error"), skip_rect)
            skip_text, skip_pos = self.responsive_text("ALL SKIP", self.font, 
                                                     self.get_theme_color("text"), 0.775, button_y + 0.04, center=True)
            self.screen.blit(skip_text, skip_pos)
            
            # Store bulk action rects
            self.catch_up_bulk_rects = [complete_rect, marked_rect, skip_rect]
        else:
            # No catch-up tasks message
            no_tasks_text = "No missed tasks to catch up on"
            no_tasks_surface, no_tasks_pos = self.responsive_text(no_tasks_text, self.font, 
                                                               self.get_theme_color("text"), 0.5, 0.5, center=True)
            self.screen.blit(no_tasks_surface, no_tasks_pos)
        
        # Back button
        self.catch_up_back_rect = self.responsive_rect(0.4, 0.02, 0.2, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.catch_up_back_rect)
        back_text, back_pos = self.responsive_text("← Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.05, center=True)
        self.screen.blit(back_text, back_pos)

    def draw_skipped_tasks_screen(self):
        """Draw the skipped tasks backlog for historical redemption."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Header Title: Skipped Tasks
        header_text = "Skipped Tasks"
        header_surface, header_pos = self.responsive_text(header_text, self.large_font, 
                                                       self.get_theme_color("text"), 0.5, 0.05, center=True)
        self.screen.blit(header_surface, header_pos)
        
        # Get skipped tasks from backlog
        skipped_tasks = self.backlog_manager.get_backlog_tasks()
        if skipped_tasks:
            # Display skipped tasks with pagination
            tasks_per_page = 6
            start_idx = self.backlog_page * tasks_per_page
            end_idx = start_idx + tasks_per_page
            current_page_tasks = skipped_tasks[start_idx:end_idx]
            
            # Draw task cards
            y_offset = 0.15
            self.skipped_task_rects = []
            self.skipped_complete_rects = []
            
            for i, task in enumerate(current_page_tasks):
                task_y = y_offset + (i * 0.12)
                
                # Dark grey card with yellow border
                task_rect = self.responsive_rect(0.05, task_y, 0.9, 0.1)
                pygame.draw.rect(self.screen, self.get_theme_color("button"), task_rect)
                pygame.draw.rect(self.screen, self.get_theme_color("warning"), task_rect, 2)
                self.skipped_task_rects.append(task_rect)
                
                # Task title and original time
                title_text = f"{task.get('task_title', 'Unknown')} - Time: {task.get('original_date', 'Unknown')}"
                title_surface, title_pos = self.responsive_text(title_text, self.font, 
                                                             self.get_theme_color("text"), 0.08, task_y + 0.02, center=False)
                self.screen.blit(title_surface, title_pos)
                
                # Complete button (Green)
                complete_rect = self.responsive_rect(0.75, task_y + 0.02, 0.15, 0.06)
                pygame.draw.rect(self.screen, self.get_theme_color("success"), complete_rect)
                complete_text, complete_pos = self.responsive_text("Complete", self.small_font, 
                                                                self.get_theme_color("text"), 0.825, task_y + 0.05, center=True)
                self.screen.blit(complete_text, complete_pos)
                self.skipped_complete_rects.append(complete_rect)
            
            # Pagination for skipped tasks
            total_pages = (len(skipped_tasks) + tasks_per_page - 1) // tasks_per_page
            if total_pages > 1:
                page_y = 0.85
                page_text = f"Page {self.backlog_page + 1} of {total_pages}"
                page_surface, page_pos = self.responsive_text(page_text, self.font, 
                                                           self.get_theme_color("text"), 0.5, page_y, center=True)
                self.screen.blit(page_surface, page_pos)
        else:
            # No skipped tasks message
            no_tasks_text = "No skipped tasks in backlog"
            no_tasks_surface, no_tasks_pos = self.responsive_text(no_tasks_text, self.font, 
                                                               self.get_theme_color("text"), 0.5, 0.5, center=True)
            self.screen.blit(no_tasks_surface, no_tasks_pos)
        
        # Back button
        self.skipped_back_rect = self.responsive_rect(0.4, 0.9, 0.2, 0.08)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.skipped_back_rect)
        back_text, back_pos = self.responsive_text("← Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.94, center=True)
        self.screen.blit(back_text, back_pos)

    def draw_all_tasks_screen(self):
        """Draw the all tasks screen with paginated task display."""
        self.screen.fill(self.get_theme_color("background"))
        
        # Header Title: All Tasks
        header_text = "All Tasks for Today"
        header_surface, header_pos = self.responsive_text(header_text, self.large_font, 
                                                       self.get_theme_color("text"), 0.5, 0.05, center=True)
        self.screen.blit(header_surface, header_pos)
        
        # Get all tasks (catch-up first, then regular)
        all_tasks = []
        
        # Add catch-up tasks FIRST (these are the missed tasks from the original list)
        catch_up_tasks = self.get_catch_up_tasks()
        for task in catch_up_tasks:
            task['is_catch_up'] = True
            all_tasks.append(task)
        
        # Add regular tasks (excluding missed ones that are already shown as catch-up)
        for task in self.today_tasks:
            if not task.get('was_missed', False):
                task['is_regular'] = True
                all_tasks.append(task)
        
        if all_tasks:
            # Display tasks with pagination (4 per page like catch-up screen)
            tasks_per_page = 4
            start_idx = self.all_tasks_page * tasks_per_page
            end_idx = start_idx + tasks_per_page
            current_page_tasks = all_tasks[start_idx:end_idx]
            
            # Draw task cards
            y_offset = 0.15
            self.all_task_rects = []
            self.all_complete_rects = []
            self.all_skip_rects = []
            self.all_details_rects = []
            
            for i, task in enumerate(current_page_tasks):
                task_y = y_offset + (i * 0.15)
                
                # Determine card color based on task status
                if task.get('completed', False):
                    card_color = self.get_theme_color("success")
                    border_color = self.get_theme_color("success")
                    status_text = "COMPLETED"
                elif task.get('skipped', False):
                    card_color = self.get_theme_color("skipped")
                    border_color = self.get_theme_color("warning")
                    status_text = "SKIPPED"
                elif task.get('is_catch_up', False):
                    card_color = self.get_theme_color("warning")
                    border_color = self.get_theme_color("warning")
                    status_text = "CATCH-UP"
                else:
                    card_color = self.get_theme_color("button")
                    border_color = self.get_theme_color("accent")
                    status_text = "PENDING"
                
                # Task card
                task_rect = self.responsive_rect(0.05, task_y, 0.9, 0.12)
                pygame.draw.rect(self.screen, card_color, task_rect)
                pygame.draw.rect(self.screen, border_color, task_rect, 2)
                self.all_task_rects.append(task_rect)
                
                # Task title and time
                title_text = f"{task.get('title', 'Unknown Task')}"
                if task.get('time'):
                    title_text += f" ({self.format_time_for_display(task.get('time'))})"
                title_surface, title_pos = self.responsive_text(title_text, self.font, 
                                                             self.get_theme_color("text"), 0.08, task_y + 0.02, center=False)
                self.screen.blit(title_surface, title_pos)
                
                # Status indicator
                status_surface, status_pos = self.responsive_text(status_text, self.small_font, 
                                                               self.get_theme_color("text"), 0.08, task_y + 0.06, center=False)
                self.screen.blit(status_surface, status_pos)
                
                # Action buttons
                button_y_pos = task_y + 0.03
                
                # View Details button (Blue) - for all tasks
                details_rect = self.responsive_rect(0.60, button_y_pos, 0.10, 0.04)
                pygame.draw.rect(self.screen, self.get_theme_color("accent"), details_rect)
                details_text, details_pos = self.responsive_text("Details", self.small_font, 
                                                              self.get_theme_color("text"), 0.65, button_y_pos + 0.02, center=True)
                self.screen.blit(details_text, details_pos)
                self.all_details_rects.append((details_rect, task))
                
                # Action buttons (only for pending tasks)
                if not task.get('completed', False) and not task.get('skipped', False):
                    # Complete button (Green)
                    complete_rect = self.responsive_rect(0.71, button_y_pos, 0.10, 0.04)
                    pygame.draw.rect(self.screen, self.get_theme_color("success"), complete_rect)
                    complete_text, complete_pos = self.responsive_text("Complete", self.small_font, 
                                                                    self.get_theme_color("text"), 0.76, button_y_pos + 0.02, center=True)
                    self.screen.blit(complete_text, complete_pos)
                    self.all_complete_rects.append((complete_rect, task))
                    
                    # Skip button (Red)
                    skip_rect = self.responsive_rect(0.82, button_y_pos, 0.08, 0.04)
                    pygame.draw.rect(self.screen, self.get_theme_color("error"), skip_rect)
                    skip_text, skip_pos = self.responsive_text("Skip", self.small_font, 
                                                             self.get_theme_color("text"), 0.86, button_y_pos + 0.02, center=True)
                    self.screen.blit(skip_text, skip_pos)
                    self.all_skip_rects.append((skip_rect, task))
            
            # Pagination
            total_pages = (len(all_tasks) + tasks_per_page - 1) // tasks_per_page
            if total_pages > 1:
                page_y = 0.85
                page_text = f"Page {self.all_tasks_page + 1} of {total_pages} ({len(all_tasks)} total tasks)"
                page_surface, page_pos = self.responsive_text(page_text, self.font, 
                                                           self.get_theme_color("text"), 0.5, page_y, center=True)
                self.screen.blit(page_surface, page_pos)
                
                # Navigation buttons
                if self.all_tasks_page > 0:
                    prev_rect = self.responsive_rect(0.3, 0.9, 0.15, 0.06)
                    pygame.draw.rect(self.screen, self.get_theme_color("button"), prev_rect)
                    prev_text, prev_pos = self.responsive_text("← Previous", self.font, 
                                                             self.get_theme_color("text"), 0.375, 0.93, center=True)
                    self.screen.blit(prev_text, prev_pos)
                    self.all_tasks_prev_rect = prev_rect
                
                if self.all_tasks_page < total_pages - 1:
                    next_rect = self.responsive_rect(0.55, 0.9, 0.15, 0.06)
                    pygame.draw.rect(self.screen, self.get_theme_color("button"), next_rect)
                    next_text, next_pos = self.responsive_text("Next →", self.font, 
                                                             self.get_theme_color("text"), 0.625, 0.93, center=True)
                    self.screen.blit(next_text, next_pos)
                    self.all_tasks_next_rect = next_rect
        else:
            # No tasks message
            no_tasks_text = "No tasks scheduled for today"
            no_tasks_surface, no_tasks_pos = self.responsive_text(no_tasks_text, self.font, 
                                                               self.get_theme_color("text"), 0.5, 0.5, center=True)
            self.screen.blit(no_tasks_surface, no_tasks_pos)
        
        # Back button
        self.all_tasks_back_rect = self.responsive_rect(0.4, 0.02, 0.2, 0.06)
        pygame.draw.rect(self.screen, self.get_theme_color("button"), self.all_tasks_back_rect)
        back_text, back_pos = self.responsive_text("← Back", self.font, 
                                                 self.get_theme_color("text"), 0.5, 0.05, center=True)
        self.screen.blit(back_text, back_pos)

    def handle_bulk_action(self, action_index):
        """Handle bulk actions for catch-up tasks."""
        catch_up_task = self.get_next_task()
        if not catch_up_task or not catch_up_task.get('is_catch_up'):
            return
        
        missed_tasks = catch_up_task.get('missed_tasks', [])
        tasks_per_page = 4
        start_idx = self.catch_up_page * tasks_per_page
        end_idx = start_idx + tasks_per_page
        current_page_tasks = missed_tasks[start_idx:end_idx]
        
        if action_index == 0:  # ALL COMPLETE
            # Mark all tasks on current page as completed
            for task in current_page_tasks:
                task['completed'] = True
            if self.voice_engine:
                self.speak_message(f"Completed {len(current_page_tasks)} catch-up tasks!")
            
        elif action_index == 1:  # DONE MARKED
            # Check if any tasks are marked for completion
            marked_tasks = [t for t in current_page_tasks if t.get('marked_for_completion', False)]
            if marked_tasks:
                for task in marked_tasks:
                    task['completed'] = True
                if self.voice_engine:
                    self.speak_message(f"Completed {len(marked_tasks)} marked tasks!")
            else:
                # Show warning popup
                self.show_popup = True
                self.popup_title = "No Tasks Marked"
                self.popup_message = "Please mark tasks for completion first by clicking on them."
                self.popup_type = "warning"
            
        elif action_index == 2:  # ALL SKIP
            # Mark all tasks on current page as skipped
            for task in current_page_tasks:
                task['skipped'] = True
            if self.voice_engine:
                self.speak_message(f"Skipped {len(current_page_tasks)} catch-up tasks!")
        
        # Navigate to next page with incomplete tasks or back to idle
        self._navigate_catch_up_pages()

    def _navigate_catch_up_pages(self):
        """Navigate to next page with incomplete tasks or back to idle."""
        catch_up_task = self.get_next_task()
        if not catch_up_task or not catch_up_task.get('is_catch_up'):
            self.current_view = "idle"
            return
        
        missed_tasks = catch_up_task.get('missed_tasks', [])
        tasks_per_page = 4
        total_pages = (len(missed_tasks) + tasks_per_page - 1) // tasks_per_page
        
        # Find next page with incomplete tasks
        for page in range(self.catch_up_page + 1, total_pages):
            start_idx = page * tasks_per_page
            end_idx = start_idx + tasks_per_page
            page_tasks = missed_tasks[start_idx:end_idx]
            
            incomplete_tasks = [t for t in page_tasks if not t.get('completed', False) and not t.get('skipped', False)]
            if incomplete_tasks:
                self.catch_up_page = page
                return
        
        # If no more pages with incomplete tasks, go back to idle
        self.current_view = "idle"

    def complete_current_task(self):
        """Complete the current task."""
        if self.current_task:
            self.current_task['completed'] = True
            self.completed_tasks.append(self.current_task)
            self.completed_tasks_count += 1
            
            if self.voice_engine:
                self.speak_message(f"Great job completing {self.current_task['title']}!")
            
            # Clear cached next task so it will be recalculated
            self.cached_next_task = None
            
            self.current_view = "idle"
            self.current_task = None

    def skip_current_task(self):
        """Skip the current task."""
        if self.current_task:
            self.current_task['skipped'] = True
            self.skipped_tasks.append(self.current_task)
            self.skipped_tasks_count += 1
            
            if self.voice_engine:
                self.speak_message(f"Task {self.current_task['title']} skipped. That's okay!")
            
            # Clear cached next task so it will be recalculated
            self.cached_next_task = None
            
            self.current_view = "idle"
            self.current_task = None

    def announce_next_task(self, task):
        """Announce the next task with voice."""
        if self.voice_engine:
            task_title = task.get('title', 'task')
            task_notes = task.get('notes', '')
            full_message = f"You need to start on: {task_title}. {task_notes}"
            self.speak_message(full_message)

def main():
    """Run the Pi simulation."""
    print("🔍 DEBUG: Starting main function...")
    try:
        print("🔍 DEBUG: Creating PiSimulation object...")
        simulation = PiSimulation()
        print("🔍 DEBUG: PiSimulation object created successfully")
        
        print("🔍 DEBUG: Starting simulation run...")
        simulation.run()
        print("🔍 DEBUG: Simulation run completed")
        
    except Exception as e:
        print(f"❌ DEBUG: Simulation error: {e}")
        import traceback
        traceback.print_exc()
        print("Make sure you have pygame installed: pip install pygame")

if __name__ == "__main__":
    print("🔍 DEBUG: Script started")
    main()
    print("🔍 DEBUG: Script finished") 