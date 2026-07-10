#!/usr/bin/env python3
"""Adapter-Rollout mit Eval-Gate (AP 5.4, Architektur §6.7).

Ablauf:
1. LoRA-Adapter dynamisch in vLLM laden (/v1/load_lora_adapter)
2. Eval-Lauf über die Plattform-API (goldene Fragen, synchron)
3. Gate: Schwellwerte erfüllt -> Adapter bleibt aktiv; sonst automatischer
   Rollback (/v1/unload_lora_adapter)

    python rollout.py --adapter out/onlumis-lora-v1 \
        --vllm-base http://vllm-chat:8001 \
        --api-base https://onlumis.local/api \
        --api-key olk_... [--min-retrieval 0.8] [--min-keywords 0.8]

Voraussetzung: vLLM mit --enable-lora und VLLM_ALLOW_RUNTIME_LORA_UPDATING=True.
"""

import argparse
import sys
from pathlib import Path

import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", type=Path, required=True,
                        help="Pfad zum Adapter-Verzeichnis (im vLLM-Container sichtbar)")
    parser.add_argument("--vllm-base", required=True)
    parser.add_argument("--api-base", required=True)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--min-retrieval", type=float, default=0.8)
    parser.add_argument("--min-keywords", type=float, default=0.8)
    args = parser.parse_args()

    adapter_name = args.adapter.name
    headers = {"X-Api-Key": args.api_key} if args.api_key else {}

    with httpx.Client(timeout=600, verify=False) as http:  # interne CA
        print(f"1/3 Lade Adapter '{adapter_name}' …")
        r = http.post(
            f"{args.vllm_base}/v1/load_lora_adapter",
            json={"lora_name": adapter_name, "lora_path": str(args.adapter)},
        )
        r.raise_for_status()

        print("2/3 Eval-Gate läuft (goldene Fragen) …")
        r = http.post(
            f"{args.api_base}/v1/admin/evals/run",
            params={"wait": "true", "notes": f"rollout:{adapter_name}"},
            headers=headers,
        )
        r.raise_for_status()
        run_id = r.json()["run_id"]
        stats = http.get(
            f"{args.api_base}/v1/admin/evals/runs/{run_id}", headers=headers
        ).json()["stats"]
        print(f"    Ergebnis: {stats}")

        ok = (
            (stats.get("retrieval_rate") or 0) >= args.min_retrieval
            and (stats.get("keyword_rate") or 0) >= args.min_keywords
        )
        if ok:
            print(f"3/3 Gate bestanden – Adapter '{adapter_name}' bleibt aktiv.")
            return 0

        print("3/3 Gate NICHT bestanden – Rollback …")
        http.post(
            f"{args.vllm_base}/v1/unload_lora_adapter",
            json={"lora_name": adapter_name},
        ).raise_for_status()
        return 1


if __name__ == "__main__":
    sys.exit(main())
