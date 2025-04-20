"""
Video processing utilities for AutoDub Pro.
"""

import os
import subprocess
import tempfile
from typing import Dict, Any, List, Tuple, Optional, Union
import pysrt
from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    TextClip, 
    CompositeVideoClip, 
    concatenate_videoclips
)


class VideoProcessor:
    """
    Class for handling video processing tasks.
    """
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        Initialize the video processor.
        
        Args:
            ffmpeg_path: Path to FFmpeg executable (optional)
        """
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"
    
    def load_video(self, video_path: str) -> Optional[VideoFileClip]:
        """
        Load a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            VideoFileClip object or None if loading fails
        """
        try:
            return VideoFileClip(video_path)
        except Exception as e:
            print(f"Error loading video: {e}")
            return None
    
    def save_video(self, video: VideoFileClip, output_path: str, codec: str = "libx264", audio_codec: str = "aac") -> bool:
        """
        Save a video to a file.
        
        Args:
            video: VideoFileClip object
            output_path: Path to save the video
            codec: Video codec to use
            audio_codec: Audio codec to use
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Export video
            video.write_videofile(
                output_path,
                codec=codec,
                audio_codec=audio_codec,
                threads=4
            )
            
            return True
            
        except Exception as e:
            print(f"Error saving video: {e}")
            return False
    
    def replace_audio(self, video: VideoFileClip, audio_path: str) -> VideoFileClip:
        """
        Replace the audio track in a video.
        
        Args:
            video: VideoFileClip object
            audio_path: Path to the audio file
            
        Returns:
            VideoFileClip with new audio
        """
        try:
            # Load audio
            audio = AudioFileClip(audio_path)
            
            # Set the audio of the clip
            video = video.set_audio(audio)
            
            return video
            
        except Exception as e:
            print(f"Error replacing audio: {e}")
            return video
    
    def add_subtitles_to_video(
        self, 
        video: VideoFileClip, 
        subtitles: Union[str, List[pysrt.SubRipItem]],
        font_size: int = 24,
        font_color: str = 'white',
        bg_color: str = 'black',
        bg_opacity: float = 0.6,
        position: Tuple[str, str] = ('center', 'bottom')
    ) -> VideoFileClip:
        """
        Add subtitles to a video.
        
        Args:
            video: VideoFileClip object
            subtitles: Path to SRT file or list of SubRipItems
            font_size: Font size for subtitles
            font_color: Font color for subtitles
            bg_color: Background color for subtitles
            bg_opacity: Background opacity for subtitles
            position: Position of subtitles ('center', 'bottom')
            
        Returns:
            VideoFileClip with subtitles
        """
        try:
            # Load subtitles if path is provided
            if isinstance(subtitles, str):
                subs = pysrt.open(subtitles, encoding='utf-8')
            else:
                subs = subtitles
                
            # Create TextClips for each subtitle and add them to the video
            subtitle_clips = []
            
            for sub in subs:
                # Convert start and end times to seconds
                start_time = (sub.start.hours * 3600 + 
                              sub.start.minutes * 60 + 
                              sub.start.seconds + 
                              sub.start.milliseconds / 1000)
                end_time = (sub.end.hours * 3600 + 
                            sub.end.minutes * 60 + 
                            sub.end.seconds + 
                            sub.end.milliseconds / 1000)
                
                # Create TextClip
                txt_clip = TextClip(
                    sub.text,
                    fontsize=font_size,
                    color=font_color,
                    bg_color=f"{bg_color}@{bg_opacity}",
                    size=(video.w * 0.9, None),
                    method='caption'
                )
                txt_clip = txt_clip.set_position(position).set_start(start_time).set_end(end_time)
                
                subtitle_clips.append(txt_clip)
            
            # Add subtitles to video
            return CompositeVideoClip([video] + subtitle_clips)
            
        except Exception as e:
            print(f"Error adding subtitles: {e}")
            return video
    
    def trim_video(self, video: VideoFileClip, start_time: float, end_time: Optional[float] = None) -> VideoFileClip:
        """
        Trim a video to a specific time range.
        
        Args:
            video: VideoFileClip object
            start_time: Start time in seconds
            end_time: End time in seconds (optional, defaults to end of video)
            
        Returns:
            Trimmed VideoFileClip
        """
        try:
            # Set end time to video duration if not provided
            if end_time is None:
                end_time = video.duration
                
            # Subclip the video
            return video.subclip(start_time, end_time)
            
        except Exception as e:
            print(f"Error trimming video: {e}")
            return video
    
    def concatenate_videos(self, video_clips: List[VideoFileClip]) -> Optional[VideoFileClip]:
        """
        Concatenate multiple videos into one.
        
        Args:
            video_clips: List of VideoFileClip objects
            
        Returns:
            Concatenated VideoFileClip or None if concatenation fails
        """
        try:
            if not video_clips:
                return None
                
            return concatenate_videoclips(video_clips)
            
        except Exception as e:
            print(f"Error concatenating videos: {e}")
            return None
    
    def export_video_with_subtitles_and_audio(
        self,
        video_path: str,
        subtitle_path: str,
        audio_path: str,
        output_path: str,
        font_size: int = 24,
        font_color: str = 'white',
        bg_color: str = 'black',
        bg_opacity: float = 0.6
    ) -> bool:
        """
        Export video with custom audio and subtitles.
        
        Args:
            video_path: Path to the video file
            subtitle_path: Path to the SRT file
            audio_path: Path to the audio file
            output_path: Path to save the output video
            font_size: Font size for subtitles
            font_color: Font color for subtitles
            bg_color: Background color for subtitles
            bg_opacity: Background opacity for subtitles
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Load video
            video = self.load_video(video_path)
            
            if video is None:
                return False
                
            # Replace audio
            video = self.replace_audio(video, audio_path)
            
            # Add subtitles
            video = self.add_subtitles_to_video(
                video,
                subtitle_path,
                font_size=font_size,
                font_color=font_color,
                bg_color=bg_color,
                bg_opacity=bg_opacity
            )
            
            # Save video
            return self.save_video(video, output_path)
            
        except Exception as e:
            print(f"Error exporting video: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get information about a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with video information
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-hide_banner"
            ]
            
            # FFmpeg outputs to stderr, not stdout
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse output
            info = {}
            
            # Extract duration
            duration_line = [line for line in result.stderr.split('\n') if "Duration" in line]
            if duration_line:
                duration_str = duration_line[0].split(',')[0].split('Duration:')[1].strip()
                hours, minutes, seconds = map(float, duration_str.split(':'))
                info['duration'] = hours * 3600 + minutes * 60 + seconds
                
            # Extract resolution
            resolution_line = [line for line in result.stderr.split('\n') if "Video:" in line]
            if resolution_line:
                resolution_part = resolution_line[0].split(',')
                for part in resolution_part:
                    if 'x' in part and any(c.isdigit() for c in part):
                        resolution = part.strip()
                        # Extract resolution (e.g., "1920x1080")
                        for word in resolution.split():
                            if 'x' in word and any(c.isdigit() for c in word):
                                width, height = map(int, word.split('x'))
                                info['width'] = width
                                info['height'] = height
                                break
            
            return info
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}
    
    def compress_video(self, input_path: str, output_path: str, crf: int = 23) -> bool:
        """
        Compress a video file.
        
        Args:
            input_path: Path to the input video file
            output_path: Path to save the compressed video
            crf: Constant Rate Factor (0-51, lower is higher quality)
            
        Returns:
            True if compression was successful, False otherwise
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-crf", str(crf),
                "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "128k",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return True
            
        except Exception as e:
            print(f"Error compressing video: {e}")
            return False 