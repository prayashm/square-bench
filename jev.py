# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Ask TypeSafe's Jev the same question. Jev is text-only, so the shape is described in text."""

import json
import os

import httpx

OPTIONS = {
    "a": "square",
    "b": "rectangle",
    "c": "parallelogram",
    "d": "rhombus",
    "e": "kite",
    "f": "all of the above",
    "g": "none of the above",
}
SHAPES = ["square", "rectangle", "parallelogram", "rhombus", "kite"]

STATES = {
    "named": "The shape is a square.",
    "described": "A quadrilateral with four equal sides and four right angles.",
}

questions = {
    "mcq": {
        "type": "choice",
        "instructions": "Which of the options is the shape described in the state?",
        "criteria": {f"{k}) {v}": None for k, v in OPTIONS.items()},
    },
    # One yes/no per shape shows which inclusive definitions Jev applies.
    **{
        f"is_{s}": {
            "type": "noul",
            "instructions": f"Is the shape described in the state a {s}?",
        }
        for s in SHAPES
    },
}

for name, state in STATES.items():
    r = httpx.post(
        "https://api.typesafe.ai/v1/systemone",
        headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"},
        json={"model": "jev-latest", "state": state, "questions": questions},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    mcq = data["answers"]["mcq"]
    print(f"== {name}: {state}  ({data['model']})")
    print(f"choice: {mcq['choice']}  confidence: {mcq['confidence']:.2f}")
    print(
        "probabilities:",
        json.dumps({k: round(v, 3) for k, v in mcq["probabilities"].items()}),
    )
    for s in SHAPES:
        print(f"  is {s:<14} {data['answers'][f'is_{s}']['noul']:.2f}")
