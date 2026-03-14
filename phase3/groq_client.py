"""Groq API client with retry logic and error handling."""
import logging
import time
import json
from typing import Optional, Any
from groq import Groq

import sys
sys.path.append('..')
from common.models import GroqConfig

logger = logging.getLogger(__name__)


class GroqAPIError(Exception):
    """Exception raised when Groq API call fails."""
    pass


class AuthenticationError(Exception):
    """Exception raised when API authentication fails."""
    pass


def _call_gemini_fallback(messages: list[dict], max_tokens: int = 2000) -> str:
    """Call Gemini API as fallback when Groq is rate limited."""
    try:
        import google.generativeai as genai
        import sys, os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from common.config import Config

        # Use Config which reads from Streamlit secrets or env vars
        gemini_keys = Config.GEMINI_API_KEYS

        if not gemini_keys:
            raise Exception("No Gemini API keys configured")

        # Build prompt from messages
        prompt = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        )

        last_err = None
        for key in gemini_keys:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens)
                )
                return response.text
            except Exception as e:
                last_err = e
                logger.warning(f"Gemini key failed: {e}")
                continue

        raise Exception(f"All Gemini keys failed: {last_err}")
    except ImportError:
        raise Exception("google-generativeai not installed. Run: pip install google-generativeai")


class GroqClient:
    """Client for interacting with Groq LLM API."""
    
    def __init__(self, config: GroqConfig):
        """Initialize Groq client with configuration."""
        self.config = config
        self.model = config.model
        self.timeout = config.timeout
        self.max_retries = config.max_retries
        
        # Support multiple API keys for rotation
        import os, sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from common.config import Config
        self.api_keys = Config.GROQ_API_KEYS if Config.GROQ_API_KEYS else [config.api_key]
        self.api_keys = [k for k in self.api_keys if k]
        
        if not self.api_keys:
            raise AuthenticationError("Groq API key is required. Set GROQ_API_KEY in .env file.")
        
        self.current_key_index = 0
        self.client = Groq(api_key=self.api_keys[0])
        logger.info(f"Groq client initialized with model: {self.model}, {len(self.api_keys)} key(s)")

    def _rotate_key(self):
        """Rotate to the next available API key."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.client = Groq(api_key=self.api_keys[self.current_key_index])
        logger.info(f"Rotated to API key #{self.current_key_index + 1}")
    
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send chat completion request to Groq API with retry logic.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        
        Returns:
            Response content as string
        
        Raises:
            GroqAPIError: If API call fails after retries
            AuthenticationError: If API key is invalid
        """
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Groq API call attempt {attempt + 1}/{self.max_retries}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout
                )
                
                content = response.choices[0].message.content
                logger.info(f"Groq API call successful (model: {self.model})")
                return content
            
            except Exception as e:
                error_msg = str(e)
                
                # Check for authentication errors
                if 'authentication' in error_msg.lower() or 'api key' in error_msg.lower():
                    raise AuthenticationError(f"Invalid Groq API key. Please check your GROQ_API_KEY in .env file.")
                
                # Check for rate limiting
                if '429' in error_msg or 'rate limit' in error_msg.lower():
                    if len(self.api_keys) > 1:
                        self._rotate_key()
                        logger.warning(f"Rate limited — rotated to key #{self.current_key_index + 1}")
                        continue
                    elif attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # All Groq keys exhausted — fall back to Gemini
                        logger.warning("Groq rate limited on all keys — falling back to Gemini...")
                        try:
                            return _call_gemini_fallback(messages, max_tokens or 2000)
                        except Exception as gem_err:
                            raise GroqAPIError(f"Groq rate limited and Gemini fallback failed: {gem_err}")
                
                # Last attempt failed
                if attempt == self.max_retries - 1:
                    logger.error(f"Groq API call failed after {self.max_retries} attempts: {error_msg}")
                    raise GroqAPIError(
                        f"Failed to call Groq API after {self.max_retries} attempts. "
                        f"Error: {error_msg}. Please check your internet connection and API key."
                    )
                
                # Retry with exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {error_msg}")
                time.sleep(wait_time)
        
        raise GroqAPIError("Unexpected error in Groq API call")
    
    def parse_json_response(self, response: str) -> dict[str, Any]:
        """
        Parse JSON response from LLM, handling markdown code blocks.
        
        Args:
            response: Raw response string from LLM
        
        Returns:
            Parsed JSON as dictionary
        
        Raises:
            ValueError: If response cannot be parsed as JSON
        """
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        elif response.startswith('```'):
            response = response[3:]
        
        if response.endswith('```'):
            response = response[:-3]
        
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
