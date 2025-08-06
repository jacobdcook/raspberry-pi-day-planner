"""
Audio Manager Module

This module handles audio playback using pygame mixer for alert sounds,
completion sounds, and snooze sounds.

Author: Raspberry Pi Day Planner
License: MIT
"""

import pygame
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any


class AudioManager:
    """
    Manages audio playback using pygame mixer.
    
    This class handles:
    - Initializing pygame mixer
    - Loading and playing sound files
    - Volume control
    - Sound file management
    - Error handling for missing audio files
    """
    
    def __init__(self, sounds_dir: Optional[str] = None):
        """
        Initialize the audio manager.
        
        Args:
            sounds_dir: Directory containing sound files.
                       Defaults to 'sounds' relative to project root.
        """
        self.logger = logging.getLogger(__name__)
        
        # Set sounds directory
        if sounds_dir is None:
            project_root = Path(__file__).parent.parent
            sounds_dir = project_root / "sounds"
        
        self.sounds_dir = Path(sounds_dir)
        
        # Initialize pygame mixer
        self.mixer_initialized = False
        self.sounds = {}
        self.volume = 0.7
        
        # Default sound file names
        self.default_sounds = {
            'alert': 'alert.wav',
            'completion': 'completion.wav',
            'snooze': 'snooze.wav',
            'error': 'error.wav'
        }
        
        self._initialize_mixer()
        self._load_sounds()
        
        self.logger.info("Audio manager initialized")
    
    def _initialize_mixer(self):
        """Initialize pygame mixer."""
        try:
            # Initialize pygame mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_initialized = True
            self.logger.info("Pygame mixer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pygame mixer: {e}")
            self.mixer_initialized = False
    
    def _load_sounds(self):
        """Load sound files from the sounds directory."""
        if not self.mixer_initialized:
            self.logger.warning("Mixer not initialized, skipping sound loading")
            return
        
        # Create sounds directory if it doesn't exist
        self.sounds_dir.mkdir(exist_ok=True)
        
        # Load each sound file
        for sound_name, filename in self.default_sounds.items():
            sound_path = self.sounds_dir / filename
            
            if sound_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(sound_path))
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    self.logger.info(f"Loaded sound: {filename}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load sound {filename}: {e}")
            else:
                self.logger.warning(f"Sound file not found: {sound_path}")
                # Create a default sound if file doesn't exist
                self._create_default_sound(sound_name, filename)
    
    def _create_default_sound(self, sound_name: str, filename: str):
        """
        Create a default sound file if it doesn't exist.
        
        Args:
            sound_name: Name of the sound.
            filename: Filename for the sound file.
        """
        try:
            # Create a simple beep sound using pygame
            sample_rate = 44100
            duration = 0.5  # seconds
            
            if sound_name == 'alert':
                frequency = 800  # Hz
            elif sound_name == 'completion':
                frequency = 1000  # Hz
            elif sound_name == 'snooze':
                frequency = 600  # Hz
            else:
                frequency = 500  # Hz
            
            # Generate a simple sine wave
            import numpy as np
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit PCM
            wave = (wave * 32767).astype(np.int16)
            
            # Save as WAV file
            import wave as wave_module
            
            sound_path = self.sounds_dir / filename
            with wave_module.open(str(sound_path), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(wave.tobytes())
            
            # Load the created sound
            sound = pygame.mixer.Sound(str(sound_path))
            sound.set_volume(self.volume)
            self.sounds[sound_name] = sound
            
            self.logger.info(f"Created default sound: {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default sound {filename}: {e}")
    
    def play_alert(self):
        """Play the alert sound."""
        self._play_sound('alert')
    
    def play_completion(self):
        """Play the completion sound."""
        self._play_sound('completion')
    
    def play_snooze(self):
        """Play the snooze sound."""
        self._play_sound('snooze')
    
    def play_error(self):
        """Play the error sound."""
        self._play_sound('error')
    
    def _play_sound(self, sound_name: str):
        """
        Play a sound by name.
        
        Args:
            sound_name: Name of the sound to play.
        """
        if not self.mixer_initialized:
            self.logger.warning("Mixer not initialized, cannot play sound")
            return
        
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                self.logger.debug(f"Playing sound: {sound_name}")
            except Exception as e:
                self.logger.error(f"Failed to play sound {sound_name}: {e}")
        else:
            self.logger.warning(f"Sound not found: {sound_name}")
    
    def set_volume(self, volume: float):
        """
        Set the volume for all sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0).
        """
        volume = max(0.0, min(1.0, volume))
        self.volume = volume
        
        for sound in self.sounds.values():
            sound.set_volume(volume)
        
        self.logger.info(f"Volume set to: {volume}")
    
    def get_volume(self) -> float:
        """
        Get the current volume level.
        
        Returns:
            Current volume level (0.0 to 1.0).
        """
        return self.volume
    
    def load_sound_file(self, filepath: str, sound_name: str):
        """
        Load a custom sound file.
        
        Args:
            filepath: Path to the sound file.
            sound_name: Name to assign to the sound.
        """
        if not self.mixer_initialized:
            self.logger.warning("Mixer not initialized, cannot load sound")
            return
        
        try:
            sound_path = Path(filepath)
            if sound_path.exists():
                sound = pygame.mixer.Sound(str(sound_path))
                sound.set_volume(self.volume)
                self.sounds[sound_name] = sound
                self.logger.info(f"Loaded custom sound: {sound_name} from {filepath}")
            else:
                self.logger.error(f"Sound file not found: {filepath}")
                
        except Exception as e:
            self.logger.error(f"Failed to load custom sound {filepath}: {e}")
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds."""
        if self.mixer_initialized:
            try:
                pygame.mixer.stop()
                self.logger.debug("Stopped all sounds")
            except Exception as e:
                self.logger.error(f"Failed to stop sounds: {e}")
    
    def pause_all_sounds(self):
        """Pause all currently playing sounds."""
        if self.mixer_initialized:
            try:
                pygame.mixer.pause()
                self.logger.debug("Paused all sounds")
            except Exception as e:
                self.logger.error(f"Failed to pause sounds: {e}")
    
    def unpause_all_sounds(self):
        """Unpause all currently playing sounds."""
        if self.mixer_initialized:
            try:
                pygame.mixer.unpause()
                self.logger.debug("Unpaused all sounds")
            except Exception as e:
                self.logger.error(f"Failed to unpause sounds: {e}")
    
    def get_available_sounds(self) -> list:
        """
        Get a list of available sound names.
        
        Returns:
            List of available sound names.
        """
        return list(self.sounds.keys())
    
    def is_sound_playing(self, sound_name: str) -> bool:
        """
        Check if a specific sound is currently playing.
        
        Args:
            sound_name: Name of the sound to check.
            
        Returns:
            True if the sound is playing, False otherwise.
        """
        if not self.mixer_initialized or sound_name not in self.sounds:
            return False
        
        try:
            # This is a simplified check - pygame doesn't provide direct access
            # to individual sound playing status, so we check if any sound is playing
            return pygame.mixer.get_busy()
        except Exception as e:
            self.logger.error(f"Failed to check sound playing status: {e}")
            return False
    
    def reload_sounds(self):
        """Reload all sound files."""
        self.logger.info("Reloading sounds...")
        self.sounds.clear()
        self._load_sounds()
    
    def close(self):
        """Close the audio manager and cleanup resources."""
        try:
            self.stop_all_sounds()
            
            if self.mixer_initialized:
                pygame.mixer.quit()
                self.mixer_initialized = False
            
            self.sounds.clear()
            self.logger.info("Audio manager closed")
            
        except Exception as e:
            self.logger.error(f"Error closing audio manager: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.close() 