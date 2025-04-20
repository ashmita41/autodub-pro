"""
AWS Transcribe integration for subtitle extraction.
"""

import os
import uuid
import time
from typing import Dict, Any, Optional
import boto3
from datetime import datetime

from autodub_pro.config import get_api_key


class AWSTranscriptionService:
    """
    Service for transcribing audio files using AWS Transcribe.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AWS Transcription service.
        
        Args:
            config: Configuration dictionary containing AWS credentials
        """
        self.config = config
        
        # Set up AWS credentials
        self.access_key = config["aws"]["access_key_id"]
        self.secret_key = config["aws"]["secret_access_key"]
        self.region = config["aws"]["region"]
        
        # Create AWS clients if credentials are available
        if self.access_key and self.secret_key:
            # Set environment variables for boto3
            os.environ['AWS_ACCESS_KEY_ID'] = self.access_key
            os.environ['AWS_SECRET_ACCESS_KEY'] = self.secret_key
            os.environ['AWS_DEFAULT_REGION'] = self.region
            
            # Initialize AWS clients
            self.s3_client = boto3.client('s3')
            self.transcribe_client = boto3.client('transcribe')
            self._initialized = True
        else:
            self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized with valid credentials."""
        return self._initialized
    
    def create_bucket_if_not_exists(self, bucket_name: str) -> None:
        """
        Create an S3 bucket if it doesn't exist.
        
        Args:
            bucket_name: Name of the S3 bucket
        """
        if not self.is_initialized:
            raise ValueError("AWS credentials not configured")
            
        # Check if bucket exists
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except:
            # Bucket doesn't exist, create it
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
    
    def upload_to_s3(self, audio_file_obj, bucket_name: str) -> str:
        """
        Upload an audio file to S3.
        
        Args:
            audio_file_obj: File-like object containing audio data
            bucket_name: Name of the S3 bucket
            
        Returns:
            S3 URI for the uploaded file
        """
        if not self.is_initialized:
            raise ValueError("AWS credentials not configured")
            
        # Ensure bucket exists
        self.create_bucket_if_not_exists(bucket_name)
        
        # Generate unique file name
        file_name = f"audio-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4()}.wav"
        
        # Upload file to S3
        self.s3_client.upload_fileobj(audio_file_obj, bucket_name, file_name)
        
        # Return S3 URI
        return f"s3://{bucket_name}/{file_name}"
    
    def start_transcription(self, audio_s3_uri: str, job_name: str, language_code: str = 'hi-IN') -> str:
        """
        Start an AWS Transcribe job.
        
        Args:
            audio_s3_uri: S3 URI for the audio file
            job_name: Name for the transcription job
            language_code: Language code for transcription
            
        Returns:
            Job name for the transcription job
        """
        if not self.is_initialized:
            raise ValueError("AWS credentials not configured")
            
        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': audio_s3_uri},
            MediaFormat='wav',
            LanguageCode=language_code,
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2
            }
        )
        
        return job_name
    
    def wait_for_transcription(self, job_name: str) -> None:
        """
        Wait for an AWS Transcribe job to complete.
        
        Args:
            job_name: Name of the transcription job
        """
        if not self.is_initialized:
            raise ValueError("AWS credentials not configured")
            
        while True:
            status = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
                
            time.sleep(5)
    
    def get_transcription_result(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of an AWS Transcribe job.
        
        Args:
            job_name: Name of the transcription job
            
        Returns:
            Dictionary containing transcription results or None if job failed
        """
        if not self.is_initialized:
            raise ValueError("AWS credentials not configured")
            
        try:
            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            
            if status == 'COMPLETED':
                transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                import requests
                result = requests.get(transcript_uri).json()
                return result
                
            return None
            
        except Exception as e:
            print(f"Error getting transcription result: {e}")
            return None
    
    def clear_s3_bucket(self, bucket_name: str) -> None:
        """
        Clear all objects from an S3 bucket.
        
        Args:
            bucket_name: Name of the S3 bucket
        """
        if not self.is_initialized:
            raise ValueError("AWS credentials not configured")
            
        try:
            # List objects in the bucket
            objects = self.s3_client.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' in objects:
                # Delete objects
                for obj in objects['Contents']:
                    self.s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                    
        except Exception as e:
            print(f"Error clearing S3 bucket: {e}") 