"""
OpenAI integration for subtitle translation and correction.
"""

import time
from typing import Dict, Any, List, Optional
import openai

from autodub_pro.config import get_api_key


class OpenAIService:
    """
    Service for translating and correcting subtitles using OpenAI GPT models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OpenAI service.
        
        Args:
            config: Configuration dictionary containing OpenAI credentials
        """
        self.config = config
        self.api_key = config["openai"]["api_key"]
        self.model = config["openai"]["model"]
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
            self._initialized = True
        else:
            self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized with valid credentials."""
        return self._initialized
    
    def translate_subtitle(self, text: str, from_lang: str, to_lang: str) -> str:
        """
        Translate subtitle text from one language to another.
        
        Args:
            text: Text to translate
            from_lang: Source language code
            to_lang: Target language code
            
        Returns:
            Translated text
        """
        if not self.is_initialized:
            raise ValueError("OpenAI API key not configured")
        
        # Define system prompt for translation
        system_prompt = f"""You are a professional translator specializing in {from_lang} to {to_lang} translation.
Your task is to translate the given text, maintaining the original meaning, tone, and cultural nuances.
Keep formatting like line breaks. Return only the translated text without explanations or notes."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error translating text: {e}")
            # On error, return original text
            return text
    
    def correct_subtitle(self, text: str, language: str) -> str:
        """
        Correct grammar, punctuation, and readability of subtitle text.
        
        Args:
            text: Text to correct
            language: Language code
            
        Returns:
            Corrected text
        """
        if not self.is_initialized:
            raise ValueError("OpenAI API key not configured")
        
        # Define system prompt for correction
        system_prompt = f"""You are a professional proofreader specializing in {language}.
Your task is to correct the given subtitle text, focusing on grammar, punctuation, and readability.
Ensure the text flows naturally and is suitable for dubbing.
Keep formatting like line breaks. Return only the corrected text without explanations or notes."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error correcting text: {e}")
            # On error, return original text
            return text
    
    def process_batch(self, subtitles: List[Dict[str, Any]], from_lang: str, to_lang: str) -> List[Dict[str, Any]]:
        """
        Process a batch of subtitles - translating and correcting them.
        
        Args:
            subtitles: List of subtitle dictionaries with 'text' field
            from_lang: Source language code
            to_lang: Target language code
            
        Returns:
            List of processed subtitles with translated and corrected text
        """
        if not self.is_initialized:
            raise ValueError("OpenAI API key not configured")
        
        processed_subtitles = []
        
        for subtitle in subtitles:
            try:
                # Translate the subtitle
                translated_text = self.translate_subtitle(subtitle['text'], from_lang, to_lang)
                
                # Correct the translated text
                corrected_text = self.correct_subtitle(translated_text, to_lang)
                
                # Create new subtitle with translated and corrected text
                processed_subtitle = subtitle.copy()
                processed_subtitle['original_text'] = subtitle['text']
                processed_subtitle['text'] = corrected_text
                
                processed_subtitles.append(processed_subtitle)
                
                # Add a short delay to avoid rate limits
                time.sleep(0.5)
                
            except openai.RateLimitError:
                # Handle rate limits by waiting and retrying
                print("Rate limit reached, waiting before retrying...")
                time.sleep(60)
                
                # Retry this subtitle
                try:
                    translated_text = self.translate_subtitle(subtitle['text'], from_lang, to_lang)
                    corrected_text = self.correct_subtitle(translated_text, to_lang)
                    
                    processed_subtitle = subtitle.copy()
                    processed_subtitle['original_text'] = subtitle['text']
                    processed_subtitle['text'] = corrected_text
                    
                    processed_subtitles.append(processed_subtitle)
                except Exception as e:
                    print(f"Error processing subtitle after retry: {e}")
                    # On error, keep original text
                    processed_subtitle = subtitle.copy()
                    processed_subtitle['original_text'] = subtitle['text']
                    processed_subtitles.append(processed_subtitle)
                    
            except Exception as e:
                print(f"Error processing subtitle: {e}")
                # On error, keep original text
                processed_subtitle = subtitle.copy()
                processed_subtitle['original_text'] = subtitle['text']
                processed_subtitles.append(processed_subtitle)
        
        return processed_subtitles 