"""
Configuration Watcher Module

This module provides automatic configuration reloading by monitoring
the YAML configuration file for changes using watchdog.

Author: Raspberry Pi Day Planner
License: MIT
"""

import logging
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import yaml


class ConfigFileHandler(FileSystemEventHandler):
    """
    File system event handler for configuration file changes.
    
    Monitors the YAML configuration file and triggers reload callbacks
    when changes are detected.
    """
    
    def __init__(self, config_path: Path, reload_callback: Callable[[Dict[str, Any]], None]):
        """
        Initialize the file handler.
        
        Args:
            config_path: Path to the configuration file to monitor.
            reload_callback: Callback function to execute when config changes.
        """
        self.config_path = config_path
        self.reload_callback = reload_callback
        self.logger = logging.getLogger(__name__)
        self.last_modified = 0
        self.debounce_time = 1.0  # seconds
        
    def on_modified(self, event):
        """
        Handle file modification events.
        
        Args:
            event: File system event.
        """
        if not isinstance(event, FileModifiedEvent):
            return
            
        if event.src_path != str(self.config_path):
            return
            
        # Debounce rapid file changes
        current_time = time.time()
        if current_time - self.last_modified < self.debounce_time:
            return
            
        self.last_modified = current_time
        
        try:
            self.logger.info(f"Configuration file changed: {self.config_path}")
            
            # Small delay to ensure file is fully written
            time.sleep(0.1)
            
            # Load and validate new configuration
            with open(self.config_path, 'r', encoding='utf-8') as file:
                new_config = yaml.safe_load(file)
            
            if new_config is not None:
                self.logger.info("Configuration reloaded successfully")
                self.reload_callback(new_config)
            else:
                self.logger.warning("Configuration file is empty or invalid")
                
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")


class ConfigWatcher:
    """
    Configuration file watcher that monitors for changes and triggers reloads.
    
    This class provides:
    - Automatic file monitoring using watchdog
    - Debounced change detection
    - Configuration validation
    - Thread-safe reload callbacks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration watcher.
        
        Args:
            config_path: Path to the configuration file to monitor.
                        Defaults to 'config/schedule.yaml' relative to project root.
        """
        self.logger = logging.getLogger(__name__)
        
        if config_path is None:
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "schedule.yaml"
        
        self.config_path = Path(config_path)
        self.observer = Observer()
        self.file_handler = None
        self.watching = False
        self.reload_callbacks = []
        
        self.logger.info(f"Configuration watcher initialized for: {self.config_path}")
    
    def add_reload_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Add a callback function to be executed when configuration changes.
        
        Args:
            callback: Function to call with the new configuration.
        """
        self.reload_callbacks.append(callback)
        self.logger.debug(f"Added reload callback: {callback.__name__}")
    
    def remove_reload_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Remove a reload callback function.
        
        Args:
            callback: Function to remove.
        """
        if callback in self.reload_callbacks:
            self.reload_callbacks.remove(callback)
            self.logger.debug(f"Removed reload callback: {callback.__name__}")
    
    def _execute_callbacks(self, config: Dict[str, Any]):
        """
        Execute all registered reload callbacks.
        
        Args:
            config: New configuration data.
        """
        for callback in self.reload_callbacks:
            try:
                callback(config)
            except Exception as e:
                self.logger.error(f"Error in reload callback {callback.__name__}: {e}")
    
    def start_watching(self):
        """Start monitoring the configuration file for changes."""
        if self.watching:
            self.logger.warning("Configuration watcher is already running")
            return
        
        if not self.config_path.exists():
            self.logger.error(f"Configuration file not found: {self.config_path}")
            return
        
        try:
            # Create file handler
            self.file_handler = ConfigFileHandler(
                self.config_path, 
                self._execute_callbacks
            )
            
            # Schedule observer
            self.observer.schedule(
                self.file_handler,
                str(self.config_path.parent),
                recursive=False
            )
            
            # Start observer
            self.observer.start()
            self.watching = True
            
            self.logger.info("Configuration watcher started")
            
        except Exception as e:
            self.logger.error(f"Failed to start configuration watcher: {e}")
    
    def stop_watching(self):
        """Stop monitoring the configuration file."""
        if not self.watching:
            return
        
        try:
            self.observer.stop()
            self.observer.join()
            self.watching = False
            
            self.logger.info("Configuration watcher stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping configuration watcher: {e}")
    
    def reload_config(self) -> Optional[Dict[str, Any]]:
        """
        Manually reload the configuration file.
        
        Returns:
            Configuration data if successful, None otherwise.
        """
        try:
            if not self.config_path.exists():
                self.logger.error(f"Configuration file not found: {self.config_path}")
                return None
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            if config is not None:
                self.logger.info("Configuration manually reloaded")
                self._execute_callbacks(config)
                return config
            else:
                self.logger.warning("Configuration file is empty or invalid")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to manually reload configuration: {e}")
            return None
    
    def is_watching(self) -> bool:
        """
        Check if the watcher is currently monitoring the file.
        
        Returns:
            True if watching, False otherwise.
        """
        return self.watching
    
    def get_config_path(self) -> Path:
        """
        Get the path of the configuration file being monitored.
        
        Returns:
            Configuration file path.
        """
        return self.config_path
    
    def __del__(self):
        """Cleanup when the watcher is destroyed."""
        self.stop_watching() 