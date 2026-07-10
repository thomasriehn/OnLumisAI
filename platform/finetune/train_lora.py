#!/usr/bin/env python3
"""QLoRA-Training auf der DGX Spark (AP 5.3) – Verhalten, nicht Wissen (ADR-9).

Läuft im Nachtfenster (Serving gedrosselt) im NGC-PyTorch-Container:
    python train_lora.py --config configs/qwen3-32b-lora.yaml [--dry-run]

Abhängigkeiten (nicht Teil der Service-Images): torch, transformers, trl,
peft, bitsandbytes, datasets, pyyaml.
"""

import argparse
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "base_model": "Qwen/Qwen3-32B",
    "train_file": "data/train.jsonl",
    "val_file": "data/val.jsonl",
    "output_dir": "out/onlumis-lora-v1",
    "epochs": 2,
    "learning_rate": 1e-4,
    "lora_r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "max_seq_length": 4096,
    "per_device_batch_size": 1,
    "gradient_accumulation": 8,
    "load_in_4bit": True,
}


def load_config(path: Path | None) -> dict:
    config = dict(DEFAULT_CONFIG)
    if path is not None:
        import yaml

        config.update(yaml.safe_load(path.read_text()) or {})
    return config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="Nur Plan ausgeben (keine GPU nötig)")
    args = parser.parse_args()
    config = load_config(args.config)

    if args.dry_run:
        print("Trainingsplan:\n" + json.dumps(config, indent=2, ensure_ascii=False))
        return

    # Schwere Importe erst hier – das Skript bleibt ohne GPU-Umgebung ladbar.
    import torch  # noqa: F401
    from datasets import load_dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    tokenizer = AutoTokenizer.from_pretrained(config["base_model"])
    quant = (
        BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
        if config["load_in_4bit"]
        else None
    )
    model = AutoModelForCausalLM.from_pretrained(
        config["base_model"],
        quantization_config=quant,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    dataset = load_dataset(
        "json",
        data_files={"train": config["train_file"], "validation": config["val_file"]},
    )
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=LoraConfig(
            r=config["lora_r"],
            lora_alpha=config["lora_alpha"],
            lora_dropout=config["lora_dropout"],
            task_type="CAUSAL_LM",
            target_modules="all-linear",
        ),
        args=SFTConfig(
            output_dir=config["output_dir"],
            num_train_epochs=config["epochs"],
            learning_rate=config["learning_rate"],
            per_device_train_batch_size=config["per_device_batch_size"],
            gradient_accumulation_steps=config["gradient_accumulation"],
            max_length=config["max_seq_length"],
            bf16=True,
            logging_steps=10,
            eval_strategy="epoch",
            save_strategy="epoch",
        ),
    )
    trainer.train()
    trainer.save_model(config["output_dir"])
    (Path(config["output_dir"]) / "training-config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False)
    )
    print(f"Adapter gespeichert: {config['output_dir']}")


if __name__ == "__main__":
    main()
