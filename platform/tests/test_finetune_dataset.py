"""Unit-Tests für den Fine-Tuning-Dataset-Builder (AP 5.3)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "finetune"))

from build_dataset import split_dataset, to_chat_example, write_jsonl, read_jsonl  # noqa: E402


def test_chat_example_format():
    example = to_chat_example(" Wie viele Urlaubstage? ", "30 Tage [1]. ")
    roles = [m["role"] for m in example["messages"]]
    assert roles == ["system", "user", "assistant"]
    assert example["messages"][1]["content"] == "Wie viele Urlaubstage?"
    assert example["messages"][2]["content"] == "30 Tage [1]."


def test_split_is_deterministic_and_complete():
    examples = [to_chat_example(f"F{i}?", f"A{i}") for i in range(20)]
    train_a, val_a = split_dataset(examples, 0.1)
    train_b, val_b = split_dataset(examples, 0.1)
    assert train_a == train_b and val_a == val_b   # deterministisch (seed)
    assert len(val_a) == 2 and len(train_a) == 18  # 10 % Validierung
    merged = train_a + val_a
    assert all(e in merged for e in examples)      # nichts geht verloren


def test_split_edge_cases():
    one = [to_chat_example("F?", "A")]
    train, val = split_dataset(one, 0.5)
    assert train == one and val == []              # nie leeres Training

    two = [to_chat_example("F1?", "A1"), to_chat_example("F2?", "A2")]
    train, val = split_dataset(two, 0.1)
    assert len(train) == 1 and len(val) == 1       # mind. 1 Val ab 2 Beispielen


def test_jsonl_roundtrip(tmp_path):
    rows = [to_chat_example("Frage mit Umlauten: Öl?", "Antwort: prüfen.")]
    path = tmp_path / "d" / "train.jsonl"
    write_jsonl(path, rows)
    assert read_jsonl(path) == rows
    assert "Öl" in path.read_text()  # ensure_ascii=False