"""
Subtitle processing utilities for AutoDub Pro.
"""

import os
import json
from typing import Dict, Any, List, Tuple, Optional
import pysrt
from datetime import timedelta


class SubtitleProcessor:
    """
    Class for handling subtitle processing tasks.
    """
    
    def __init__(self):
        """Initialize the subtitle processor."""
        pass
    
    def load_srt(self, file_path: str) -> List[pysrt.SubRipItem]:
        """
        Load subtitles from an SRT file.
        
        Args:
            file_path: Path to the SRT file
            
        Returns:
            List of SubRipItems
        """
        try:
            return pysrt.open(file_path, encoding='utf-8')
        except Exception as e:
            print(f"Error loading SRT file: {e}")
            return []
    
    def save_srt(self, subtitles: List[pysrt.SubRipItem], file_path: str) -> bool:
        """
        Save subtitles to an SRT file.
        
        Args:
            subtitles: List of SubRipItems
            file_path: Path to save the SRT file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            subtitle_file = pysrt.SubRipFile(items=subtitles)
            subtitle_file.save(file_path, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error saving SRT file: {e}")
            return False
    
    def aws_result_to_srt(self, aws_result: Dict[str, Any]) -> List[pysrt.SubRipItem]:
        """
        Convert AWS Transcribe result to SRT format.
        
        Args:
            aws_result: AWS Transcribe result dictionary
            
        Returns:
            List of SubRipItems
        """
        items = []
        
        try:
            # Extract the transcript items from AWS result
            transcript_items = aws_result.get('results', {}).get('items', [])
            
            # Group items by speaker and time
            segments = self._group_transcript_items(transcript_items)
            
            # Convert segments to SubRipItems
            for i, segment in enumerate(segments):
                start_time = segment['start_time']
                end_time = segment['end_time']
                text = segment['text']
                
                # Create a SubRipItem
                item = pysrt.SubRipItem(
                    index=i+1,
                    start=self._seconds_to_subrip_time(start_time),
                    end=self._seconds_to_subrip_time(end_time),
                    text=text
                )
                
                items.append(item)
            
            return items
            
        except Exception as e:
            print(f"Error converting AWS result to SRT: {e}")
            return []
    
    def _group_transcript_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group AWS transcript items into continuous speech segments.
        
        Args:
            items: List of AWS transcript items
            
        Returns:
            List of segment dictionaries with start_time, end_time, and text
        """
        segments = []
        current_segment = None
        
        for item in items:
            # Skip non-pronunciation items
            if item.get('type') != 'pronunciation':
                continue
                
            # Get start and end time
            start_time = float(item.get('start_time', 0))
            end_time = float(item.get('end_time', 0))
            
            # Get the content
            content = item.get('alternatives', [{}])[0].get('content', '')
            
            # Create a new segment if we don't have one
            if current_segment is None:
                current_segment = {
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': content
                }
            # Check if the new item is part of the current segment (less than 0.5s gap)
            elif start_time - current_segment['end_time'] < 0.5:
                # Add a space and the content to the current segment
                current_segment['text'] += ' ' + content
                current_segment['end_time'] = end_time
            # Otherwise, finish the current segment and start a new one
            else:
                segments.append(current_segment)
                current_segment = {
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': content
                }
        
        # Add the last segment if we have one
        if current_segment is not None:
            segments.append(current_segment)
        
        return segments
    
    def _seconds_to_subrip_time(self, seconds: float) -> pysrt.SubRipTime:
        """
        Convert seconds to SubRipTime.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            SubRipTime object
        """
        td = timedelta(seconds=seconds)
        
        # Extract hours, minutes, seconds, and milliseconds
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int(td.microseconds / 1000)
        
        return pysrt.SubRipTime(hours, minutes, seconds, milliseconds)
    
    def crop_subtitle(self, subtitle: pysrt.SubRipItem, is_end: bool = True, position: Optional[float] = None) -> pysrt.SubRipItem:
        """
        Crop a subtitle at a specific position.
        
        Args:
            subtitle: Subtitle to crop
            is_end: Whether to crop the end (True) or start (False)
            position: Position in seconds to crop at (optional)
            
        Returns:
            Cropped subtitle
        """
        if position is None:
            return subtitle
            
        position_time = self._seconds_to_subrip_time(position)
        
        new_subtitle = subtitle.copy()
        
        if is_end:
            new_subtitle.end = position_time
        else:
            new_subtitle.start = position_time
        
        return new_subtitle
    
    def merge_subtitles(self, subtitles: List[pysrt.SubRipItem], indices: List[int]) -> Tuple[pysrt.SubRipItem, List[int]]:
        """
        Merge multiple subtitles into one.
        
        Args:
            subtitles: List of subtitles
            indices: List of indices to merge
            
        Returns:
            Tuple of (merged subtitle, removed indices)
        """
        if not indices or len(indices) < 2:
            return None, []
            
        # Sort indices
        indices = sorted(indices)
        
        # Get subtitles to merge
        to_merge = [subtitles[i] for i in indices if 0 <= i < len(subtitles)]
        
        if not to_merge:
            return None, []
            
        # Create merged subtitle
        merged = to_merge[0].copy()
        merged.end = to_merge[-1].end
        merged.text = ' '.join([sub.text for sub in to_merge])
        
        return merged, indices[1:]
    
    def split_subtitle(self, subtitle: pysrt.SubRipItem, position: float) -> Tuple[pysrt.SubRipItem, pysrt.SubRipItem]:
        """
        Split a subtitle at a specific position.
        
        Args:
            subtitle: Subtitle to split
            position: Position in seconds to split at
            
        Returns:
            Tuple of (first part, second part)
        """
        position_time = self._seconds_to_subrip_time(position)
        
        # Check if position is within subtitle duration
        if not (subtitle.start.ordinal <= position_time.ordinal <= subtitle.end.ordinal):
            return subtitle, None
            
        # Create first part
        first_part = subtitle.copy()
        first_part.end = position_time
        
        # Create second part
        second_part = subtitle.copy()
        second_part.start = position_time
        
        return first_part, second_part
    
    def set_subtitle_timing(self, subtitle: pysrt.SubRipItem, start: Optional[float] = None, end: Optional[float] = None) -> pysrt.SubRipItem:
        """
        Set the start and/or end time of a subtitle.
        
        Args:
            subtitle: Subtitle to modify
            start: New start time in seconds (optional)
            end: New end time in seconds (optional)
            
        Returns:
            Modified subtitle
        """
        new_subtitle = subtitle.copy()
        
        if start is not None:
            new_subtitle.start = self._seconds_to_subrip_time(start)
            
        if end is not None:
            new_subtitle.end = self._seconds_to_subrip_time(end)
            
        return new_subtitle
    
    def get_subtitle_duration(self, subtitle: pysrt.SubRipItem) -> float:
        """
        Get the duration of a subtitle in seconds.
        
        Args:
            subtitle: Subtitle to get duration of
            
        Returns:
            Duration in seconds
        """
        return (subtitle.end.ordinal - subtitle.start.ordinal) / 1000.0
    
    def format_timestamp(self, timestamp: pysrt.SubRipTime) -> str:
        """
        Format a timestamp for display.
        
        Args:
            timestamp: Timestamp to format
            
        Returns:
            Formatted timestamp string (HH:MM:SS.mmm)
        """
        return f"{timestamp.hours:02d}:{timestamp.minutes:02d}:{timestamp.seconds:02d}.{timestamp.milliseconds:03d}" 