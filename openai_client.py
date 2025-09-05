import os
import time
import logging
from typing import Optional, Dict, Any
from openai import OpenAI, RateLimitError, APIError, APIConnectionError, APITimeoutError
import dash_mantine_components as dmc
from dash import html, dcc

from config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.max_retries = config.OPENAI_MAX_RETRIES
        self.base_delay = config.OPENAI_BASE_DELAY
        
    def _handle_api_error(self, error: Exception) -> str:
        """Handle different types of OpenAI API errors and return user-friendly messages."""
        if isinstance(error, RateLimitError):
            if "quota" in str(error).lower() or "insufficient_quota" in str(error).lower():
                return "⚠️ **API Quota Exceeded**\n\nYour OpenAI API quota has been exceeded. Please check your billing details and plan limits. You can:\n\n- Check your usage at [OpenAI Platform](https://platform.openai.com/usage)\n- Upgrade your plan if needed\n- Wait for your quota to reset\n\nFor now, I'll provide a basic analysis of your data instead."
            else:
                return "⚠️ **Rate Limit Exceeded**\n\nToo many requests to the AI service. Please wait a moment and try again."
        elif isinstance(error, APIConnectionError):
            return "⚠️ **Connection Error**\n\nUnable to connect to the AI service. Please check your internet connection and try again."
        elif isinstance(error, APITimeoutError):
            return "⚠️ **Request Timeout**\n\nThe AI service is taking too long to respond. Please try again with a simpler question."
        elif isinstance(error, APIError):
            return f"⚠️ **API Error**\n\nAn error occurred with the AI service: {str(error)}"
        else:
            return f"⚠️ **Unexpected Error**\n\nAn unexpected error occurred: {str(error)}"
    
    def _get_fallback_response(self, question: str, df_info: str) -> str:
        """Generate a fallback response when OpenAI API is unavailable."""
        return f"""**Basic Data Analysis** (AI service unavailable)

Based on your question: *"{question}"*

Here's what I can tell you about your dataset:
{df_info}

**Note:** For more detailed AI-powered insights, please ensure your OpenAI API key is valid and has sufficient quota."""
    
    def chat_completion(self, messages: list, model: str = None, **kwargs) -> Optional[str]:
        """
        Make a chat completion request with error handling and retry logic.
        
        Args:
            messages: List of message dictionaries
            model: Model to use for completion (defaults to config setting)
            **kwargs: Additional arguments for the completion request
            
        Returns:
            Response content or None if all retries failed
        """
        if model is None:
            model = config.OPENAI_MODEL
            
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
                
            except (RateLimitError, APIConnectionError, APITimeoutError) as e:
                logger.warning(f"API error on attempt {attempt + 1}: {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed: {e}")
                    return None
                    
            except APIError as e:
                logger.error(f"API error: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        return None
    
    def safe_chat_completion(self, messages: list, model: str = None, 
                           fallback_info: str = "", question: str = "", **kwargs) -> str:
        """
        Make a chat completion request with fallback response.
        
        Args:
            messages: List of message dictionaries
            model: Model to use for completion
            fallback_info: Information to include in fallback response
            question: User's question for fallback response
            **kwargs: Additional arguments for the completion request
            
        Returns:
            Response content or fallback response
        """
        try:
            response = self.chat_completion(messages, model, **kwargs)
            if response:
                return response
            else:
                return self._get_fallback_response(question, fallback_info)
                
        except Exception as e:
            error_msg = self._handle_api_error(e)
            logger.error(f"Error in safe_chat_completion: {e}")
            return error_msg

# Global instance
openai_client = OpenAIClient()

def create_error_notification(message: str) -> html.Div:
    """Create a styled error notification component."""
    return html.Div(
        [
            dmc.Alert(
                message,
                title="Service Notice",
                color="yellow",
                variant="light",
                style={"margin": "10px 0"}
            )
        ]
    )

def create_fallback_analysis(df_info: str, question: str) -> html.Div:
    """Create a fallback analysis when AI service is unavailable."""
    return html.Div(
        [
            dmc.Alert(
                "AI service is currently unavailable. Here's a basic analysis:",
                title="Limited Analysis Mode",
                color="blue",
                variant="light",
                style={"margin": "10px 0"}
            ),
            dcc.Markdown(
                openai_client._get_fallback_response(question, df_info),
                className="chat-item answer"
            )
        ]
    )
