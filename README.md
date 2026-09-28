# quad-bench

Asks vision models whether a square is a square, rectangle, parallelogram, rhombus, kite, all of the above, or none of the above.

A square is all five shapes, so the expected answer is `f`. The rotated image tests whether a model mistakes a tilted square for only a rhombus.

## The question

<img src="images/square.png" alt="A square" width="200">

Look at the shape in the image. Which of the following is it?

- [ ] a) square
- [ ] b) rectangle
- [ ] c) parallelogram
- [ ] d) rhombus
- [ ] e) kite
- [ ] f) all of the above
- [ ] g) none of the above

## Run

```sh
cp .env.sample .env                                  # fill in keys
uv run --env-file .env bench.py                      # all models in MODELS, 3 runs each, every image in images/
uv run --env-file .env bench.py --runs 5 --models anthropic/claude-opus-5.5 openai/gpt-6-sol
uv run --env-file .env jev.py                        # Jev is text-only, so the shape is described in text
```

Drop real photos into `images/` to add cases. Raw responses go to `results.jsonl`.
Parser check: `uv run --with httpx python test_bench.py`.

## Results (2026-09-28, 3 runs each, about $0.67)

| model                         | square.png  | square_rotated45.png |
| ----------------------------- | ----------- | -------------------- |
| anthropic/claude-opus-5.5     | fx3         | fx3                  |
| anthropic/claude-fable-5.1    | fx3         | fx3                  |
| openai/gpt-6-sol              | fx3         | fx3                  |
| openai/gpt-6-luna             | fx3         | fx3                  |
| google/gemini-3.1-pro-preview | fx3         | fx3                  |
| google/gemini-3.8-flash       | fx3         | fx3                  |
| x-ai/grok-4.7                 | fx3         | fx3                  |
| qwen/qwen3.8-27b              | fx3         | fx3                  |
| mistralai/mistral-medium-3-5  | fx3         | dx3                  |
| moonshotai/kimi-k3            | fx3         | fx3                  |
| z-ai/glm-5v-turbo             | fx3         | fx3                  |
| typesafe/jev-router           | fx3         | fx3                  |

`typesafe/jev-router` routes to other models, so its answers are not Jev's own. `meta/muse-spark-1.3` has no zero-data-retention endpoint, so it fails on accounts that require ZDR.
