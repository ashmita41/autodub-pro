"""
Google Drive integration for cloud synchronization.
"""

import os
from typing import Dict, Any, List, Optional
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleDriveService:
    """
    Service for synchronizing files with Google Drive.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Google Drive service.
        
        Args:
            config: Configuration dictionary containing Google Drive settings
        """
        self.config = config
        self.credentials_file = config["google_drive"]["credentials_file"]
        self.folder_id = config["google_drive"]["folder_id"]
        self.enabled = config["google_drive"]["enabled"]
        
        self._drive = None
        self._initialized = False
        
        # Initialize if enabled and credentials file exists
        if self.enabled and os.path.exists(self.credentials_file):
            self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the Google Drive API client."""
        try:
            gauth = GoogleAuth()
            gauth.LoadCredentialsFile(self.credentials_file)
            
            if gauth.credentials is None:
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                gauth.Refresh()
            else:
                gauth.Authorize()
                
            gauth.SaveCredentialsFile(self.credentials_file)
            self._drive = GoogleDrive(gauth)
            self._initialized = True
            
        except Exception as e:
            print(f"Error initializing Google Drive: {e}")
            self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized with valid credentials."""
        return self._initialized and self._drive is not None
    
    def authenticate(self) -> bool:
        """
        Manually authenticate with Google Drive.
        
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            self._initialize()
            return self.is_initialized
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def list_files(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in a Google Drive folder.
        
        Args:
            folder_id: ID of the folder to list files from (defaults to configured folder_id)
            
        Returns:
            List of file dictionaries with 'id', 'title', etc.
        """
        if not self.is_initialized:
            raise ValueError("Google Drive not initialized")
            
        folder_id = folder_id or self.folder_id
        if not folder_id:
            raise ValueError("No folder ID specified")
            
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            file_list = self._drive.ListFile({'q': query}).GetList()
            return file_list
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def download_files(self, file_list: List[Dict[str, Any]], local_dir: str, max_threads: int = 5) -> List[str]:
        """
        Download files from Google Drive to a local directory.
        
        Args:
            file_list: List of file dictionaries to download
            local_dir: Local directory to download files to
            max_threads: Maximum number of concurrent downloads
            
        Returns:
            List of paths to downloaded files
        """
        if not self.is_initialized:
            raise ValueError("Google Drive not initialized")
            
        # Ensure local directory exists
        os.makedirs(local_dir, exist_ok=True)
        
        downloaded_files = []
        
        with ThreadPoolExecutor(max_threads) as executor:
            future_to_file = {
                executor.submit(self._download_file, file, local_dir): file 
                for file in file_list
            }
            
            for future in as_completed(future_to_file):
                file_path = future.result()
                if file_path:
                    downloaded_files.append(file_path)
        
        return downloaded_files
    
    def _download_file(self, file: Dict[str, Any], local_dir: str) -> Optional[str]:
        """
        Download a single file from Google Drive.
        
        Args:
            file: File dictionary
            local_dir: Local directory to download to
            
        Returns:
            Path to downloaded file or None if download failed
        """
        try:
            file_path = os.path.join(local_dir, file['title'])
            
            if not os.path.exists(file_path):
                file.GetContentFile(file_path)
                
            return file_path
            
        except Exception as e:
            print(f"Failed to download {file.get('title', '')}: {e}")
            return None
    
    def upload_files(self, file_paths: List[str], folder_id: Optional[str] = None, max_threads: int = 5) -> List[str]:
        """
        Upload files to Google Drive.
        
        Args:
            file_paths: List of local file paths to upload
            folder_id: ID of the folder to upload to (defaults to configured folder_id)
            max_threads: Maximum number of concurrent uploads
            
        Returns:
            List of IDs of uploaded files
        """
        if not self.is_initialized:
            raise ValueError("Google Drive not initialized")
            
        folder_id = folder_id or self.folder_id
        if not folder_id:
            raise ValueError("No folder ID specified")
            
        # Get existing files to avoid duplicates
        existing_files = {
            file['title']: file['id'] 
            for file in self.list_files(folder_id)
        }
        
        uploaded_file_ids = []
        
        with ThreadPoolExecutor(max_threads) as executor:
            future_to_file = {
                executor.submit(self._upload_file, file_path, folder_id, existing_files): file_path 
                for file_path in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_id = future.result()
                if file_id:
                    uploaded_file_ids.append(file_id)
        
        return uploaded_file_ids
    
    def _upload_file(self, file_path: str, folder_id: str, existing_files: Dict[str, str]) -> Optional[str]:
        """
        Upload a single file to Google Drive.
        
        Args:
            file_path: Path to local file
            folder_id: ID of the folder to upload to
            existing_files: Dictionary of existing files (title -> id)
            
        Returns:
            ID of uploaded file or None if upload failed
        """
        try:
            file_name = os.path.basename(file_path)
            
            # Check if file already exists
            if file_name in existing_files:
                # File exists, update it
                file = self._drive.CreateFile({'id': existing_files[file_name]})
            else:
                # File doesn't exist, create new
                file = self._drive.CreateFile({
                    'title': file_name,
                    'parents': [{'id': folder_id}]
                })
                
            file.SetContentFile(file_path)
            file.Upload()
            
            return file['id']
            
        except Exception as e:
            print(f"Failed to upload {file_path}: {e}")
            return None
    
    def delete_files(self, file_ids: List[str]) -> List[str]:
        """
        Delete files from Google Drive.
        
        Args:
            file_ids: List of file IDs to delete
            
        Returns:
            List of successfully deleted file IDs
        """
        if not self.is_initialized:
            raise ValueError("Google Drive not initialized")
            
        deleted_file_ids = []
        
        for file_id in file_ids:
            try:
                file = self._drive.CreateFile({'id': file_id})
                file.Delete()
                deleted_file_ids.append(file_id)
            except Exception as e:
                print(f"Failed to delete file {file_id}: {e}")
        
        return deleted_file_ids 