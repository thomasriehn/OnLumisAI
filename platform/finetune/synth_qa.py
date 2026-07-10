#!/usr/bin/env python3
"""Synthetische QA-Paare aus allgemein freigegebenen Dokumenten (AP 5.5).

ACL-Wächter (ADR-9): verwendet ausschließlich Chunks von Dokumenten, deren
acl_groups die Gruppe 'all-users' enthält – nichts Vertrauliches gelangt in
Trainingsdaten. Generierung über den lokalen vLLM-Chat-Endpoint.

    python synth_qa.py --database-url $DATABASE_URL \
        --chat-base-url http://localhost:8001/v1 --limit 200 --out data/synth.jsonl
"""

import argparse
import asyncio
import json
from pathlib import Path

GENERATE_PROMPT = """\
Erzeuge aus dem folgenden internen Dokumentauszug GENAU EIN Frage-Antwort-Paar
für das Training eines Wissensassistenten. Die Frage soll so klingen, wie ein
Mitarbeitender sie stellen würde; die Antwort knapp, korrekt und mit dem
Platzhalter-Zitat [1] belegt.

Auszug:
{chunk}

Antworte NUR als JSON: {{"question": "...", "answer": "..."}}\
"""


async def amain() -> None:
    import asyncpg
    import httpx

    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--chat-base-url", required=True)
    parser.add_argument("--chat-model", default="chat")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--out", type=Path, default=Path("data/synth.jsonl"))
    args = parser.parse_args()

    conn = await asyncpg.connect(args.database_url)
    try:
        rows = await conn.fetch(
            """
            SELECT c.content FROM knowledge.chunks c
            JOIN knowledge.documents d ON d.id = c.document_id
            WHERE d.deleted_at IS NULL
              AND 'all-users' = ANY(d.acl_groups)   -- ACL-Wächter
            ORDER BY c.id LIMIT $1
            """,
            args.limit,
        )
    finally:
        await conn.close()

    examples: list[dict] = []
    async with httpx.AsyncClient(timeout=120) as http:
        for row in rows:
            r = await http.post(
                f"{args.chat_base_url}/chat/completions",
                json={
                    "model": args.chat_model,
                    "messages": [
                        {"role": "user",
                         "content": GENERATE_PROMPT.format(chunk=row["content"][:3000])}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 400,
                },
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"]
            try:
                pair = json.loads(raw[raw.index("{") : raw.rindex("}") + 1])
                examples.append(
                    {"messages": [
                        {"role": "user", "content": pair["question"]},
                        {"role": "assistant", "content": pair["answer"]},
                    ]}
                )
            except (ValueError, KeyError):
                continue  # unbrauchbare Generierung überspringen

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in examples)
    )
    print(f"OK: {len(examples)} QA-Paare -> {args.out}")


if __name__ == "__main__":
    asyncio.run(amain())
