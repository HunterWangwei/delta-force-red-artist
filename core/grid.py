from __future__ import annotations

HEART = (
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 1, 1, 1, 0, 1, 1, 1, 0),
    (0, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    (0, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    (0, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    (0, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    (0, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    (0, 0, 1, 1, 1, 1, 1, 1, 1, 0),
    (0, 0, 0, 1, 1, 1, 1, 1, 0, 0),
    (0, 0, 0, 0, 1, 1, 1, 0, 0, 0),
    (0, 0, 0, 0, 0, 1, 0, 0, 0, 0),
)
ROWS, COLS = len(HEART), len(HEART[0])

def cells() -> list[tuple[int, int]]:
    return [(r, c) for r, row in enumerate(HEART) for c, value in enumerate(row) if value]
