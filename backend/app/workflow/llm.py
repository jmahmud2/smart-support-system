"""
LLM integration module for the customer support workflow.
Handles communication with OpenRouter API using the Gemma 4 31B model.
"""

import os
import time
import json
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")


def call_llm(prompt: str, retries: int = 3) -> str:
    """
    Send a prompt to the OpenRouter API and return the response.

    Args:
        prompt: The input text to send to the LLM
        retries: Number of retry attempts for rate limiting

    Returns:
        The LLM's response as a string

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in .env file")

    for attempt in range(retries):
        try:
            # Prepare the request payload
            payload = {
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            }

            # Make the API request
            response = httpx.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Smart Support System"
                },
                json=payload,
                timeout=60.0,
            )

            # Log error details for debugging
            if response.status_code != 200:
                print(f"API Error {response.status_code}: {response.text}")
                if response.status_code == 400:
                    print("Request payload:", json.dumps(payload, indent=2))

            response.raise_for_status()

            # Extract and return the response
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            # Handle rate limiting with exponential backoff
            if e.response.status_code == 429 and attempt < retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            # Handle 400 Bad Request
            if e.response.status_code == 400:
                print(f"Bad Request: {e.response.text}")
                # Try without custom headers
                try:
                    fallback_response = httpx.post(
                        f"{OPENROUTER_BASE_URL}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "google/gemini-2.0-flash-exp:free",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 500,
                        },
                        timeout=60.0,
                    )
                    fallback_response.raise_for_status()
                    return fallback_response.json()["choices"][0]["message"]["content"]
                except Exception as fallback_error:
                    print(f"Fallback also failed: {fallback_error}")
                    raise

            raise

        except Exception as e:
            if attempt < retries - 1:
                print(f"Error occurred, retrying... ({attempt + 1}/{retries})")
                time.sleep(1)
                continue

            print(f"LLM Error after {retries} attempts: {e}")
            return "Unable to process your request at this time. Please try again later."

    return "Maximum retry attempts exceeded. Please try again later."