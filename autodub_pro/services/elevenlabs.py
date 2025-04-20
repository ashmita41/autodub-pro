"""
ElevenLabs integration for text-to-speech voice generation.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List, Tuple, BinaryIO
import tempfile
import io

from autodub_pro.config import get_api_key


class ElevenLabsService:
    """
    Service for generating natural-sounding speech using ElevenLabs API.
    """
    
    # API endpoints
    BASE_URL = "https://api.elevenlabs.io/v1"
    TTS_ENDPOINT = "/text-to-speech/{voice_id}/with-timestamps"
    VOICES_ENDPOINT = "/voices"
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ElevenLabs service.
        
        Args:
            config: Configuration dictionary containing ElevenLabs credentials
        """
        self.config = config
        self.api_key = config["elevenlabs"]["api_key"]
        self.voice_id = config["elevenlabs"]["voice_id"]
        
        # Check if API key is available
        self._initialized = bool(self.api_key)
    
    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized with valid credentials."""
        return self._initialized
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """
        List available voices from ElevenLabs.
        
        Returns:
            List of voice dictionaries
        """
        if not self.is_initialized:
            raise ValueError("ElevenLabs API key not configured")
            
        url = f"{self.BASE_URL}{self.VOICES_ENDPOINT}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json().get("voices", [])
            
        except Exception as e:
            print(f"Error listing voices: {e}")
            return []
    
    def generate_speech(self, text: str, voice_id: Optional[str] = None) -> Tuple[bytes, Dict[str, Any]]:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (defaults to configured voice_id)
            
        Returns:
            Tuple of (audio_data, metadata) where metadata contains timing information
        """
        if not self.is_initialized:
            raise ValueError("ElevenLabs API key not configured")
            
        # Use provided voice_id or default
        voice_id = voice_id or self.voice_id
        if not voice_id:
            raise ValueError("No voice ID specified")
            
        url = f"{self.BASE_URL}{self.TTS_ENDPOINT.format(voice_id=voice_id)}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Extract timing metadata from response
            metadata = {}
            metadata_header = response.headers.get("Timestamps-Info")
            if metadata_header:
                metadata = json.loads(metadata_header)
            
            # Get binary audio data
            audio_data = response.content
            
            return audio_data, metadata
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            # Return empty data and metadata on error
            return bytes(), {}
    
    def generate_speech_to_file(self, text: str, output_path: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate speech from text and save to a file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the generated audio
            voice_id: Voice ID to use (defaults to configured voice_id)
            
        Returns:
            Metadata dictionary containing timing information
        """
        audio_data, metadata = self.generate_speech(text, voice_id)
        
        if audio_data:
            with open(output_path, 'wb') as f:
                f.write(audio_data)
                
        return metadata
    
    def generate_speech_to_buffer(self, text: str, voice_id: Optional[str] = None) -> Tuple[io.BytesIO, Dict[str, Any]]:
        """
        Generate speech from text and return as an in-memory buffer.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (defaults to configured voice_id)
            
        Returns:
            Tuple of (audio_buffer, metadata) where metadata contains timing information
        """
        audio_data, metadata = self.generate_speech(text, voice_id)
        
        buffer = io.BytesIO(audio_data)
        buffer.seek(0)
        
        return buffer, metadata
    
    def process_batch(self, subtitles: List[Dict[str, Any]], output_dir: str, voice_id: Optional[str] = None) -> Dict[int, Dict[str, Any]]:
        """
        Process a batch of subtitles, generating audio for each.
        
        Args:
            subtitles: List of subtitle dictionaries with 'index' and 'text' fields
            output_dir: Directory to save the generated audio files
            voice_id: Voice ID to use (defaults to configured voice_id)
            
        Returns:
            Dictionary mapping subtitle index to metadata
        """
        if not self.is_initialized:
            raise ValueError("ElevenLabs API key not configured")
            
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        metadata_dict = {}
        
        for subtitle in subtitles:
            try:
                text = subtitle['text']
                index = subtitle['index']
                
                # Generate output filename
                output_file = os.path.join(output_dir, f"{index:04d}.mp3")
                
                # Generate speech
                metadata = self.generate_speech_to_file(text, output_file, voice_id)
                
                # Store metadata with subtitle index
                metadata_dict[index] = metadata
                
            except Exception as e:
                print(f"Error processing subtitle {subtitle.get('index')}: {e}")
        
        return metadata_dict 