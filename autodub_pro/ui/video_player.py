"""
Video player widget for AutoDub Pro.
"""

import os
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, 
    QLabel, QStyle, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QUrl, QTimer, Signal, Slot
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaFormat
from PySide6.QtMultimediaWidgets import QVideoWidget

from autodub_pro.core.video import VideoProcessor


class VideoPlayerWidget(QWidget):
    """
    Widget for video playback with custom controls.
    """
    
    # Signals
    playback_position_changed = Signal(float)
    playback_state_changed = Signal(bool)
    video_loaded = Signal(str)
    
    def __init__(self, parent=None):
        """
        Initialize the video player widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Instance variables
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)
        
        self.duration = 0
        self.position_update_timer = QTimer()
        self.position_update_timer.setInterval(50)  # 50ms interval for smoother updates
        self.position_update_timer.timeout.connect(self.update_position)
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Video container with frame
        video_container = QFrame()
        video_container.setFrameStyle(QFrame.StyledPanel)
        video_container_layout = QVBoxLayout(video_container)
        video_container_layout.setContentsMargins(0, 0, 0, 0)
        video_container_layout.addWidget(self.video_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Play/pause button
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setToolTip("Play/Pause (Space)")
        self.play_button.setFixedSize(32, 32)
        
        # Stop button
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.setToolTip("Stop")
        self.stop_button.setFixedSize(32, 32)
        
        # Mute button
        self.mute_button = QPushButton()
        self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_button.setToolTip("Mute/Unmute (M)")
        self.mute_button.setFixedSize(32, 32)
        self.mute_button.setCheckable(True)
        
        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100)
        self.position_slider.setFixedHeight(24)
        
        # Position labels
        self.position_label = QLabel("00:00:00")
        self.duration_label = QLabel("00:00:00")
        
        # Add widgets to controls layout
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.position_label)
        controls_layout.addWidget(self.position_slider)
        controls_layout.addWidget(self.duration_label)
        controls_layout.addWidget(self.mute_button)
        
        # Add components to main layout
        layout.addWidget(video_container)
        layout.addLayout(controls_layout)
        
        # Keyboard shortcuts
        self.play_pause_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.play_pause_shortcut.activated.connect(self.toggle_play_pause)
        
        self.mute_shortcut = QShortcut(QKeySequence("M"), self)
        self.mute_shortcut.activated.connect(self.toggle_mute)
    
    def connect_signals(self):
        """Connect internal signals and slots."""
        # Button connections
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop)
        self.mute_button.clicked.connect(self.toggle_mute)
        
        # Slider connections
        self.position_slider.sliderPressed.connect(self.position_slider_pressed)
        self.position_slider.sliderReleased.connect(self.position_slider_released)
        self.position_slider.valueChanged.connect(self.position_slider_value_changed)
        
        # Media player connections
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.playbackStateChanged.connect(self.playback_state_changed_handler)
        self.media_player.errorOccurred.connect(self.handle_error)
    
    def load_video(self, file_path: str) -> bool:
        """
        Load a video file into the player.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Reset player state
            self.stop()
            
            # Set new media source
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            
            # Update UI
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            
            # Emit signal
            self.video_loaded.emit(file_path)
            
            return True
            
        except Exception as e:
            print(f"Error loading video: {e}")
            return False
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start or resume playback."""
        self.media_player.play()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.position_update_timer.start()
        self.playback_state_changed.emit(True)
    
    def pause(self):
        """Pause playback."""
        self.media_player.pause()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.position_update_timer.stop()
        self.playback_state_changed.emit(False)
    
    def stop(self):
        """Stop playback."""
        self.media_player.stop()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.position_update_timer.stop()
        self.position_slider.setValue(0)
        self.position_label.setText("00:00:00")
        self.playback_state_changed.emit(False)
    
    def toggle_mute(self):
        """Toggle mute state."""
        muted = not self.audio_output.isMuted()
        self.audio_output.setMuted(muted)
        
        if muted:
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
    
    def seek_to_position(self, position_seconds: float):
        """
        Seek to a specific position in the video.
        
        Args:
            position_seconds: Position in seconds
        """
        if self.duration > 0:
            # Convert to milliseconds for QMediaPlayer
            position_ms = int(position_seconds * 1000)
            self.media_player.setPosition(position_ms)
            self.update_position()
    
    @Slot()
    def update_position(self):
        """Update position slider and label with current playback position."""
        position = self.media_player.position()
        
        # Update slider (blocking signals to prevent feedback loop)
        self.position_slider.blockSignals(True)
        if self.duration > 0:
            self.position_slider.setValue(int(position / self.duration * 100))
        else:
            self.position_slider.setValue(0)
        self.position_slider.blockSignals(False)
        
        # Update label
        position_seconds = position / 1000
        self.position_label.setText(self.format_time(position_seconds))
        
        # Emit signal with position in seconds
        self.playback_position_changed.emit(position_seconds)
    
    @Slot(int)
    def duration_changed(self, duration: int):
        """
        Handle duration changed signal from media player.
        
        Args:
            duration: Duration in milliseconds
        """
        self.duration = duration
        
        # Update duration label
        duration_seconds = duration / 1000
        self.duration_label.setText(self.format_time(duration_seconds))
    
    @Slot(QMediaPlayer.PlaybackState)
    def playback_state_changed_handler(self, state: QMediaPlayer.PlaybackState):
        """
        Handle playback state changed signal from media player.
        
        Args:
            state: New playback state
        """
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.position_update_timer.start()
            self.playback_state_changed.emit(True)
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.position_update_timer.stop()
            self.playback_state_changed.emit(False)
            
            # If stopped, reset position
            if state == QMediaPlayer.PlaybackState.StoppedState:
                self.position_slider.setValue(0)
                self.position_label.setText("00:00:00")
    
    def position_slider_pressed(self):
        """Handle position slider press event."""
        # Pause updates during scrubbing
        self.position_update_timer.stop()
    
    def position_slider_released(self):
        """Handle position slider release event."""
        # Convert slider value to position
        value = self.position_slider.value()
        position = int(value * self.duration / 100)
        
        # Set new position
        self.media_player.setPosition(position)
        
        # Resume updates if playing
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.position_update_timer.start()
    
    def position_slider_value_changed(self, value: int):
        """
        Handle position slider value changed event.
        
        Args:
            value: New slider value
        """
        # Only seek if user is dragging the slider
        if self.position_slider.isSliderDown():
            position = int(value * self.duration / 100)
            position_seconds = position / 1000
            self.position_label.setText(self.format_time(position_seconds))
    
    @Slot(QMediaPlayer.Error, str)
    def handle_error(self, error: QMediaPlayer.Error, error_string: str):
        """
        Handle media player errors.
        
        Args:
            error: Error code
            error_string: Error description
        """
        print(f"Media player error: {error} - {error_string}")
    
    def format_time(self, seconds: float) -> str:
        """
        Format time in seconds to HH:MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}" 