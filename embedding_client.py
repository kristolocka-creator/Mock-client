import sys
import time
import requests

API_URL = "http://127.0.0.1:8000/embed"

def get_embedding(text, retry_config):
    max_retries = retry_config["max_retries"]
    initial_delay = retry_config["initial_delay"]
    multiplier = retry_config["multiplier"]

    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                API_URL,
                json={"text": text},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return data["embedding"]

            if response.status_code in (400, 404):
                raise RuntimeError(
                    f"Permanent error: HTTP {response.status_code}"
                )

            if response.status_code in (429, 500, 503):
                raise RuntimeError(
                    f"Temporary error: HTTP {response.status_code}"
                )

            raise RuntimeError(
                f"Unexpected error: HTTP {response.status_code}"
            )

        except requests.exceptions.Timeout:
            error_message = "Request timeout"

        except RuntimeError as error:
            if (
                "Permanent error" in str(error)
                or "Unexpected error" in str(error)
            ):
                raise

            error_message = str(error)

        if attempt == max_retries:
            raise RuntimeError(
                f"Retries exhausted: {error_message}"
            )

        print(
    f"Attempt {attempt + 1} failed: {error_message}. "
    f"Retrying in {delay} seconds...",
    file=sys.stderr
)

        time.sleep(delay)
        delay *= multiplier