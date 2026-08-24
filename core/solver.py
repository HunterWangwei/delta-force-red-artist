from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ortools.sat.python import cp_model

@dataclass(frozen=True)
class Item:
    name: str
    width: int
    height: int
    value: float
    quantity: int
    icon: str = ""

def placements(items: list[Item], mask: list[int], rows: int, cols: int) -> list[dict]:
    idx = {(r, c): i for i, (r, c) in enumerate((r, c) for r in range(rows) for c in range(cols) if mask[r * cols + c])}
    result = []
    for item in items:
        orientations = {(item.width, item.height), (item.height, item.width)}
        for width, height in orientations:
            for row in range(rows):
                for col in range(cols):
                    cells = []
                    for dr in range(height):
                        for dc in range(width):
                            key = (row + dr, col + dc)
                            if key not in idx:
                                break
                            cells.append(idx[key])
                        else:
                            continue
                        break
                    if len(cells) == width * height:
                        result.append({"item": item, "w": width, "h": height, "row": row, "col": col, "cells": tuple(cells)})
    return result

def solve(items: list[Item], rows: int, cols: int, mask: list[int], seconds: float = 120) -> dict:
    candidates = placements(items, mask, rows, cols)
    model = cp_model.CpModel()
    variables = [model.NewBoolVar(f"p{i}") for i in range(len(candidates))]
    for cell in range(sum(mask)):
        model.Add(sum(v for v, p in zip(variables, candidates) if cell in p["cells"]) <= 1)
    for item in items:
        model.Add(sum(v for v, p in zip(variables, candidates) if p["item"] == item) <= item.quantity)
    model.Maximize(sum(int(round(p["item"].value * 100)) * v for p, v in zip(candidates, variables)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f"求解失败: {solver.StatusName(status)}")
    chosen = []
    for var, p in zip(variables, candidates):
        if solver.Value(var):
            item = p["item"]
            chosen.append({"name": item.name, "value": item.value, "w": p["w"], "h": p["h"], "topRow": p["row"], "topCol": p["col"], "icon": item.icon})
    return {"status": solver.StatusName(status), "totalValue": round(sum(p["value"] for p in chosen), 2), "grid": {"rows": rows, "cols": cols}, "metrics": {"candidates": len(candidates), "selected": len(chosen)}, "placements": chosen}
