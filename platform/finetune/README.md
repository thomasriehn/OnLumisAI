# Fine-Tuning-Pipeline (Phase 5, Architektur §6.7)

**Grundsatz (ADR-9):** Fine-Tuning trainiert *Verhalten* – Tonalität,
Firmenterminologie, Zitiertreue, Antwortformate. **Niemals Faktenwissen**, denn
Dokument-ACLs greifen nur im Retrieval; in Gewichte eingebranntes Wissen würde
Berechtigungen umgehen. Datensätze dürfen daher nur Inhalte enthalten, die alle
Nutzer sehen dürfen (`all-users`), oder müssen entsprechend kuratiert sein.

## Ablauf

```
Feedback (👍 + Kuratierung im Admin-Portal)   Synthetische QA-Paare
                └──────────────┬──────────────────────┘
                       build_dataset.py
                     (train/val JSONL, Chat-Format)
                               │
                        train_lora.py
              (QLoRA, Unsloth/TRL, Nachtfenster auf der Spark)
                               │
                     Eval-Gate: POST /v1/admin/evals/run
              (goldene Fragen; Schwellwerte siehe rollout.py)
                               │
                         rollout.py
        (vLLM Dynamic-LoRA-Load, dokumentierter Rollback)
```

## Kommandos

```bash
# 1. Datensatz bauen (liest kuratiertes Feedback direkt aus der DB)
python build_dataset.py --database-url $DATABASE_URL --out data/

# 1b. Optional anreichern: synthetische QA-Paare aus allgemein
#     freigegebenen Dokumenten (nutzt das laufende Chat-Modell)
python synth_qa.py --database-url $DATABASE_URL \
  --chat-base-url http://localhost:8001/v1 --limit 200 --out data/synth.jsonl

# 2. LoRA-Training (auf der Spark, GPU; --dry-run zeigt den Plan ohne GPU)
python train_lora.py --config configs/qwen3-32b-lora.yaml

# 3. Eval-Gate + Rollout (lädt den Adapter nur bei bestandenem Gate)
python rollout.py --adapter out/onlumis-lora-v1 \
  --api-base https://onlumis.local/api --vllm-base http://vllm-chat:8001
```

`train_lora.py` benötigt `torch`, `transformers`, `trl`, `peft`,
`bitsandbytes` (bzw. Unsloth) – bewusst **nicht** in den Service-Images
enthalten; auf der Spark das NGC-PyTorch-Image verwenden. Adapter werden mit
Versionsnummer und Trainings-Config im Verzeichnis `out/` abgelegt
(Adapter-Registry) und beim Backup mitgesichert.
