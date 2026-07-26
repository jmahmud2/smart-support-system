"""
LLM integration module for the customer support workflow.
Handles communication with OpenRouter API with rate limit handling.
"""

import os
import time
import httpx
from dotenv import load_dotenv
from ..utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")

# Rate limiting configuration
RATE_LIMIT_RETRIES = 3
RATE_LIMIT_BACKOFF = 2  # seconds


def call_llm(prompt: str, retries: int = RATE_LIMIT_RETRIES) -> str:
    """
    Send a prompt to the OpenRouter API with rate limit handling.
    ALWAYS returns a string, never None.
    """
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY not set in .env file")
        return "Unable to process request: API key not configured."

    for attempt in range(retries):
        try:
            payload = {
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300,
            }

            logger.debug(f"Calling OpenRouter API (attempt {attempt + 1}/{retries})")

            response = httpx.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )

            if response.status_code == 429:
                wait_time = (attempt + 1) * RATE_LIMIT_BACKOFF
                logger.warning(f"Rate limited (attempt {attempt + 1}/{retries}), waiting {wait_time}s")
                if attempt < retries - 1:
                    time.sleep(wait_time)
                    continue
                return "Currently experiencing high demand. Please try again in a few moments."

            if response.status_code != 200:
                logger.error(f"API Error {response.status_code}: {response.text[:200]}")
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return "Unable to process request at this time."

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            if content is None:
                logger.warning("LLM returned None, using fallback")
                return "Unable to process request. Please try again later."
            
            logger.info(f"LLM response received ({len(content)} chars)")
            return content

        except httpx.TimeoutException:
            logger.warning(f"Timeout (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return "Request timed out. Please try again."

        except Exception as e:
            logger.error(f"LLM Exception: {e}")
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return "Unable to process request. Please try again later."

    logger.error("Maximum retry attempts exceeded")
    return "Unable to process request. Please try again later."


def get_available_models() -> list:
    """Get list of available free models on OpenRouter."""
    if not OPENROUTER_API_KEY:
        return []
    
    try:
        response = httpx.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=10.0
        )
        if response.status_code == 200:
            models = response.json().get("data", [])
            free_models = [m["id"] for m in models if "free" in m.get("id", "")]
            return free_models
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
    
    return []