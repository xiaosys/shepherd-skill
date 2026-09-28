#!/usr/bin/env python3
"""Prepare or execute a minimal TypeSafe Jev routing request for Shepherd."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
SCHEMA_VERSION = "shepherd-route-v1"
ALLOWED_STATE_FIELDS = {
    "goal",
    "authorization",
    "scope_clarity",
    "write_scope",
    "risk_signals",
    "acceptance_oracle",
    "task_dependencies",
    "runtime_constraints",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a Shepherd routing request for TypeSafe Jev. Dry-run is the "
            "default; --execute performs the network call."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON state file. Omit to read JSON from stdin.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Call the TypeSafe API; requires an environment or configured Keychain key.",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--model", default=MODEL)
    return parser.parse_args()


def load_state(path: Optional[Path]) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8") if path else sys.stdin.read()
    if not raw.strip():
        raise ValueError("input must contain a JSON object")
    state = json.loads(raw)
    if not isinstance(state, dict):
        raise ValueError("input must be a JSON object")

    unknown = sorted(set(state) - ALLOWED_STATE_FIELDS)
    if unknown:
        raise ValueError("unsupported state fields: " + ", ".join(unknown))
    if not isinstance(state.get("goal"), str) or not state["goal"].strip():
        raise ValueError("state.goal must be a non-empty string")
    return {"schema_version": SCHEMA_VERSION, **state}


def build_request(state: Dict[str, Any], model: str) -> Dict[str, Any]:
    return {
        "state": state,
        "model": model,
        "questions": {
            "route": {
                "type": "choice",
                "instructions": (
                    "Which Shepherd execution mode best fits this task state? "
                    "Judge only routing shape, not permission or completion."
                ),
                "criteria": {
                    "direct": (
                        "A simple answer, deterministic check, or tiny change where "
                        "delegation overhead is at least as large as the work."
                    ),
                    "routed": (
                        "One bounded non-trivial package with a clear owner and "
                        "acceptance oracle would benefit from one executor."
                    ),
                    "parallel": (
                        "At least two genuinely independent useful packages have "
                        "separate or read-only scopes and their own acceptance oracles."
                    ),
                    "planner_review": (
                        "The state is incomplete, ambiguous, high-risk, or lacks a "
                        "clear oracle, so a planner must decide before dispatch."
                    ),
                },
            },
            "complexity": {
                "type": "score",
                "instructions": (
                    "How difficult is it to isolate and verify the implementation "
                    "work described by this task state?"
                ),
                "criteria": [
                    "Deterministic check, answer, or tiny low-risk change.",
                    "Bounded implementation or investigation with a clear oracle.",
                    "High coupling, unknown root cause, shared contracts, or unclear verification.",
                ],
            },
        },
    }


def execute(request_body: Dict[str, Any], api_key: str, timeout: float) -> Dict[str, Any]:
    payload = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def load_api_key() -> str:
    """Load the API key from the environment or the macOS Keychain."""
    api_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if api_key:
        return api_key

    if sys.platform == "darwin":
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                "typesafe-ai",
                "-a",
                "api_key",
                "-w",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return ""


def main() -> int:
    args = parse_args()
    try:
        state = load_state(args.input)
        request_body = build_request(state, args.model)
        if not args.execute:
            json.dump(request_body, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            return 0

        api_key = load_api_key()
        if not api_key:
            raise ValueError(
                "set TYPESAFE_API_KEY or store a macOS Keychain item with "
                "service=typesafe-ai and account=api_key"
            )
        result = execute(request_body, api_key, args.timeout)
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except urllib.error.HTTPError as error:
        print(f"TypeSafe API returned HTTP {error.code}", file=sys.stderr)
    except urllib.error.URLError as error:
        print(f"TypeSafe API request failed: {error.reason}", file=sys.stderr)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"jev_route: {error}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
