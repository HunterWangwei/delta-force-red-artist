from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

from core.grid import COLS, HEART, ROWS
from core.solver import Item, solve
from integrations.wegame import login_and_fetch
from ui.app import run

ROOT = Path(__file__).resolve().parent

def main():
    loots, goods = login_and_fetch()
    grouped = {}
    for loot in loots:
        iid = str(loot.get("id") or "")
        meta = goods.get(iid, {})
        shape = meta.get("shape")
        if not shape:
            raise RuntimeError(f"远端 goods_list 缺少物品形状: {name} ({iid})")
        name = meta.get("name") or loot.get("name") or iid
        value = float(loot.get("value") or 0) / 1000
        icon = str(loot.get("icon") or meta.get("icon") or "").strip()
        if name not in grouped: grouped[name] = {"shape": shape, "value": value, "qty": 0, "icon": icon}
        grouped[name]["qty"] += 1
    items = [Item(name, *d["shape"], d["value"], d["qty"], d["icon"]) for name, d in grouped.items()]
    mask = [v for row in HEART for v in row]
    solution = solve(items, ROWS, COLS, mask)
    out = ROOT / "solution.json"
    out.write_text(json.dumps(solution, ensure_ascii=False, indent=2), encoding="utf-8")
    run(out)

if __name__ == "__main__": main()
