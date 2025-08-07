"""
Pi Detection and Configuration Module

This module detects if the application is running on actual Raspberry Pi hardware
and configures the application accordingly for optimal performance.

Author: Raspberry Pi Day Planner
License: MIT
"""

import os
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class PiDetector:
    """
    Detects Raspberry Pi hardware and configures application settings.
    
    This class handles:
    - Hardware detection (Pi vs simulation)
    - Pi-specific configuration
    - Performance optimizations
    - Audio/display settings for Pi
    """
    
    def __init__(self):
        """Initialize the Pi detector."""
        self.logger = logging.getLogger(__name__)
        self.is_pi = False
        self.pi_model = None
        self.pi_config = {}
        
        self._detect_hardware()
        self._configure_for_hardware()
    
    def _detect_hardware(self):
        """Detect if running on Raspberry Pi hardware."""
        try:
            # Method 1: Check for Pi-specific files
            if os.path.exists('/proc/device-tree/model'):
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().strip()
                    if 'Raspberry Pi' in model:
                        self.is_pi = True
                        self.pi_model = model
                        self.logger.info(f"Detected Pi hardware: {model}")
                        return
            
            # Method 2: Check CPU info
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'BCM2708' in cpuinfo or 'BCM2709' in cpuinfo or 'BCM2711' in cpuinfo:
                        self.is_pi = True
                        self.pi_model = "Raspberry Pi (detected via CPU)"
                        self.logger.info("Detected Pi hardware via CPU info")
                        return
            
            # Method 3: Check for Pi-specific environment variables
            if 'RASPBERRY_PI' in os.environ:
                self.is_pi = True
                self.pi_model = "Raspberry Pi (environment variable)"
                self.logger.info("Detected Pi hardware via environment variable")
                return
            
            # Method 4: Check platform
            if platform.system() == 'Linux':
                try:
                    result = subprocess.run(['cat', '/etc/os-release'], 
                                         capture_output=True, text=True)
                    if 'raspbian' in result.stdout.lower() or 'raspberry' in result.stdout.lower():
                        self.is_pi = True
                        self.pi_model = "Raspberry Pi (OS detection)"
                        self.logger.info("Detected Pi hardware via OS detection")
                        return
                except:
                    pass
            
            self.logger.info("Running in simulation mode (not on Pi hardware)")
            
        except Exception as e:
            self.logger.warning(f"Error detecting hardware: {e}")
            self.is_pi = False
    
    def _configure_for_hardware(self):
        """Configure application settings based on detected hardware."""
        if self.is_pi:
            self.pi_config = {
                # Display settings for Pi
                'display': {
                    'fullscreen': True,
                    'vsync': True,
                    'hardware_acceleration': True,
                    'screen_timeout': 300,  # 5 minutes
                    'brightness': 0.8,
                    'font_size_multiplier': 1.2  # Larger fonts for Pi display
                },
                
                # Audio settings for Pi
                'audio': {
                    'device': 'default',  # Use Pi's default audio
                    'sample_rate': 44100,
                    'channels': 2,
                    'buffer_size': 1024,  # Larger buffer for Pi
                    'volume': 0.8
                },
                
                # Performance settings for Pi
                'performance': {
                    'max_fps': 30,  # Lower FPS for Pi
                    'enable_vsync': True,
                    'reduce_animations': True,
                    'memory_limit': 512,  # MB
                    'cpu_throttle': True
                },
                
                # Pi-specific features
                'features': {
                    'enable_gpio': True,
                    'enable_led_indicators': True,
                    'enable_touch_support': True,
                    'auto_brightness': True
                }
            }
        else:
            # Simulation/desktop settings
            self.pi_config = {
                'display': {
                    'fullscreen': False,
                    'vsync': False,
                    'hardware_acceleration': False,
                    'screen_timeout': 0,  # No timeout in simulation
                    'brightness': 1.0,
                    'font_size_multiplier': 1.0
                },
                
                'audio': {
                    'device': 'default',
                    'sample_rate': 44100,
                    'channels': 2,
                    'buffer_size': 512,
                    'volume': 0.7
                },
                
                'performance': {
                    'max_fps': 60,
                    'enable_vsync': False,
                    'reduce_animations': False,
                    'memory_limit': 1024,
                    'cpu_throttle': False
                },
                
                'features': {
                    'enable_gpio': False,
                    'enable_led_indicators': False,
                    'enable_touch_support': False,
                    'auto_brightness': False
                }
            }
        
        self.logger.info(f"Configured for {'Pi hardware' if self.is_pi else 'simulation'}")
    
    def is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi hardware."""
        return self.is_pi
    
    def get_pi_model(self) -> Optional[str]:
        """Get the detected Pi model."""
        return self.pi_model
    
    def get_config(self) -> Dict[str, Any]:
        """Get the hardware-specific configuration."""
        return self.pi_config
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get display-specific configuration."""
        return self.pi_config.get('display', {})
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio-specific configuration."""
        return self.pi_config.get('audio', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-specific configuration."""
        return self.pi_config.get('performance', {})
    
    def get_feature_config(self) -> Dict[str, Any]:
        """Get feature-specific configuration."""
        return self.pi_config.get('features', {})
    
    def optimize_for_pi(self):
        """Apply Pi-specific optimizations."""
        if not self.is_pi:
            return
        
        try:
            # Set environment variables for Pi
            os.environ['SDL_VIDEODRIVER'] = 'fbcon'
            os.environ['SDL_FBDEV'] = '/dev/fb0'
            os.environ['SDL_AUDIODRIVER'] = 'alsa'
            
            # Disable screen saver
            os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
            
            self.logger.info("Applied Pi-specific optimizations")
            
        except Exception as e:
            self.logger.warning(f"Failed to apply Pi optimizations: {e}")
    
    def check_pi_health(self) -> Dict[str, Any]:
        """Check Pi hardware health and status."""
        health = {
            'is_pi': self.is_pi,
            'model': self.pi_model,
            'temperature': None,
            'memory_usage': None,
            'cpu_usage': None,
            'disk_usage': None
        }
        
        if not self.is_pi:
            return health
        
        try:
            # Check CPU temperature
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = int(f.read().strip()) / 1000.0
                    health['temperature'] = f"{temp:.1f}°C"
            
            # Check memory usage
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    total = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
                    available = int([line for line in meminfo.split('\n') if 'MemAvailable' in line][0].split()[1])
                    used = total - available
                    usage_percent = (used / total) * 100
                    health['memory_usage'] = f"{usage_percent:.1f}%"
            
            # Check disk usage
            try:
                result = subprocess.run(['df', '/'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 5:
                            usage_percent = parts[4].replace('%', '')
                            health['disk_usage'] = f"{usage_percent}%"
            except:
                pass
            
        except Exception as e:
            self.logger.warning(f"Error checking Pi health: {e}")
        
        return health


# Global instance
pi_detector = PiDetector()
