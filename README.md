# quad-bench

Asks vision models whether a square is a square, rectangle, parallelogram, rhombus, kite, trapezium, all of the above, or none of the above.

Under inclusive definitions a square is all six shapes, so the expected answer is `g`. Under the exclusive trapezium definition (exactly one pair of parallel sides), `g` is wrong and `a` is the best answer. Disagreement between models is partly about which convention they pick.

## Run

```sh
uv run bench.py                      # all models in MODELS, 3 runs each, every image in images/
uv run bench.py --runs 5 --models anthropic/claude-opus-5.5 openai/gpt-6-sol
TYPESAFE_API_KEY=... uv run jev.py   # Jev is text-only, so the shape is described in text
```

Needs `OPENROUTER_API_KEY`. Drop real photos into `images/` to add cases. Raw responses go to `results.jsonl`.
Parser check: `uv run --with httpx python test_bench.py`.

## Results (2026-09-27, 3 runs each, about $1.30)

| model                         | square.png  | square_rotated45.png |
| ----------------------------- | ----------- | -------------------- |
| anthropic/claude-opus-5.5     | gx3         | gx3                  |
| anthropic/claude-fable-5.1    | gx3         | gx3                  |
| openai/gpt-6-sol              | gx3         | gx3                  |
| openai/gpt-6-luna             | ax3         | ax3                  |
| google/gemini-3.1-pro-preview | gx3         | gx3                  |
| google/gemini-3.8-flash       | gx3         | gx3                  |
| x-ai/grok-4.7                 | ax2 gx1     | gx3                  |
| qwen/qwen3.8-27b              | gx3         | ax1 ex1 gx1          |
| mistralai/mistral-medium-3-5  | ax2 gx1     | dx3                  |
| moonshotai/kimi-k3            | gx3         | gx2 ax1              |
| z-ai/glm-5v-turbo             | gx3         | gx2 dx1              |
| typesafe/jev-router           | gx2 ax1     | gx3                  |

`typesafe/jev-router` routes to other models, so its answers are not Jev's own. `meta/muse-spark-1.3` needs 18+ confirmation in OpenRouter settings.
