"""
Main window UI for AutoDub Pro.
"""

import os
import sys
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QTabWidget, QStatusBar, QToolBar,
    QProgressBar, QSplitter, QLineEdit
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction, QKeySequence

from autodub_pro.ui.video_player import VideoPlayerWidget
from autodub_pro.ui.subtitle_editor import SubtitleEditorWidget
from autodub_pro.core.subtitle import SubtitleProcessor
from autodub_pro.core.audio import AudioProcessor
from autodub_pro.core.video import VideoProcessor
from autodub_pro.services.aws import AWSTranscriptionService
from autodub_pro.services.openai_service import OpenAIService
from autodub_pro.services.elevenlabs import ElevenLabsService
from autodub_pro.utils.helpers import find_ffmpeg, is_ffmpeg_available


class MainWindow(QMainWindow):
    """
    Main application window for AutoDub Pro.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the main window.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        
        self.config = config
        self.current_video_path = None
        self.current_subtitle_path = None
        self.current_audio_path = None
        
        # Initialize processing classes
        self.init_processors()
        
        # Initialize service integrations
        self.init_services()
        
        # Set up the UI
        self.init_ui()
        
        # Check for required dependencies
        self.check_dependencies()
    
    def init_processors(self):
        """Initialize processing components."""
        ffmpeg_path = find_ffmpeg()
        
        self.subtitle_processor = SubtitleProcessor()
        self.audio_processor = AudioProcessor(ffmpeg_path=ffmpeg_path)
        self.video_processor = VideoProcessor(ffmpeg_path=ffmpeg_path)
    
    def init_services(self):
        """Initialize external service integrations."""
        self.aws_service = AWSTranscriptionService(self.config)
        self.openai_service = OpenAIService(self.config)
        self.elevenlabs_service = ElevenLabsService(self.config)
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("AutoDub Pro")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.main_splitter)
        
        # Create video player widget
        self.video_player = VideoPlayerWidget()
        self.main_splitter.addWidget(self.video_player)
        
        # Create subtitle editor widget
        self.subtitle_editor = SubtitleEditorWidget()
        self.main_splitter.addWidget(self.subtitle_editor)
        
        # Set splitter sizes (60% video, 40% subtitle editor)
        self.main_splitter.setSizes([600, 400])
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add progress bar to status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Show initialization status
        self.status_bar.showMessage("Ready")
        
        # Connect signals and slots
        self.connect_signals()
    
    def create_toolbar(self):
        """Create the main toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)
        
        # Load video action
        self.load_video_action = QAction("Load Video", self)
        self.load_video_action.setShortcut(QKeySequence("Ctrl+O"))
        self.load_video_action.triggered.connect(self.load_video)
        self.toolbar.addAction(self.load_video_action)
        
        self.toolbar.addSeparator()
        
        # Extract subtitles action
        self.extract_subtitles_action = QAction("Extract Subtitles", self)
        self.extract_subtitles_action.triggered.connect(self.extract_subtitles)
        self.toolbar.addAction(self.extract_subtitles_action)
        
        # Load subtitles action
        self.load_subtitles_action = QAction("Load Subtitles", self)
        self.load_subtitles_action.triggered.connect(self.load_subtitles)
        self.toolbar.addAction(self.load_subtitles_action)
        
        # Save subtitles action
        self.save_subtitles_action = QAction("Save Subtitles", self)
        self.save_subtitles_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_subtitles_action.triggered.connect(self.save_subtitles)
        self.toolbar.addAction(self.save_subtitles_action)
        
        self.toolbar.addSeparator()
        
        # Translate subtitles action
        self.translate_subtitles_action = QAction("Translate Subtitles", self)
        self.translate_subtitles_action.triggered.connect(self.translate_subtitles)
        self.toolbar.addAction(self.translate_subtitles_action)
        
        self.toolbar.addSeparator()
        
        # Generate audio action
        self.generate_audio_action = QAction("Generate Audio", self)
        self.generate_audio_action.triggered.connect(self.generate_audio)
        self.toolbar.addAction(self.generate_audio_action)
        
        self.toolbar.addSeparator()
        
        # Export video action
        self.export_video_action = QAction("Export Video", self)
        self.export_video_action.triggered.connect(self.export_video)
        self.toolbar.addAction(self.export_video_action)
        
        self.toolbar.addSeparator()
        
        # Settings action
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.show_settings)
        self.toolbar.addAction(self.settings_action)
    
    def connect_signals(self):
        """Connect signals and slots."""
        # Connect video player signals
        self.video_player.playback_position_changed.connect(self.subtitle_editor.highlight_subtitle_at_position)
        
        # Connect subtitle editor signals
        self.subtitle_editor.subtitle_selected.connect(self.video_player.seek_to_position)
    
    def check_dependencies(self):
        """Check for required dependencies."""
        # Check for FFmpeg
        if not is_ffmpeg_available():
            QMessageBox.warning(
                self,
                "Missing Dependency",
                "FFmpeg not found. Some features will not work properly.\n\n"
                "Please install FFmpeg and make sure it's in your system PATH."
            )
        
        # Check AWS credentials
        if not self.aws_service.is_initialized:
            self.status_bar.showMessage("AWS credentials not configured")
        
        # Check OpenAI API key
        if not self.openai_service.is_initialized:
            self.status_bar.showMessage("OpenAI API key not configured")
        
        # Check ElevenLabs API key
        if not self.elevenlabs_service.is_initialized:
            self.status_bar.showMessage("ElevenLabs API key not configured")
    
    def load_video(self):
        """Open a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Load the video
        self.current_video_path = file_path
        self.video_player.load_video(file_path)
        
        # Update status
        self.status_bar.showMessage(f"Loaded video: {os.path.basename(file_path)}")
    
    def extract_subtitles(self):
        """Extract subtitles from the current video."""
        if not self.current_video_path:
            QMessageBox.warning(self, "Warning", "No video loaded")
            return
            
        if not self.aws_service.is_initialized:
            QMessageBox.warning(self, "Warning", "AWS credentials not configured")
            return
            
        # Extract audio from video
        temp_audio_path = self.audio_processor.extract_audio_from_video(self.current_video_path)
        
        if not temp_audio_path:
            QMessageBox.warning(self, "Error", "Failed to extract audio from video")
            return
            
        # TODO: Implement the actual AWS transcription process
        # For now, just show a message
        QMessageBox.information(
            self,
            "Extract Subtitles",
            "Subtitle extraction is not fully implemented yet.\n\n"
            "This would use AWS Transcribe to extract subtitles from the video."
        )
    
    def load_subtitles(self):
        """Load subtitles from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Subtitles",
            "",
            "Subtitle Files (*.srt);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Load the subtitles
        subtitles = self.subtitle_processor.load_srt(file_path)
        
        if not subtitles:
            QMessageBox.warning(self, "Error", "Failed to load subtitles")
            return
            
        # Set the subtitles in the editor
        self.subtitle_editor.set_subtitles(subtitles)
        self.current_subtitle_path = file_path
        
        # Update status
        self.status_bar.showMessage(f"Loaded subtitles: {os.path.basename(file_path)}")
    
    def save_subtitles(self):
        """Save subtitles to a file."""
        if not self.subtitle_editor.has_subtitles():
            QMessageBox.warning(self, "Warning", "No subtitles to save")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Subtitles",
            "",
            "Subtitle Files (*.srt);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Ensure the path has .srt extension
        if not file_path.lower().endswith('.srt'):
            file_path += '.srt'
            
        # Get the subtitles from the editor
        subtitles = self.subtitle_editor.get_subtitles()
        
        # Save the subtitles
        if self.subtitle_processor.save_srt(subtitles, file_path):
            self.current_subtitle_path = file_path
            self.status_bar.showMessage(f"Saved subtitles: {os.path.basename(file_path)}")
        else:
            QMessageBox.warning(self, "Error", "Failed to save subtitles")
    
    def translate_subtitles(self):
        """Translate subtitles using OpenAI."""
        if not self.subtitle_editor.has_subtitles():
            QMessageBox.warning(self, "Warning", "No subtitles to translate")
            return
            
        if not self.openai_service.is_initialized:
            QMessageBox.warning(self, "Warning", "OpenAI API key not configured")
            return
            
        # TODO: Implement the actual translation process
        # For now, just show a message
        QMessageBox.information(
            self,
            "Translate Subtitles",
            "Subtitle translation is not fully implemented yet.\n\n"
            "This would use OpenAI to translate the subtitles."
        )
    
    def generate_audio(self):
        """Generate audio from subtitles using ElevenLabs."""
        if not self.subtitle_editor.has_subtitles():
            QMessageBox.warning(self, "Warning", "No subtitles to generate audio from")
            return
            
        if not self.elevenlabs_service.is_initialized:
            QMessageBox.warning(self, "Warning", "ElevenLabs API key not configured")
            return
            
        # TODO: Implement the actual audio generation process
        # For now, just show a message
        QMessageBox.information(
            self,
            "Generate Audio",
            "Audio generation is not fully implemented yet.\n\n"
            "This would use ElevenLabs to generate audio from the subtitles."
        )
    
    def export_video(self):
        """Export the dubbed video."""
        if not self.current_video_path:
            QMessageBox.warning(self, "Warning", "No video loaded")
            return
            
        if not self.subtitle_editor.has_subtitles():
            QMessageBox.warning(self, "Warning", "No subtitles available")
            return
            
        if not self.current_audio_path:
            # No audio has been generated yet
            reply = QMessageBox.question(
                self,
                "Export Video",
                "No audio has been generated yet. Do you want to export with subtitles only?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
                
        # Get output file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video",
            "",
            "Video Files (*.mp4);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Ensure the path has .mp4 extension
        if not file_path.lower().endswith('.mp4'):
            file_path += '.mp4'
            
        # TODO: Implement the actual video export process
        # For now, just show a message
        QMessageBox.information(
            self,
            "Export Video",
            "Video export is not fully implemented yet.\n\n"
            "This would export the video with the generated audio and subtitles."
        )
    
    def show_settings(self):
        """Show the settings dialog."""
        # TODO: Implement settings dialog
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog is not implemented yet."
        )
    
    def closeEvent(self, event):
        """Handle the window close event."""
        # Clean up resources
        self.video_player.stop()
        event.accept() 