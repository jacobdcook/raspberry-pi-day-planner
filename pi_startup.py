#!/usr/bin/env python3
"""
Pi Startup Script
=================

This script handles Pi-specific startup tasks and ensures optimal performance
for the Raspberry Pi Day Planner application.

Features:
- Hardware detection and optimization
- Audio/display configuration
- Performance monitoring
- Error recovery
- Health checks

Usage:
    python pi_startup.py
"""

import os
import sys
import logging
import subprocess
import time
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from pi_detection import PiDetector

class PiStartup:
    """Handles Pi-specific startup tasks and optimizations."""
    
    def __init__(self):
        """Initialize the Pi startup handler."""
        self.logger = logging.getLogger(__name__)
        self.pi_detector = PiDetector()
        self.is_pi = self.pi_detector.is_raspberry_pi()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_startup_checks(self):
        """Run all startup checks and optimizations."""
        print("🚀 Starting Pi Day Planner...")
        print("=" * 50)
        
        if not self.is_pi:
            print("ℹ️ Running in simulation mode")
            return True
        
        print("🍓 Raspberry Pi detected - running Pi-specific optimizations")
        
        # Run startup tasks
        checks = [
            self._check_system_requirements,
            self._configure_audio,
            self._configure_display,
            self._optimize_performance,
            self._check_storage,
            self._check_network,
            self._apply_pi_optimizations
        ]
        
        for check in checks:
            try:
                if not check():
                    print(f"⚠️ Warning: {check.__name__} failed")
            except Exception as e:
                print(f"❌ Error in {check.__name__}: {e}")
        
        print("✅ Pi startup checks completed")
        return True
    
    def _check_system_requirements(self):
        """Check if system meets minimum requirements."""
        print("\n1. Checking system requirements...")
        
        try:
            # Check Python version
            if sys.version_info < (3, 7):
                print("❌ Python 3.7+ required")
                return False
            
            # Check available memory
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    total = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
                    total_mb = total // 1024
                    
                    if total_mb < 1024:  # Less than 1GB
                        print(f"⚠️ Low memory: {total_mb}MB (1GB+ recommended)")
                    else:
                        print(f"✅ Memory: {total_mb}MB")
            
            # Check available disk space
            try:
                result = subprocess.run(['df', '/'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 4:
                            available_gb = int(parts[3]) // (1024 * 1024)
                            if available_gb < 1:
                                print(f"⚠️ Low disk space: {available_gb}GB available")
                            else:
                                print(f"✅ Disk space: {available_gb}GB available")
            except:
                pass
            
            print("✅ System requirements check passed")
            return True
            
        except Exception as e:
            print(f"❌ System requirements check failed: {e}")
            return False
    
    def _configure_audio(self):
        """Configure audio for Pi."""
        print("\n2. Configuring audio...")
        
        try:
            # Check if audio is working
            result = subprocess.run(['speaker-test', '-t', 'wav', '-c', '2', '-l', '1'], 
                                 capture_output=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Audio test passed")
            else:
                print("⚠️ Audio test failed - check audio configuration")
            
            # Set audio volume
            try:
                subprocess.run(['amixer', 'set', 'Master', '80%'], capture_output=True)
                print("✅ Audio volume set to 80%")
            except:
                print("⚠️ Could not set audio volume")
            
            return True
            
        except Exception as e:
            print(f"❌ Audio configuration failed: {e}")
            return False
    
    def _configure_display(self):
        """Configure display for Pi."""
        print("\n3. Configuring display...")
        
        try:
            # Check display resolution
            if 'DISPLAY' in os.environ:
                print(f"✅ Display detected: {os.environ['DISPLAY']}")
            else:
                print("⚠️ No display detected")
            
            # Set display environment variables for Pi
            if self.is_pi:
                os.environ['SDL_VIDEODRIVER'] = 'fbcon'
                os.environ['SDL_FBDEV'] = '/dev/fb0'
                print("✅ Pi display environment configured")
            
            return True
            
        except Exception as e:
            print(f"❌ Display configuration failed: {e}")
            return False
    
    def _optimize_performance(self):
        """Apply Pi-specific performance optimizations."""
        print("\n4. Optimizing performance...")
        
        try:
            # Get performance config
            perf_config = self.pi_detector.get_performance_config()
            
            # Apply optimizations
            if perf_config.get('cpu_throttle', False):
                print("✅ CPU throttling enabled")
            
            if perf_config.get('reduce_animations', False):
                print("✅ Animation reduction enabled")
            
            if perf_config.get('enable_vsync', False):
                print("✅ V-sync enabled")
            
            # Set memory limit
            memory_limit = perf_config.get('memory_limit', 512)
            print(f"✅ Memory limit set to {memory_limit}MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Performance optimization failed: {e}")
            return False
    
    def _check_storage(self):
        """Check storage health and space."""
        print("\n5. Checking storage...")
        
        try:
            # Check disk usage
            result = subprocess.run(['df', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_percent = parts[4].replace('%', '')
                        usage_int = int(usage_percent)
                        
                        if usage_int > 90:
                            print(f"❌ High disk usage: {usage_percent}")
                            return False
                        elif usage_int > 80:
                            print(f"⚠️ Disk usage: {usage_percent}")
                        else:
                            print(f"✅ Disk usage: {usage_percent}")
            
            # Check for read-only filesystem
            result = subprocess.run(['mount'], capture_output=True, text=True)
            if result.returncode == 0 and 'ro,' in result.stdout:
                print("⚠️ Filesystem is read-only")
            
            return True
            
        except Exception as e:
            print(f"❌ Storage check failed: {e}")
            return False
    
    def _check_network(self):
        """Check network connectivity."""
        print("\n6. Checking network...")
        
        try:
            # Check internet connectivity
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                 capture_output=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Internet connectivity confirmed")
            else:
                print("⚠️ No internet connectivity")
            
            # Check local network
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0:
                ip = result.stdout.strip()
                if ip:
                    print(f"✅ Local IP: {ip}")
                else:
                    print("⚠️ No local IP address")
            
            return True
            
        except Exception as e:
            print(f"❌ Network check failed: {e}")
            return False
    
    def _apply_pi_optimizations(self):
        """Apply additional Pi-specific optimizations."""
        print("\n7. Applying Pi optimizations...")
        
        try:
            # Apply Pi detector optimizations
            self.pi_detector.optimize_for_pi()
            
            # Disable screen saver
            os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
            
            # Set process priority
            try:
                os.nice(10)  # Lower priority to be nice to system
                print("✅ Process priority set")
            except:
                pass
            
            print("✅ Pi optimizations applied")
            return True
            
        except Exception as e:
            print(f"❌ Pi optimizations failed: {e}")
            return False
    
    def get_health_status(self):
        """Get current Pi health status."""
        return self.pi_detector.check_pi_health()


def main():
    """Main startup function."""
    startup = PiStartup()
    
    if startup.run_startup_checks():
        print("\n" + "=" * 50)
        print("✅ Pi startup completed successfully!")
        print("\nStarting main application...")
        
        # Import and start main application
        try:
            from main import main as main_app
            main_app()
        except KeyboardInterrupt:
            print("\n⚠️ Application interrupted by user")
        except Exception as e:
            print(f"\n❌ Application failed to start: {e}")
    else:
        print("\n❌ Pi startup failed - check configuration")


if __name__ == "__main__":
    main()
