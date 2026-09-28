# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Ask several VLMs on OpenRouter to classify the quadrilateral in each image in images/."""

import argparse
import asyncio
import base64
import json
import os
import re
from collections import Counter
from pathlib import Path

import httpx

MODELS = [
    "anthropic/claude-opus-5.5",
    "anthropic/claude-fable-5.1",
    "openai/gpt-6-sol",
    "openai/gpt-6-luna",
    "google/gemini-3.1-pro-preview",
    "google/gemini-3.8-flash",
    "x-ai/grok-4.7",
    "qwen/qwen3.8-27b",
    "meta/muse-spark-1.3",
    "mistralai/mistral-medium-3-5",
    "moonshotai/kimi-k3",
    "z-ai/glm-5v-turbo",
    "typesafe/jev-router",
]

PROMPT = """Look at the shape in the image. Which of the following is it?

a) square
b) rectangle
c) parallelogram
d) rhombus
e) kite
f) trapezium
g) all of the above
h) none of the above

End your reply with a line of the form "Answer: <letter>"."""

ANSWER_RE = re.compile(r"answer:\s*\(?\**([a-h])\b", re.IGNORECASE)


def parse(text: str) -> str | None:
    if m := ANSWER_RE.findall(text):
        return m[-1].lower()
    stripped = text.strip().strip("().*").lower()
    return stripped if re.fullmatch(r"[a-h]", stripped) else None


async def ask(client, sem, model, image: Path, run: int) -> dict:
    b64 = base64.b64encode(image.read_bytes()).decode()
    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                ],
            }
        ],
    }
    async with sem:
        try:
            r = await client.post("/chat/completions", json=body)
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"] or ""
            return {
                "model": model,
                "image": image.name,
                "run": run,
                "answer": parse(text),
                "raw": text,
                "cost": data.get("usage", {}).get("cost"),
            }
        except (httpx.HTTPError, KeyError, IndexError) as e:
            detail = (
                e.response.text[:200]
                if isinstance(e, httpx.HTTPStatusError)
                else repr(e)
            )
            return {
                "model": model,
                "image": image.name,
                "run": run,
                "answer": None,
                "error": detail,
            }


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--models", nargs="+", default=MODELS)
    ap.add_argument("--out", default="results.jsonl")
    args = ap.parse_args()

    images = sorted(
        p
        for p in Path("images").iterdir()
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}
    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient(
        base_url="https://openrouter.ai/api/v1", headers=headers, timeout=300
    ) as client:
        results = await asyncio.gather(
            *(
                ask(client, sem, m, img, i)
                for m in args.models
                for img in images
                for i in range(args.runs)
            )
        )

    Path(args.out).write_text("".join(json.dumps(r) + "\n" for r in results))

    width = max(map(len, args.models))
    print(f"{'model':<{width}}  " + "  ".join(f"{img.name:<24}" for img in images))
    for m in args.models:
        cells = []
        for img in images:
            rs = [r for r in results if r["model"] == m and r["image"] == img.name]
            counts = Counter(
                r["answer"] or ("ERR" if "error" in r else "?") for r in rs
            )
            cells.append(f"{' '.join(f'{k}x{v}' for k, v in counts.most_common()):<24}")
        print(f"{m:<{width}}  " + "  ".join(cells))
    total = sum(r.get("cost") or 0 for r in results)
    print(f"\ncost: ${total:.4f}  raw responses: {args.out}")


if __name__ == "__main__":
    asyncio.run(main())
