#!/usr/bin/env python3
"""
Simple LiteLLM key test script.

Usage (PowerShell):
    $env:LITELLM_API_KEY = "your_key_here"
    $env:LITELLM_BASE_URL = "https://your-litellm-endpoint"   # optional, default: http://localhost:4000
    python litellm_test.py --model gpt-4o-mini

Or create a .env file next to this script (or in current working directory):
    LITELLM_API_KEY=your_key_here
    LITELLM_BASE_URL=https://your-litellm-endpoint
    LITELLM_MODEL=gpt-4o
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


def load_dotenv_file() -> None:
    """Load simple KEY=VALUE pairs from .env into process environment."""
    candidates = [Path.cwd() / ".env", Path(__file__).resolve().parent / ".env"]
    dotenv_path = next((p for p in candidates if p.is_file()), None)
    if dotenv_path is None:
        return

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue

        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Support inline comments like: KEY="value"  # note
        if "#" in value:
            value = value.split("#", 1)[0].strip()

        if not key:
            continue

        # Strip optional surrounding quotes and tolerate uneven quoting.
        value = value.strip().strip('"').strip("'")

        if key not in os.environ:
            os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test a LiteLLM key with a chat completion call.")
    parser.add_argument("--model", default=os.getenv("LITELLM_MODEL", "gpt-4o"), help="Model name to test")
    parser.add_argument("--message", default="Say 'LiteLLM test successful' in one short sentence.", help="Prompt message")
    parser.add_argument(
        "--base-url",
        default=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        help="LiteLLM base URL (env: LITELLM_BASE_URL)",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("LITELLM_API_KEY", ""),
        help="LiteLLM API key (env: LITELLM_API_KEY)",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv_file()
    args = parse_args()

    if not args.api_key:
        print("Error: missing API key. Set LITELLM_API_KEY or pass --api-key.", file=sys.stderr)
        return 1

    url = args.base_url.rstrip("/") + "/v1/chat/completions"

    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.message}],
        "temperature": 0,
    }

    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {args.api_key}",
        "Content-Type": "application/json",
    }

    request = urllib.request.Request(url=url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code} {exc.reason}", file=sys.stderr)
        print(error_body, file=sys.stderr)
        return 2
    except urllib.error.URLError as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        return 3
    except json.JSONDecodeError:
        print("Received non-JSON response from server.", file=sys.stderr)
        return 4

    print("Request succeeded. Full response:")
    print(json.dumps(data, indent=2))

    try:
        assistant_text = data["choices"][0]["message"]["content"]
        print("\nAssistant reply:")
        print(assistant_text)
    except (KeyError, IndexError, TypeError):
        print("\nCould not extract assistant message from response.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
