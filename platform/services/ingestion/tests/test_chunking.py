from worker.chunking import Chunk, chunk_blocks
from worker.parsing import Block, parse_markdown


def test_heading_paths_and_boundaries():
    blocks = [
        Block(text="Handbuch", heading_level=1),
        Block(text="Einleitung " * 30),
        Block(text="Wartung", heading_level=2),
        Block(text="Ölstand prüfen. " * 20),
    ]
    chunks = chunk_blocks(blocks, target_chars=2000, max_chars=3200)
    assert len(chunks) == 2
    assert chunks[0].heading_path == "Handbuch"
    assert chunks[1].heading_path == "Handbuch › Wartung"
    assert "Ölstand" in chunks[1].content


def test_heading_stack_resets_deeper_levels():
    blocks = [
        Block(text="A", heading_level=1),
        Block(text="A.1", heading_level=2),
        Block(text="text eins " * 5),
        Block(text="B", heading_level=1),
        Block(text="text zwei " * 5),
    ]
    chunks = chunk_blocks(blocks)
    assert chunks[0].heading_path == "A › A.1"
    assert chunks[1].heading_path == "B"  # A.1 darf nicht mehr im Pfad stehen


def test_long_paragraph_split_with_overlap():
    text = "Satz Nummer eins ist hier. " * 300  # ~8100 Zeichen
    chunks = chunk_blocks([Block(text=text)], target_chars=2000, max_chars=3200,
                          overlap_chars=200)
    assert len(chunks) >= 3
    assert all(len(c.content) <= 3200 for c in chunks)
    # Indizes fortlaufend
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_size_bounds_and_min_filter():
    blocks = [Block(text="ok " * 400), Block(text="x")]  # 2. Block unter Minimum
    chunks = chunk_blocks(blocks, target_chars=600, max_chars=900, min_chars=20)
    assert all(len(c.content) <= 900 for c in chunks)
    assert all(len(c.content) >= 20 for c in chunks)


def test_page_tracking_from_first_block():
    blocks = [Block(text="Seite eins Inhalt " * 10, page=1),
              Block(text="Seite zwei Inhalt " * 10, page=2)]
    chunks = chunk_blocks(blocks, target_chars=100, max_chars=400)
    assert chunks[0].page == 1
    assert chunks[-1].page == 2


def test_deterministic():
    doc = parse_markdown("# T\n\nAbsatz eins.\n\n## U\n\nAbsatz zwei ist länger und gut.")
    a = chunk_blocks(doc.blocks)
    b = chunk_blocks(doc.blocks)
    assert a == b
    assert all(isinstance(c, Chunk) for c in a)
