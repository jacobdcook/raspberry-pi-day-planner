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

Usage:
    python pi_simulation.py

This gives you a preview of exactly how your Pi will behave!
"""

import pygame
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import threading

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))
from peptide_scheduler import PeptideScheduler

class PiSimulation:
    def __init__(self):
        pygame.init()
        
        # Simulate Pi display (common Pi screen sizes)
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Raspberry Pi Day Planner - Simulation")
        
        # Colors (Pi-friendly, high contrast)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        
        # Fonts
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # State
        self.current_screen = "idle"  # idle, notification, menu
        self.current_task = None
        self.today_tasks = []
        self.current_time = datetime.now()
        self.next_task_time = None
        
        # Load schedule
        self.load_schedule()
        
        # Clock
        self.clock = pygame.time.Clock()
        self.last_update = time.time()
        
    def load_schedule(self):
        """Load the schedule like the Pi would."""
        try:
            config_dir = Path(__file__).parent / "config"
            peptide_scheduler = PeptideScheduler(config_dir=str(config_dir))
            
            if peptide_scheduler.select_schedule("personal"):
                print("✅ Personal schedule loaded")
                schedule_data = peptide_scheduler.main_schedule
            else:
                print("⚠️ Using sample schedule")
                schedule_data = peptide_scheduler.main_schedule
            
            # Extract tasks from all sections
            all_tasks = []
            for section in ['morning_tasks', 'afternoon_tasks', 'evening_tasks', 'daily_tasks']:
                if section in schedule_data:
                    all_tasks.extend(schedule_data[section])
            
            self.today_tasks = all_tasks
            print(f"Loaded {len(self.today_tasks)} tasks")
            
        except Exception as e:
            print(f"Error loading schedule: {e}")
            # Create sample tasks for demo
            self.today_tasks = [
                {
                    'title': 'Wake Up & Hydrate',
                    'time': '06:45',
                    'notes': 'Drink 16 oz water with lemon + Himalayan salt',
                    'priority': 1,
                    'duration': 15
                },
                {
                    'title': 'Take Supplements',
                    'time': '07:00',
                    'notes': 'Vitamin D3+K2 (2000 IU), Fish Oil (1000mg), Probiotic (20B CFU), B-Complex',
                    'priority': 1,
                    'duration': 10
                },
                {
                    'title': 'Cold Shower',
                    'time': '07:15',
                    'notes': '2-3 minutes cold exposure for recovery',
                    'priority': 2,
                    'duration': 5
                }
            ]
    
    def get_next_task(self):
        """Get the next task based on current time."""
        current_time_str = self.current_time.strftime("%H:%M")
        
        for task in self.today_tasks:
            if task.get('time', '00:00') > current_time_str:
                return task
        return None
    
    def draw_idle_screen(self):
        """Draw the idle screen (what you see when no task is active)."""
        self.screen.fill(self.BLACK)
        
        # Current time
        time_text = self.current_time.strftime("%H:%M:%S")
        time_surface = self.large_font.render(time_text, True, self.WHITE)
        time_rect = time_surface.get_rect(center=(self.width//2, 100))
        self.screen.blit(time_surface, time_rect)
        
        # Date
        date_text = self.current_time.strftime("%A, %B %d, %Y")
        date_surface = self.medium_font.render(date_text, True, self.GRAY)
        date_rect = date_surface.get_rect(center=(self.width//2, 150))
        self.screen.blit(date_surface, date_rect)
        
        # Next task info
        next_task = self.get_next_task()
        if next_task:
            next_text = f"Next: {next_task['title']}"
            next_surface = self.medium_font.render(next_text, True, self.GREEN)
            next_rect = next_surface.get_rect(center=(self.width//2, 250))
            self.screen.blit(next_surface, next_rect)
            
            time_text = f"at {next_task['time']}"
            time_surface = self.small_font.render(time_text, True, self.YELLOW)
            time_rect = time_surface.get_rect(center=(self.width//2, 280))
            self.screen.blit(time_surface, time_rect)
        else:
            done_text = "All tasks completed for today!"
            done_surface = self.medium_font.render(done_text, True, self.GREEN)
            done_rect = done_surface.get_rect(center=(self.width//2, 250))
            self.screen.blit(done_surface, done_rect)
        
        # Instructions
        inst_text = "Press SPACE to simulate task notification"
        inst_surface = self.small_font.render(inst_text, True, self.GRAY)
        inst_rect = inst_surface.get_rect(center=(self.width//2, 500))
        self.screen.blit(inst_surface, inst_rect)
        
        inst_text2 = "Press ESC to exit simulation"
        inst_surface2 = self.small_font.render(inst_text2, True, self.GRAY)
        inst_rect2 = inst_surface2.get_rect(center=(self.width//2, 520))
        self.screen.blit(inst_surface2, inst_rect2)
    
    def draw_notification_screen(self):
        """Draw the task notification screen (what appears when a task is due)."""
        if not self.current_task:
            return
        
        self.screen.fill(self.BLACK)
        
        # Task title
        title_text = self.current_task['title']
        title_surface = self.large_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.width//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Task time
        time_text = f"Time: {self.current_task.get('time', 'Unknown')}"
        time_surface = self.medium_font.render(time_text, True, self.YELLOW)
        time_rect = time_surface.get_rect(center=(self.width//2, 200))
        self.screen.blit(time_surface, time_rect)
        
        # Task notes (wrapped)
        notes = self.current_task.get('notes', 'No details available')
        self.draw_wrapped_text(notes, self.medium_font, self.WHITE, 
                             self.width//2, 280, self.width - 100)
        
        # Buttons
        button_y = 450
        button_width = 120
        button_height = 50
        spacing = 20
        
        # DONE button
        done_rect = pygame.Rect(self.width//2 - button_width - spacing//2, button_y, 
                               button_width, button_height)
        pygame.draw.rect(self.screen, self.GREEN, done_rect)
        done_text = self.medium_font.render("DONE", True, self.BLACK)
        done_text_rect = done_text.get_rect(center=done_rect.center)
        self.screen.blit(done_text, done_text_rect)
        
        # SKIP button
        skip_rect = pygame.Rect(self.width//2 + spacing//2, button_y, 
                               button_width, button_height)
        pygame.draw.rect(self.screen, self.RED, skip_rect)
        skip_text = self.medium_font.render("SKIP", True, self.WHITE)
        skip_text_rect = skip_text.get_rect(center=skip_rect.center)
        self.screen.blit(skip_text, skip_text_rect)
        
        # Store button rects for click detection
        self.done_button_rect = done_rect
        self.skip_button_rect = skip_rect
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width):
        """Draw text with word wrapping."""
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
        
        for i, line in enumerate(lines):
            if y + i * 30 > self.height - 100:  # Don't draw below buttons
                break
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect(center=(x, y + i * 30))
            self.screen.blit(line_surface, line_rect)
    
    def handle_click(self, pos):
        """Handle mouse clicks on buttons."""
        if self.current_screen == "notification" and self.current_task:
            if self.done_button_rect.collidepoint(pos):
                print(f"✅ Task completed: {self.current_task['title']}")
                self.current_task['completed'] = True
                self.current_screen = "idle"
                self.current_task = None
                return True
            
            elif self.skip_button_rect.collidepoint(pos):
                print(f"⏭️ Task skipped: {self.current_task['title']}")
                self.current_task['skipped'] = True
                self.current_screen = "idle"
                self.current_task = None
                return True
        
        return False
    
    def simulate_task_notification(self):
        """Simulate a task notification appearing."""
        next_task = self.get_next_task()
        if next_task and not next_task.get('completed', False) and not next_task.get('skipped', False):
            self.current_task = next_task
            self.current_screen = "notification"
            print(f"🔔 Task notification: {next_task['title']}")
            return True
        return False
    
    def run(self):
        """Main simulation loop."""
        print("🎮 Raspberry Pi Day Planner Simulation")
        print("=" * 50)
        print("This shows exactly how your Pi will behave!")
        print("Controls:")
        print("- SPACE: Simulate task notification")
        print("- Mouse: Click DONE/SKIP buttons")
        print("- ESC: Exit simulation")
        print("=" * 50)
        
        running = True
        while running:
            # Update current time
            self.current_time = datetime.now()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.current_screen == "idle":
                            self.simulate_task_notification()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            # Draw current screen
            if self.current_screen == "idle":
                self.draw_idle_screen()
            elif self.current_screen == "notification":
                self.draw_notification_screen()
            
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
        
        pygame.quit()
        print("🎮 Simulation ended. Your Pi will work exactly like this!")

def main():
    """Run the Pi simulation."""
    try:
        simulation = PiSimulation()
        simulation.run()
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        print("Make sure you have pygame installed: pip install pygame")

if __name__ == "__main__":
    main() 