"""
System Monitor Module

This module provides system monitoring and failure recovery capabilities,
including hardware detection, resource monitoring, and automatic recovery.

Author: Raspberry Pi Day Planner
License: MIT
"""

import logging
import threading
import time
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import psutil


class SystemMonitor:
    """
    System monitoring and failure recovery system.
    
    This class provides:
    - Hardware status monitoring
    - Resource usage tracking
    - Failure detection and recovery
    - Health check reporting
    - Automatic restart capabilities
    """
    
    def __init__(self, 
                 audio_manager: Any = None,
                 display_manager: Any = None,
                 notification_callback: Optional[Callable] = None):
        """
        Initialize the system monitor.
        
        Args:
            audio_manager: Audio manager for alert sounds.
            display_manager: Display manager for notifications.
            notification_callback: Callback for sending notifications.
        """
        self.logger = logging.getLogger(__name__)
        self.audio_manager = audio_manager
        self.display_manager = display_manager
        self.notification_callback = notification_callback
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Health thresholds
        self.thresholds = {
            'cpu_usage': 90.0,      # CPU usage percentage
            'memory_usage': 85.0,   # Memory usage percentage
            'disk_usage': 90.0,     # Disk usage percentage
            'temperature': 80.0,    # CPU temperature in Celsius
            'uptime_minutes': 5     # Minimum uptime before monitoring
        }
        
        # Health status
        self.health_status = {
            'last_check': None,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'temperature': 0.0,
            'uptime': 0.0,
            'display_connected': True,
            'audio_working': True,
            'overall_health': 'healthy'
        }
        
        # Failure tracking
        self.failure_count = 0
        self.last_failure = None
        self.recovery_attempts = 0
        
        self.logger.info("System monitor initialized")
    
    def start_monitoring(self, interval: int = 30):
        """
        Start system monitoring.
        
        Args:
            interval: Monitoring interval in seconds.
        """
        if self.monitoring:
            self.logger.warning("System monitoring is already running")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info(f"System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._check_system_health()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _check_system_health(self):
        """Check overall system health."""
        try:
            # Update health status
            self.health_status['last_check'] = datetime.now()
            self.health_status['cpu_usage'] = self._get_cpu_usage()
            self.health_status['memory_usage'] = self._get_memory_usage()
            self.health_status['disk_usage'] = self._get_disk_usage()
            self.health_status['temperature'] = self._get_cpu_temperature()
            self.health_status['uptime'] = self._get_system_uptime()
            self.health_status['display_connected'] = self._check_display_connection()
            self.health_status['audio_working'] = self._check_audio_system()
            
            # Determine overall health
            health_issues = []
            
            if self.health_status['cpu_usage'] > self.thresholds['cpu_usage']:
                health_issues.append(f"High CPU usage: {self.health_status['cpu_usage']:.1f}%")
            
            if self.health_status['memory_usage'] > self.thresholds['memory_usage']:
                health_issues.append(f"High memory usage: {self.health_status['memory_usage']:.1f}%")
            
            if self.health_status['disk_usage'] > self.thresholds['disk_usage']:
                health_issues.append(f"High disk usage: {self.health_status['disk_usage']:.1f}%")
            
            if self.health_status['temperature'] > self.thresholds['temperature']:
                health_issues.append(f"High temperature: {self.health_status['temperature']:.1f}°C")
            
            if not self.health_status['display_connected']:
                health_issues.append("Display connection lost")
            
            if not self.health_status['audio_working']:
                health_issues.append("Audio system not working")
            
            # Update overall health status
            if health_issues:
                self.health_status['overall_health'] = 'warning'
                self._handle_health_warning(health_issues)
            else:
                self.health_status['overall_health'] = 'healthy'
                # Reset failure count if system is healthy
                if self.failure_count > 0:
                    self.logger.info("System recovered, resetting failure count")
                    self.failure_count = 0
                    self.recovery_attempts = 0
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            self.health_status['overall_health'] = 'error'
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"Error getting CPU usage: {e}")
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage."""
        try:
            memory = psutil.virtual_memory()
            return memory.percent
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return 0.0
    
    def _get_disk_usage(self) -> float:
        """Get current disk usage percentage."""
        try:
            disk = psutil.disk_usage('/')
            return (disk.used / disk.total) * 100
        except Exception as e:
            self.logger.error(f"Error getting disk usage: {e}")
            return 0.0
    
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature in Celsius."""
        try:
            # Try to read temperature from Raspberry Pi thermal zone
            temp_file = Path('/sys/class/thermal/thermal_zone0/temp')
            if temp_file.exists():
                with open(temp_file, 'r') as f:
                    temp = int(f.read().strip()) / 1000.0
                return temp
            
            # Fallback: try to get temperature using psutil
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 0:
                                return entry.current
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error getting CPU temperature: {e}")
            return 0.0
    
    def _get_system_uptime(self) -> float:
        """Get system uptime in minutes."""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            return uptime_seconds / 60.0
        except Exception as e:
            self.logger.error(f"Error getting system uptime: {e}")
            return 0.0
    
    def _check_display_connection(self) -> bool:
        """Check if display is connected and working."""
        try:
            # Check if X11 display is available
            display = subprocess.run(
                ['xrandr', '--listmonitors'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return display.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error checking display connection: {e}")
            return False
    
    def _check_audio_system(self) -> bool:
        """Check if audio system is working."""
        try:
            # Check if ALSA is working
            result = subprocess.run(
                ['aplay', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error checking audio system: {e}")
            return False
    
    def _handle_health_warning(self, issues: List[str]):
        """Handle health warnings and trigger recovery actions."""
        self.failure_count += 1
        self.last_failure = datetime.now()
        
        # Log the issues
        for issue in issues:
            self.logger.warning(f"Health issue detected: {issue}")
        
        # Send notification if callback is available
        if self.notification_callback:
            try:
                message = f"System health warning: {'; '.join(issues)}"
                self.notification_callback("System Health Warning", message)
            except Exception as e:
                self.logger.error(f"Error sending notification: {e}")
        
        # Play alert sound
        if self.audio_manager:
            try:
                self.audio_manager.play_error()
            except Exception as e:
                self.logger.error(f"Error playing alert sound: {e}")
        
        # Attempt recovery if failure count is high
        if self.failure_count >= 3 and self.recovery_attempts < 3:
            self._attempt_recovery(issues)
    
    def _attempt_recovery(self, issues: List[str]):
        """Attempt to recover from system issues."""
        self.recovery_attempts += 1
        self.logger.warning(f"Attempting system recovery (attempt {self.recovery_attempts}/3)")
        
        try:
            # Restart audio system if needed
            if "Audio system not working" in issues and self.audio_manager:
                self.logger.info("Restarting audio system...")
                self.audio_manager.close()
                time.sleep(2)
                # Reinitialize audio manager (this would need to be implemented)
            
            # Restart display system if needed
            if "Display connection lost" in issues:
                self.logger.info("Attempting to reconnect display...")
                # Try to restart X11 or reconnect display
                subprocess.run(['xrandr', '--auto'], timeout=10)
            
            # Clear disk space if needed
            if any("High disk usage" in issue for issue in issues):
                self.logger.info("Cleaning up disk space...")
                self._cleanup_disk_space()
            
            # Log recovery attempt
            self.logger.info(f"Recovery attempt {self.recovery_attempts} completed")
            
        except Exception as e:
            self.logger.error(f"Error during recovery attempt: {e}")
    
    def _cleanup_disk_space(self):
        """Clean up disk space by removing old files."""
        try:
            # Clean up old log files
            log_dir = Path(__file__).parent.parent / "logs"
            if log_dir.exists():
                for log_file in log_dir.glob("*.log.*"):
                    if log_file.stat().st_mtime < (time.time() - 7 * 24 * 3600):  # 7 days
                        log_file.unlink()
                        self.logger.info(f"Deleted old log file: {log_file}")
            
            # Clean up old reports
            reports_dir = Path(__file__).parent.parent / "reports"
            if reports_dir.exists():
                for report_file in reports_dir.glob("*"):
                    if report_file.stat().st_mtime < (time.time() - 30 * 24 * 3600):  # 30 days
                        report_file.unlink()
                        self.logger.info(f"Deleted old report: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up disk space: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current system health status.
        
        Returns:
            Dictionary containing health status information.
        """
        return self.health_status.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get detailed system information.
        
        Returns:
            Dictionary containing system information.
        """
        try:
            info = {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_total': psutil.disk_usage('/').total,
                'disk_free': psutil.disk_usage('/').free,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'python_version': psutil.sys.version,
                'platform': psutil.sys.platform
            }
            
            # Add Raspberry Pi specific info
            if Path('/proc/cpuinfo').exists():
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'Raspberry Pi' in cpuinfo:
                        info['device'] = 'Raspberry Pi'
                        # Extract model info
                        for line in cpuinfo.split('\n'):
                            if line.startswith('Model'):
                                info['model'] = line.split(':')[1].strip()
                                break
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def is_healthy(self) -> bool:
        """
        Check if the system is currently healthy.
        
        Returns:
            True if system is healthy, False otherwise.
        """
        return self.health_status['overall_health'] == 'healthy'
    
    def get_failure_stats(self) -> Dict[str, Any]:
        """
        Get failure statistics.
        
        Returns:
            Dictionary containing failure statistics.
        """
        return {
            'failure_count': self.failure_count,
            'recovery_attempts': self.recovery_attempts,
            'last_failure': self.last_failure.isoformat() if self.last_failure else None,
            'uptime_minutes': self.health_status['uptime']
        }
    
    def reset_failure_count(self):
        """Reset failure count and recovery attempts."""
        self.failure_count = 0
        self.recovery_attempts = 0
        self.last_failure = None
        self.logger.info("Failure count reset")
    
    def set_thresholds(self, **kwargs):
        """
        Update monitoring thresholds.
        
        Args:
            **kwargs: Threshold values to update.
        """
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                self.logger.info(f"Updated threshold {key}: {value}")
            else:
                self.logger.warning(f"Unknown threshold: {key}")
    
    def __del__(self):
        """Cleanup when the monitor is destroyed."""
        self.stop_monitoring() 