"""Strukturbewusstes Chunking (AP 1.4, Architektur §6.5).

- Überschriften bilden Chunk-Grenzen und werden als Pfad ("Kap. 3 › Wartung")
  an jeden Chunk gehängt – Grundlage für präzise Zitate (A1).
- Zielgröße/Obergrenze in Zeichen (≈ Tokens × 4); überlange Absätze werden an
  Satzgrenzen mit Überlappung geteilt.
"""

from dataclasses import dataclass

from .config import settings
from .parsing import Block


@dataclass
class Chunk:
    index: int
    content: str
    heading_path: str | None
    page: int | None


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            window_start = start + max_chars // 2
            cut = text.rfind(". ", window_start, end)
            if cut == -1:
                cut = text.rfind(" ", window_start, end)
            if cut != -1:
                end = cut + 1
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


def chunk_blocks(
    blocks: list[Block],
    *,
    target_chars: int | None = None,
    max_chars: int | None = None,
    overlap_chars: int | None = None,
    min_chars: int | None = None,
) -> list[Chunk]:
    target = target_chars or settings.chunk_target_chars
    maximum = max_chars or settings.chunk_max_chars
    overlap = overlap_chars or settings.chunk_overlap_chars
    minimum = min_chars if min_chars is not None else settings.chunk_min_chars

    chunks: list[Chunk] = []
    headings: dict[int, str] = {}
    buffer: list[str] = []
    buffer_page: int | None = None

    def heading_path() -> str | None:
        if not headings:
            return None
        return " › ".join(headings[level] for level in sorted(headings))

    def flush() -> None:
        nonlocal buffer, buffer_page
        content = "\n\n".join(buffer).strip()
        if len(content) >= minimum:
            chunks.append(
                Chunk(
                    index=len(chunks),
                    content=content,
                    heading_path=heading_path(),
                    page=buffer_page,
                )
            )
        buffer = []
        buffer_page = None

    for block in blocks:
        if block.heading_level is not None:
            flush()
            level = block.heading_level
            headings[level] = block.text
            for deeper in [lv for lv in headings if lv > level]:
                del headings[deeper]
            continue

        parts = (
            _split_long(block.text, maximum, overlap)
            if len(block.text) > maximum
            else [block.text]
        )
        for part in parts:
            current_len = sum(len(p) for p in buffer) + 2 * len(buffer)
            if buffer and current_len + len(part) > target:
                flush()
            if not buffer:
                buffer_page = block.page
            buffer.append(part)
            if len(parts) > 1:  # geteilte Überlänge: jedes Teilstück eigener Chunk
                flush()

    flush()
    return chunks
