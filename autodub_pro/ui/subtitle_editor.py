"""
Subtitle editor widget for AutoDub Pro.
"""

import os
from typing import List, Optional, Dict, Any, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenu, QToolBar, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, Slot, QItemSelectionModel
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QColor, QTextCursor, QBrush, QAction

import pysrt


class SubtitleEditorWidget(QWidget):
    """
    Widget for editing and managing subtitles.
    """
    
    # Signals
    subtitle_selected = Signal(float)  # Emits position in seconds when a subtitle is selected
    subtitle_changed = Signal(int, str)  # Emits index and new text when a subtitle is edited
    subtitle_timing_changed = Signal(int, float, float)  # Emits index, start and end time when timing is changed
    
    def __init__(self, parent=None):
        """
        Initialize the subtitle editor widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Instance variables
        self.subtitles: Optional[pysrt.SubRipFile] = None
        self.current_subtitle_index = -1
        self.modified = False
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create toolbar
        self.toolbar = QToolBar("Subtitle Toolbar")
        layout.addWidget(self.toolbar)
        
        # Add subtitle action
        self.add_subtitle_action = QAction("Add", self)
        self.add_subtitle_action.setToolTip("Add new subtitle")
        self.add_subtitle_action.triggered.connect(self.add_subtitle)
        self.toolbar.addAction(self.add_subtitle_action)
        
        # Delete subtitle action
        self.delete_subtitle_action = QAction("Delete", self)
        self.delete_subtitle_action.setToolTip("Delete selected subtitle")
        self.delete_subtitle_action.triggered.connect(self.delete_subtitle)
        self.toolbar.addAction(self.delete_subtitle_action)
        
        # Merge subtitles action
        self.merge_subtitles_action = QAction("Merge", self)
        self.merge_subtitles_action.setToolTip("Merge selected subtitles")
        self.merge_subtitles_action.triggered.connect(self.merge_subtitles)
        self.toolbar.addAction(self.merge_subtitles_action)
        
        # Split subtitle action
        self.split_subtitle_action = QAction("Split", self)
        self.split_subtitle_action.setToolTip("Split subtitle at cursor position")
        self.split_subtitle_action.triggered.connect(self.split_subtitle)
        self.toolbar.addAction(self.split_subtitle_action)
        
        self.toolbar.addSeparator()
        
        # Edit timing action
        self.edit_timing_action = QAction("Edit Timing", self)
        self.edit_timing_action.setToolTip("Edit subtitle timing")
        self.edit_timing_action.triggered.connect(self.edit_timing)
        self.toolbar.addAction(self.edit_timing_action)
        
        self.toolbar.addSeparator()
        
        # Create main splitter (subtitle list on top, editor below)
        self.main_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(self.main_splitter)
        
        # Subtitle table
        self.subtitle_table = QTableWidget()
        self.subtitle_table.setColumnCount(4)
        self.subtitle_table.setHorizontalHeaderLabels(["#", "Start", "End", "Text"])
        self.subtitle_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.subtitle_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.subtitle_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.subtitle_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.subtitle_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.subtitle_table.setAlternatingRowColors(True)
        
        # Editor area
        self.editor_widget = QWidget()
        editor_layout = QVBoxLayout(self.editor_widget)
        
        # Editor labels
        editor_header_layout = QHBoxLayout()
        self.current_subtitle_label = QLabel("No subtitle selected")
        editor_header_layout.addWidget(self.current_subtitle_label)
        
        self.timing_label = QLabel("")
        editor_header_layout.addWidget(self.timing_label)
        editor_header_layout.addStretch()
        
        # Editor text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Select a subtitle to edit")
        self.text_edit.setEnabled(False)
        
        # Add to editor layout
        editor_layout.addLayout(editor_header_layout)
        editor_layout.addWidget(self.text_edit)
        
        # Add to main splitter
        self.main_splitter.addWidget(self.subtitle_table)
        self.main_splitter.addWidget(self.editor_widget)
        
        # Set splitter sizes (60% table, 40% editor)
        self.main_splitter.setSizes([600, 400])
    
    def connect_signals(self):
        """Connect internal signals and slots."""
        self.subtitle_table.itemSelectionChanged.connect(self.selection_changed)
        self.text_edit.textChanged.connect(self.text_edited)
    
    def set_subtitles(self, subtitles: pysrt.SubRipFile):
        """
        Set the subtitles to edit.
        
        Args:
            subtitles: SubRipFile object
        """
        self.subtitles = subtitles
        self.current_subtitle_index = -1
        self.modified = False
        self.populate_table()
        self.update_editor()
    
    def get_subtitles(self) -> pysrt.SubRipFile:
        """
        Get the current subtitles.
        
        Returns:
            SubRipFile object
        """
        return self.subtitles
    
    def has_subtitles(self) -> bool:
        """
        Check if subtitles are loaded.
        
        Returns:
            True if subtitles are loaded, False otherwise
        """
        return self.subtitles is not None and len(self.subtitles) > 0
    
    def populate_table(self):
        """Populate the subtitle table with current subtitles."""
        self.subtitle_table.setRowCount(0)
        
        if not self.has_subtitles():
            return
        
        self.subtitle_table.setRowCount(len(self.subtitles))
        
        for i, sub in enumerate(self.subtitles):
            # Index
            index_item = QTableWidgetItem(str(i + 1))
            index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
            self.subtitle_table.setItem(i, 0, index_item)
            
            # Start time
            start_item = QTableWidgetItem(self.format_timestamp(sub.start))
            start_item.setFlags(start_item.flags() & ~Qt.ItemIsEditable)
            self.subtitle_table.setItem(i, 1, start_item)
            
            # End time
            end_item = QTableWidgetItem(self.format_timestamp(sub.end))
            end_item.setFlags(end_item.flags() & ~Qt.ItemIsEditable)
            self.subtitle_table.setItem(i, 2, end_item)
            
            # Text (first line only)
            text = sub.text.split('\n')[0]
            if len(sub.text.split('\n')) > 1:
                text += "..."
            text_item = QTableWidgetItem(text)
            text_item.setFlags(text_item.flags() & ~Qt.ItemIsEditable)
            self.subtitle_table.setItem(i, 3, text_item)
    
    def update_editor(self):
        """Update the editor with the current subtitle."""
        self.text_edit.setEnabled(False)
        
        if not self.has_subtitles() or self.current_subtitle_index < 0 or self.current_subtitle_index >= len(self.subtitles):
            self.current_subtitle_label.setText("No subtitle selected")
            self.timing_label.setText("")
            self.text_edit.clear()
            return
        
        sub = self.subtitles[self.current_subtitle_index]
        
        # Update labels
        self.current_subtitle_label.setText(f"Subtitle #{self.current_subtitle_index + 1}")
        self.timing_label.setText(f"{self.format_timestamp(sub.start)} - {self.format_timestamp(sub.end)}")
        
        # Update text editor
        self.text_edit.blockSignals(True)
        self.text_edit.setText(sub.text)
        self.text_edit.blockSignals(False)
        self.text_edit.setEnabled(True)
    
    def selection_changed(self):
        """Handle subtitle table selection changes."""
        selected_rows = self.subtitle_table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.current_subtitle_index = -1
            self.update_editor()
            return
        
        # Get the first selected row
        row = selected_rows[0].row()
        self.current_subtitle_index = row
        self.update_editor()
        
        # Emit signal with start time
        if self.has_subtitles() and 0 <= row < len(self.subtitles):
            start_seconds = (self.subtitles[row].start.hours * 3600 + 
                           self.subtitles[row].start.minutes * 60 + 
                           self.subtitles[row].start.seconds +
                           self.subtitles[row].start.milliseconds / 1000)
            self.subtitle_selected.emit(start_seconds)
    
    def text_edited(self):
        """Handle subtitle text edits."""
        if not self.has_subtitles() or self.current_subtitle_index < 0:
            return
        
        new_text = self.text_edit.toPlainText()
        self.subtitles[self.current_subtitle_index].text = new_text
        self.modified = True
        
        # Update the table cell
        text = new_text.split('\n')[0]
        if len(new_text.split('\n')) > 1:
            text += "..."
        self.subtitle_table.item(self.current_subtitle_index, 3).setText(text)
        
        # Emit signal
        self.subtitle_changed.emit(self.current_subtitle_index, new_text)
    
    def add_subtitle(self):
        """Add a new subtitle."""
        if not self.has_subtitles():
            QMessageBox.warning(self, "Warning", "No subtitles loaded")
            return
        
        # Determine where to add the new subtitle
        if self.current_subtitle_index >= 0:
            # Add after current subtitle
            current_sub = self.subtitles[self.current_subtitle_index]
            
            # Calculate new start and end times
            new_start = current_sub.end
            new_end = pysrt.SubRipTime(0, 0, 5, 0)  # 5 seconds after start
            
            # Ensure end time doesn't overlap with next subtitle
            if self.current_subtitle_index < len(self.subtitles) - 1:
                next_sub = self.subtitles[self.current_subtitle_index + 1]
                if (new_start.hours * 3600 + new_start.minutes * 60 + new_start.seconds + 5) > \
                   (next_sub.start.hours * 3600 + next_sub.start.minutes * 60 + next_sub.seconds):
                    new_end = next_sub.start
            
            # Create new subtitle
            new_sub = pysrt.SubRipItem(
                index=len(self.subtitles) + 1,
                start=new_start,
                end=new_end,
                text=""
            )
            
            # Insert after current subtitle
            self.subtitles.insert(self.current_subtitle_index + 1, new_sub)
            
            # Update indices
            self.update_indices()
            
            # Refresh table
            self.populate_table()
            
            # Select the new subtitle
            self.select_subtitle(self.current_subtitle_index + 1)
            
        else:
            # No subtitle selected, add at the end
            if len(self.subtitles) > 0:
                last_sub = self.subtitles[-1]
                new_start = last_sub.end
            else:
                new_start = pysrt.SubRipTime(0, 0, 0, 0)
            
            # Calculate end time (5 seconds after start)
            new_end = pysrt.SubRipTime(
                new_start.hours,
                new_start.minutes,
                new_start.seconds + 5,
                new_start.milliseconds
            )
            
            # Create new subtitle
            new_sub = pysrt.SubRipItem(
                index=len(self.subtitles) + 1,
                start=new_start,
                end=new_end,
                text=""
            )
            
            # Add to end
            self.subtitles.append(new_sub)
            
            # Refresh table
            self.populate_table()
            
            # Select the new subtitle
            self.select_subtitle(len(self.subtitles) - 1)
        
        self.modified = True
    
    def delete_subtitle(self):
        """Delete the selected subtitle."""
        if not self.has_subtitles() or self.current_subtitle_index < 0:
            return
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Delete Subtitle",
            f"Are you sure you want to delete subtitle #{self.current_subtitle_index + 1}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Delete the subtitle
        del self.subtitles[self.current_subtitle_index]
        
        # Update indices
        self.update_indices()
        
        # Refresh table
        self.populate_table()
        
        # Update selection
        if self.current_subtitle_index >= len(self.subtitles):
            self.current_subtitle_index = len(self.subtitles) - 1
        
        if self.current_subtitle_index >= 0:
            self.select_subtitle(self.current_subtitle_index)
        else:
            self.update_editor()
        
        self.modified = True
    
    def merge_subtitles(self):
        """Merge selected subtitles."""
        # Get selected rows
        selected_rows = self.subtitle_table.selectionModel().selectedRows()
        if len(selected_rows) < 2:
            QMessageBox.warning(self, "Warning", "Select at least two subtitles to merge")
            return
        
        # Sort rows in ascending order
        rows = sorted([row.row() for row in selected_rows])
        
        # Check if rows are consecutive
        for i in range(1, len(rows)):
            if rows[i] != rows[i-1] + 1:
                QMessageBox.warning(self, "Warning", "Can only merge consecutive subtitles")
                return
        
        # Get first and last subtitles
        first_sub = self.subtitles[rows[0]]
        last_sub = self.subtitles[rows[-1]]
        
        # Create merged text
        merged_text = ""
        for i, row in enumerate(rows):
            if i > 0:
                merged_text += "\n"
            merged_text += self.subtitles[row].text
        
        # Create merged subtitle
        merged_sub = pysrt.SubRipItem(
            index=first_sub.index,
            start=first_sub.start,
            end=last_sub.end,
            text=merged_text
        )
        
        # Replace first subtitle with merged subtitle
        self.subtitles[rows[0]] = merged_sub
        
        # Remove remaining subtitles (in reverse order to avoid index issues)
        for row in reversed(rows[1:]):
            del self.subtitles[row]
        
        # Update indices
        self.update_indices()
        
        # Refresh table
        self.populate_table()
        
        # Select the merged subtitle
        self.select_subtitle(rows[0])
        
        self.modified = True
    
    def split_subtitle(self):
        """Split the selected subtitle at cursor position."""
        if not self.has_subtitles() or self.current_subtitle_index < 0:
            return
        
        # Get text before and after cursor
        cursor = self.text_edit.textCursor()
        text = self.text_edit.toPlainText()
        cursor_pos = cursor.position()
        
        if cursor_pos <= 0 or cursor_pos >= len(text):
            QMessageBox.warning(self, "Warning", "Place the cursor where you want to split the subtitle")
            return
        
        # Get current subtitle
        current_sub = self.subtitles[self.current_subtitle_index]
        
        # Calculate timing
        start_ms = current_sub.start.ordinal
        end_ms = current_sub.end.ordinal
        duration_ms = end_ms - start_ms
        
        # Text before and after cursor
        text_before = text[:cursor_pos].strip()
        text_after = text[cursor_pos:].strip()
        
        if not text_before or not text_after:
            QMessageBox.warning(self, "Warning", "Cannot split at beginning or end of text")
            return
        
        # Calculate time proportional to cursor position in text
        split_ratio = cursor_pos / len(text)
        split_ms = start_ms + int(duration_ms * split_ratio)
        
        # Create split time
        split_time = pysrt.SubRipTime.from_ordinal(split_ms)
        
        # Update current subtitle
        current_sub.text = text_before
        current_sub.end = split_time
        
        # Create new subtitle for second part
        new_sub = pysrt.SubRipItem(
            index=current_sub.index + 1,
            start=split_time,
            end=current_sub.end,
            text=text_after
        )
        
        # Insert new subtitle
        self.subtitles.insert(self.current_subtitle_index + 1, new_sub)
        
        # Update indices
        self.update_indices()
        
        # Refresh table
        self.populate_table()
        
        # Select the first part
        self.select_subtitle(self.current_subtitle_index)
        
        self.modified = True
    
    def edit_timing(self):
        """Edit timing of the current subtitle."""
        if not self.has_subtitles() or self.current_subtitle_index < 0:
            return
        
        current_sub = self.subtitles[self.current_subtitle_index]
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Timing")
        
        # Create form layout
        layout = QFormLayout(dialog)
        
        # Start time input
        start_time_edit = QLineEdit(self.format_timestamp(current_sub.start))
        layout.addRow("Start Time (HH:MM:SS.mmm):", start_time_edit)
        
        # End time input
        end_time_edit = QLineEdit(self.format_timestamp(current_sub.end))
        layout.addRow("End Time (HH:MM:SS.mmm):", end_time_edit)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        # Show dialog
        if dialog.exec() == QDialog.Accepted:
            try:
                # Parse start time
                start_time_str = start_time_edit.text()
                start_time = self.parse_timestamp(start_time_str)
                
                # Parse end time
                end_time_str = end_time_edit.text()
                end_time = self.parse_timestamp(end_time_str)
                
                # Update subtitle
                current_sub.start = start_time
                current_sub.end = end_time
                
                # Update table
                self.subtitle_table.item(self.current_subtitle_index, 1).setText(self.format_timestamp(start_time))
                self.subtitle_table.item(self.current_subtitle_index, 2).setText(self.format_timestamp(end_time))
                
                # Update editor
                self.update_editor()
                
                # Emit signal
                start_seconds = (start_time.hours * 3600 + 
                               start_time.minutes * 60 + 
                               start_time.seconds +
                               start_time.milliseconds / 1000)
                end_seconds = (end_time.hours * 3600 + 
                             end_time.minutes * 60 + 
                             end_time.seconds +
                             end_time.milliseconds / 1000)
                self.subtitle_timing_changed.emit(self.current_subtitle_index, start_seconds, end_seconds)
                
                self.modified = True
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Invalid time format: {str(e)}")
    
    def update_indices(self):
        """Update subtitle indices to be sequential."""
        for i, sub in enumerate(self.subtitles):
            sub.index = i + 1
    
    def select_subtitle(self, index: int):
        """
        Select a subtitle by index.
        
        Args:
            index: Subtitle index
        """
        if 0 <= index < self.subtitle_table.rowCount():
            self.subtitle_table.selectRow(index)
    
    def highlight_subtitle_at_position(self, position_seconds: float):
        """
        Highlight the subtitle at the given playback position.
        
        Args:
            position_seconds: Playback position in seconds
        """
        if not self.has_subtitles():
            return
            
        # Find subtitle that contains the position
        found_index = -1
        
        for i, sub in enumerate(self.subtitles):
            start_seconds = (sub.start.hours * 3600 + 
                           sub.start.minutes * 60 + 
                           sub.start.seconds +
                           sub.start.milliseconds / 1000)
            end_seconds = (sub.end.hours * 3600 + 
                         sub.end.minutes * 60 + 
                         sub.end.seconds +
                         sub.end.milliseconds / 1000)
            
            if start_seconds <= position_seconds <= end_seconds:
                found_index = i
                break
        
        # If found and different from current selection, select it
        if found_index >= 0 and found_index != self.current_subtitle_index:
            self.select_subtitle(found_index)
    
    def format_timestamp(self, timestamp: pysrt.SubRipTime) -> str:
        """
        Format a timestamp for display.
        
        Args:
            timestamp: SubRipTime object
            
        Returns:
            Formatted timestamp string
        """
        return f"{timestamp.hours:02d}:{timestamp.minutes:02d}:{timestamp.seconds:02d}.{timestamp.milliseconds:03d}"
    
    def parse_timestamp(self, timestamp_str: str) -> pysrt.SubRipTime:
        """
        Parse a timestamp string.
        
        Args:
            timestamp_str: Timestamp string in format HH:MM:SS.mmm
            
        Returns:
            SubRipTime object
        """
        parts = timestamp_str.replace(',', '.').split(':')
        
        if len(parts) != 3:
            raise ValueError("Invalid timestamp format")
            
        hours = int(parts[0])
        minutes = int(parts[1])
        
        seconds_parts = parts[2].split('.')
        seconds = int(seconds_parts[0])
        
        milliseconds = 0
        if len(seconds_parts) > 1:
            # Ensure milliseconds are exactly 3 digits
            ms_str = seconds_parts[1].ljust(3, '0')[:3]
            milliseconds = int(ms_str)
        
        return pysrt.SubRipTime(hours, minutes, seconds, milliseconds) 