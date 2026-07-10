#!/usr/bin/env python3
"""OnLumis-Lasttest (AP 1.9 PoC-Messung / AP 6.1 Härtung).

Simuliert parallele Chat-Nutzer gegen /v1/chat/completions (Streaming) und
misst TTFT (Zeit bis erstes Token), Gesamtdauer und Fehlerrate; optional
zusätzlich die Such-Latenz. Läuft mit dem venv der Plattform (httpx).

Beispiele:
    # Dev-Auth gegen lokalen Stack
    python loadtest.py --base-url http://127.0.0.1:8000 --users 10 --duration 60

    # Auf der Spark über Caddy mit API-Key (Scope chat+search)
    python loadtest.py --base-url https://onlumis.local/api \
        --api-key olk_... --users 20 --duration 120 --insecure

Interpretation (Zielwerte Implementierungsplan §7):
    TTFT p50 < 2 s, p95 < 6 s bei 10 parallelen Chats.
"""

import argparse
import asyncio
import json
import time

import httpx

QUESTIONS = [
    "Wie viele Urlaubstage habe ich pro Jahr?",
    "Wie viel Sonderurlaub gibt es bei einer Hochzeit?",
    "Was tun, wenn die Presse P-300 keinen Druck aufbaut?",
    "Welcher Öldruck ist bei der wöchentlichen Wartung korrekt?",
    "Wie lange kann Resturlaub übertragen werden?",
]


def pct(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    k = min(len(ordered) - 1, max(0, round(p / 100 * (len(ordered) - 1))))
    return ordered[k]


async def chat_once(client: httpx.AsyncClient, question: str, stats: dict,
                    headers: dict) -> None:
    start = time.monotonic()
    ttft = None
    chunks = 0
    try:
        async with client.stream(
            "POST",
            "/v1/chat/completions",
            headers=headers,
            json={
                "messages": [{"role": "user", "content": question}],
                "stream": True,
            },
        ) as response:
            if response.status_code == 429:
                stats["limited"] += 1
                return
            if response.status_code != 200:
                stats["errors"] += 1
                return
            async for line in response.aiter_lines():
                if not line.startswith("data: ") or line[6:].strip() == "[DONE]":
                    continue
                try:
                    payload = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
                if payload.get("object") == "chat.completion.chunk":
                    delta = payload.get("choices", [{}])[0].get("delta", {})
                    if delta.get("content"):
                        chunks += 1
                        if ttft is None:
                            ttft = time.monotonic() - start
        stats["requests"] += 1
        stats["chunks"] += chunks
        if ttft is not None:
            stats["ttft"].append(ttft)
        stats["total"].append(time.monotonic() - start)
    except httpx.HTTPError:
        stats["errors"] += 1


async def search_once(client: httpx.AsyncClient, question: str, stats: dict,
                      headers: dict) -> None:
    start = time.monotonic()
    try:
        r = await client.post(
            "/v1/search", headers=headers, json={"query": question, "top_k": 8}
        )
        if r.status_code == 200:
            stats["search"].append(time.monotonic() - start)
        elif r.status_code == 429:
            stats["limited"] += 1
        else:
            stats["errors"] += 1
    except httpx.HTTPError:
        stats["errors"] += 1


async def user_loop(client: httpx.AsyncClient, deadline: float, stats: dict,
                    with_search: bool, index: int, headers: dict) -> None:
    i = index
    while time.monotonic() < deadline:
        question = QUESTIONS[i % len(QUESTIONS)]
        i += 1
        await chat_once(client, question, stats, headers)
        if with_search:
            await search_once(client, question, stats, headers)


async def amain() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--duration", type=int, default=60, help="Sekunden")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--dev-user", default="bench")
    parser.add_argument("--dev-groups", default="all-users")
    parser.add_argument("--no-search", action="store_true")
    parser.add_argument("--insecure", action="store_true",
                        help="TLS-Prüfung aus (interne CA)")
    args = parser.parse_args()

    def headers_for(index: int) -> dict:
        # Dev-Modus: eigene Identität je virtuellem Nutzer, damit das
        # Pro-Nutzer-Rate-Limit realistisch greift. Bei API-Key teilen sich
        # alle eine Identität -> für Lasttests RATE_LIMIT_PER_MINUTE erhöhen.
        if args.api_key:
            return {"X-Api-Key": args.api_key}
        return {"X-Dev-User": f"{args.dev_user}-{index}",
                "X-Dev-Groups": args.dev_groups}

    stats = {"requests": 0, "errors": 0, "limited": 0, "chunks": 0,
             "ttft": [], "total": [], "search": []}

    async with httpx.AsyncClient(
        base_url=args.base_url, timeout=300, verify=not args.insecure,
    ) as client:
        started = time.monotonic()
        deadline = started + args.duration
        await asyncio.gather(*[
            user_loop(client, deadline, stats, not args.no_search, i, headers_for(i))
            for i in range(args.users)
        ])
        elapsed = time.monotonic() - started

    print(f"\n=== OnLumis-Lasttest: {args.users} Nutzer, {elapsed:.0f}s, "
          f"{args.base_url} ===")
    print(f"Chat-Anfragen : {stats['requests']}  (Fehler: {stats['errors']}, "
          f"rate-limitiert: {stats['limited']})")
    if stats["limited"] and not stats["errors"]:
        print("Hinweis: 429er = Rate-Limit greift (RATE_LIMIT_PER_MINUTE); "
              "für reine Durchsatzmessung auf 0 setzen.")
    if stats["ttft"]:
        print(f"TTFT          : p50 {pct(stats['ttft'], 50):.2f}s | "
              f"p95 {pct(stats['ttft'], 95):.2f}s | max {max(stats['ttft']):.2f}s")
        print(f"Antwortdauer  : p50 {pct(stats['total'], 50):.2f}s | "
              f"p95 {pct(stats['total'], 95):.2f}s")
        print(f"Durchsatz     : {stats['requests'] / elapsed:.2f} Antworten/s | "
              f"~{stats['chunks'] / elapsed:.0f} Chunks/s")
        print(f"Mittl. Chunks : {stats['chunks'] / max(1, stats['requests']):.0f} pro Antwort")
    if stats["search"]:
        print(f"Suche         : p50 {pct(stats['search'], 50) * 1000:.0f}ms | "
              f"p95 {pct(stats['search'], 95) * 1000:.0f}ms "
              f"({len(stats['search'])} Anfragen)")
    ok = stats["ttft"] and pct(stats["ttft"], 50) < 2 and pct(stats["ttft"], 95) < 6
    print(f"Zielwerte (p50<2s, p95<6s): {'ERFÜLLT' if ok else 'NICHT erfüllt'}")


if __name__ == "__main__":
    asyncio.run(amain())
