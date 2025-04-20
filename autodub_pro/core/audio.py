"""
Audio processing utilities for AutoDub Pro.
"""

import os
import subprocess
import io
import tempfile
import wave
from typing import Dict, Any, List, Tuple, Optional, BinaryIO
import numpy as np
try:
    from pydub import AudioSegment
except ImportError as e:
    if "pyaudioop" in str(e):
        print("Warning: pyaudioop module not found. Audio processing will be limited.")
        # Create a dummy AudioSegment class to prevent crashes
        class AudioSegment:
            """Dummy AudioSegment class for when pydub is not available."""
            converter = None
            @classmethod
            def from_file(cls, *args, **kwargs):
                return cls()
            def export(self, *args, **kwargs):
                pass
            def __add__(self, other):
                return self
    else:
        raise
import soundfile as sf


class AudioProcessor:
    """
    Class for handling audio processing tasks.
    """
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        Initialize the audio processor.
        
        Args:
            ffmpeg_path: Path to FFmpeg executable (optional)
        """
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"
        
        # Ensure Pydub uses the correct FFmpeg path
        AudioSegment.converter = self.ffmpeg_path
    
    def extract_audio_from_video(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to the video file
            output_path: Path to save the extracted audio (optional)
            
        Returns:
            Path to the extracted audio file
        """
        if output_path is None:
            # Generate output path if not provided
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(tempfile.gettempdir(), f"{base_name}_audio.wav")
        
        try:
            # Run FFmpeg to extract audio
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # PCM 16-bit little-endian audio
                "-ar", "44100",  # 44.1 kHz sample rate
                "-ac", "2",  # 2 channels (stereo)
                "-y",  # Overwrite output file
                output_path
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return output_path
            
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return ""
    
    def load_audio(self, audio_path: str) -> Optional[AudioSegment]:
        """
        Load an audio file using Pydub.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            AudioSegment object or None if loading fails
        """
        try:
            # Detect format from file extension
            file_ext = os.path.splitext(audio_path)[1].lower().lstrip('.')
            
            if not file_ext:
                # Default to WAV if no extension
                file_ext = "wav"
            
            # Load audio file
            audio = AudioSegment.from_file(audio_path, format=file_ext)
            return audio
            
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None
    
    def save_audio(self, audio: AudioSegment, output_path: str) -> bool:
        """
        Save an audio segment to a file.
        
        Args:
            audio: AudioSegment object
            output_path: Path to save the audio
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Detect format from file extension
            file_ext = os.path.splitext(output_path)[1].lower().lstrip('.')
            
            if not file_ext:
                # Default to WAV if no extension
                file_ext = "wav"
                output_path += ".wav"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Export audio to file
            audio.export(output_path, format=file_ext)
            
            return True
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def convert_audio_format(self, input_path: str, output_path: str) -> bool:
        """
        Convert audio from one format to another.
        
        Args:
            input_path: Path to the input audio file
            output_path: Path to save the converted audio
            
        Returns:
            True if conversion was successful, False otherwise
        """
        try:
            # Load audio
            audio = self.load_audio(input_path)
            
            if audio is None:
                return False
            
            # Save in new format
            return self.save_audio(audio, output_path)
            
        except Exception as e:
            print(f"Error converting audio: {e}")
            return False
    
    def concatenate_audio_files(self, audio_paths: List[str], output_path: str) -> bool:
        """
        Concatenate multiple audio files into one.
        
        Args:
            audio_paths: List of paths to audio files
            output_path: Path to save the concatenated audio
            
        Returns:
            True if concatenation was successful, False otherwise
        """
        try:
            if not audio_paths:
                return False
            
            # Load the first audio file
            combined = self.load_audio(audio_paths[0])
            
            if combined is None:
                return False
            
            # Concatenate the rest
            for path in audio_paths[1:]:
                audio = self.load_audio(path)
                
                if audio is not None:
                    combined += audio
            
            # Save the combined audio
            return self.save_audio(combined, output_path)
            
        except Exception as e:
            print(f"Error concatenating audio: {e}")
            return False
    
    def adjust_audio_speed(self, audio: AudioSegment, speed_factor: float) -> AudioSegment:
        """
        Adjust the speed of an audio segment.
        
        Args:
            audio: AudioSegment object
            speed_factor: Factor to adjust speed by (e.g., 1.5 for 50% faster)
            
        Returns:
            Speed-adjusted AudioSegment
        """
        try:
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())
            
            # Get audio parameters
            channels = audio.channels
            sample_width = audio.sample_width
            
            # Reshape samples for processing if stereo
            if channels == 2:
                samples = samples.reshape((-1, 2))
            
            # Calculate new length
            new_length = int(len(samples) / speed_factor)
            
            # Resample audio
            indices = np.arange(0, len(samples), len(samples) / new_length)
            indices = indices.astype(np.int32)[:new_length]
            resampled = samples[indices]
            
            # Reshape back if necessary
            if channels == 2:
                resampled = resampled.flatten()
            
            # Create new AudioSegment
            new_audio = AudioSegment(
                resampled.tobytes(),
                frame_rate=audio.frame_rate,
                sample_width=sample_width,
                channels=channels
            )
            
            return new_audio
            
        except Exception as e:
            print(f"Error adjusting audio speed: {e}")
            return audio
    
    def add_silence(self, duration_ms: int) -> AudioSegment:
        """
        Create a silent audio segment.
        
        Args:
            duration_ms: Duration of silence in milliseconds
            
        Returns:
            Silent AudioSegment
        """
        return AudioSegment.silent(duration=duration_ms)
    
    def trim_audio(self, audio: AudioSegment, start_ms: int, end_ms: Optional[int] = None) -> AudioSegment:
        """
        Trim an audio segment.
        
        Args:
            audio: AudioSegment object
            start_ms: Start time in milliseconds
            end_ms: End time in milliseconds (optional, defaults to end of audio)
            
        Returns:
            Trimmed AudioSegment
        """
        if end_ms is None:
            end_ms = len(audio)
        
        return audio[start_ms:end_ms]
    
    def overlay_audio(self, base_audio: AudioSegment, overlay_audio: AudioSegment, position_ms: int) -> AudioSegment:
        """
        Overlay one audio segment on top of another.
        
        Args:
            base_audio: Base AudioSegment
            overlay_audio: AudioSegment to overlay
            position_ms: Position to overlay at in milliseconds
            
        Returns:
            Combined AudioSegment
        """
        return base_audio.overlay(overlay_audio, position=position_ms)
    
    def normalize_audio(self, audio: AudioSegment, target_dBFS: float = -20.0) -> AudioSegment:
        """
        Normalize audio to a target level.
        
        Args:
            audio: AudioSegment object
            target_dBFS: Target dB level
            
        Returns:
            Normalized AudioSegment
        """
        change_in_dBFS = target_dBFS - audio.dBFS
        return audio.apply_gain(change_in_dBFS)
    
    def change_audio_volume(self, audio: AudioSegment, volume_change_dB: float) -> AudioSegment:
        """
        Change the volume of an audio segment.
        
        Args:
            audio: AudioSegment object
            volume_change_dB: Volume change in dB (positive for louder, negative for quieter)
            
        Returns:
            Volume-adjusted AudioSegment
        """
        return audio.apply_gain(volume_change_dB)
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get the duration of an audio file in seconds.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration in seconds
        """
        try:
            audio = self.load_audio(audio_path)
            
            if audio is None:
                return 0.0
                
            return len(audio) / 1000.0
            
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0.0
    
    def silent_ffmpeg(self, command: List[str]) -> Tuple[bool, bytes, bytes]:
        """
        Run an FFmpeg command silently.
        
        Args:
            command: FFmpeg command as a list of strings
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Ensure FFmpeg is the first element
            if not command[0].endswith("ffmpeg"):
                command = [self.ffmpeg_path] + command
                
            # Run the command
            process = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True, process.stdout, process.stderr
            
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except Exception as e:
            print(f"Error running FFmpeg command: {e}")
            return False, b"", bytes(str(e), "utf-8") 