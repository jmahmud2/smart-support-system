"""
LLM integration module for the customer support workflow.
Handles communication with OpenRouter API.
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


def call_llm(prompt: str, retries: int = 2) -> str:
    """
    Send a prompt to the OpenRouter API and return the response.
    ALWAYS returns a string, never None.
    """
    logger.info(f"LLM Call: {OPENROUTER_MODEL}")
    logger.debug(f"   Prompt: {prompt[:100]}...")

    if not OPENROUTER_API_KEY:
        logger.error("⚠️ OPENROUTER_API_KEY not set in .env file")
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
                logger.warning(f"Rate limited (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.info(f"   Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return "Service is busy. Please try again in a moment."

            if response.status_code != 200:
                logger.error(f"API Error {response.status_code}: {response.text[:200]}")
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return "Unable to process request at this time."

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info(f"LLM response received ({len(content)} chars)")
            logger.debug(f"   Response: {content[:100]}...")
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