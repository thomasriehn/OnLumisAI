#!/usr/bin/env python3
"""Baut Trainings-/Validierungsdatensätze aus kuratiertem Feedback (AP 5.2/5.3).

Quelle: app.feedback (rating='up', reviewed=true) + optionale JSONL-Dateien
(z. B. aus synth_qa.py). Ausgabe: Chat-Format-JSONL für TRL/Unsloth.

    python build_dataset.py --database-url postgresql://... --out data/ \
        [--extra data/synth.jsonl] [--val-ratio 0.1]
"""

import argparse
import asyncio
import json
import random
from pathlib import Path

SYSTEM_HINT = (
    "Du bist OnLumis, der interne Wissensassistent. Antworte präzise, "
    "auf Deutsch und belege Aussagen mit [n]-Zitaten."
)


def to_chat_example(question: str, answer: str) -> dict:
    """Ein kuratiertes Q/A-Paar im Chat-Format (Verhalten, nicht Wissen)."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_HINT},
            {"role": "user", "content": question.strip()},
            {"role": "assistant", "content": answer.strip()},
        ]
    }


def split_dataset(
    examples: list[dict], val_ratio: float, seed: int = 42
) -> tuple[list[dict], list[dict]]:
    """Deterministischer Train/Val-Split (mind. 1 Val-Beispiel ab 2 Beispielen)."""
    shuffled = examples[:]
    random.Random(seed).shuffle(shuffled)
    val_count = min(len(shuffled) - 1, max(1, round(len(shuffled) * val_ratio))) \
        if len(shuffled) > 1 else 0
    return shuffled[val_count:], shuffled[:val_count]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


async def load_curated_feedback(database_url: str) -> list[dict]:
    import asyncpg

    conn = await asyncpg.connect(database_url)
    try:
        rows = await conn.fetch(
            """
            SELECT m.content AS answer,
                   (SELECT um.content FROM app.messages um
                     WHERE um.conversation_id = m.conversation_id
                       AND um.role = 'user' AND um.created_at <= m.created_at
                     ORDER BY um.created_at DESC LIMIT 1) AS question
            FROM app.feedback f
            JOIN app.messages m ON m.id = f.message_id
            WHERE f.rating = 'up' AND f.reviewed
            ORDER BY f.created_at
            """
        )
    finally:
        await conn.close()
    return [
        to_chat_example(r["question"], r["answer"]) for r in rows if r["question"]
    ]


async def amain() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--out", type=Path, default=Path("data"))
    parser.add_argument("--extra", type=Path, action="append", default=[])
    parser.add_argument("--val-ratio", type=float, default=0.1)
    args = parser.parse_args()

    examples = await load_curated_feedback(args.database_url)
    for extra in args.extra:
        examples.extend(read_jsonl(extra))
    if not examples:
        raise SystemExit("Keine kuratierten Beispiele gefunden – erst Feedback freigeben.")

    train, val = split_dataset(examples, args.val_ratio)
    write_jsonl(args.out / "train.jsonl", train)
    write_jsonl(args.out / "val.jsonl", val)
    print(f"OK: {len(train)} Train / {len(val)} Val -> {args.out}/")


if __name__ == "__main__":
    asyncio.run(amain())
