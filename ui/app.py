from __future__ import annotations

import base64
import colorsys
import json
import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.request import Request, urlopen

from core.grid import COLS, HEART, ROWS

BG = "#0e1218"
SURFACE = "#171d25"
SURFACE_2 = "#202936"
BORDER = "#303b4a"
TEXT = "#f0f4f8"
MUTED = "#91a0b2"
ACCENT = "#f4b35d"
CELL, GAP, STEP = 46, 3, 49

def color_for(name: str, index: int) -> str:
    value = 0
    for char in f"{name}:{index}":
        value = (value * 33 + ord(char)) & 0xFFFFFFFF
    r, g, b = colorsys.hsv_to_rgb((value % 360) / 360, 0.45, 0.62)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

class App(tk.Tk):
    def __init__(self, solution: dict, root: Path):
        super().__init__()
        self.title("大红艺术家 · 爱心格方案")
        self.geometry("1160x820")
        self.minsize(960, 700)
        self.configure(bg=BG)
        self.solution, self.root_path = solution, root
        self._image_refs: list[tk.PhotoImage] = []
        self._configure_styles()
        self._build_layout()
        self._draw_board()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Root.TFrame", background=BG)
        style.configure("Surface.TFrame", background=SURFACE)
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Microsoft YaHei UI", 19, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Microsoft YaHei UI", 9))
        style.configure("Section.TLabel", background=SURFACE, foreground=TEXT, font=("Microsoft YaHei UI", 12, "bold"))
        style.configure("Value.TLabel", background=SURFACE, foreground=TEXT, font=("Microsoft YaHei UI", 13, "bold"))
        style.configure("Caption.TLabel", background=SURFACE, foreground=MUTED, font=("Microsoft YaHei UI", 9))
        style.configure("Accent.TButton", background=ACCENT, foreground="#1a1e23", padding=(14, 8), borderwidth=0)

    def _build_layout(self):
        root = ttk.Frame(self, style="Root.TFrame", padding=22); root.pack(fill=tk.BOTH, expand=True)
        header = ttk.Frame(root, style="Root.TFrame"); header.pack(fill=tk.X, pady=(0, 18))
        title = ttk.Frame(header, style="Root.TFrame"); title.pack(side=tk.LEFT)
        ttk.Label(title, text="爱心格方案", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title, text=f"{self.solution.get('status', 'UNKNOWN')}  ·  {len(self.solution.get('placements', []))} 件物品", style="Sub.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Button(header, text="重新载入", style="Accent.TButton", command=self._reload).pack(side=tk.RIGHT)
        body = ttk.Frame(root, style="Root.TFrame"); body.pack(fill=tk.BOTH, expand=True)
        board = ttk.Frame(body, style="Surface.TFrame", padding=18); board.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))
        board_head = ttk.Frame(board, style="Surface.TFrame"); board_head.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(board_head, text="摆放预览", style="Section.TLabel").pack(side=tk.LEFT)
        ttk.Label(board_head, text="行列坐标从 1 开始", style="Caption.TLabel").pack(side=tk.RIGHT)
        self.canvas = tk.Canvas(board, bg=SURFACE, highlightthickness=0); self.canvas.pack(expand=True)
        panel = ttk.Frame(body, style="Surface.TFrame", padding=18, width=300); panel.pack(side=tk.RIGHT, fill=tk.Y); panel.pack_propagate(False)
        ttk.Label(panel, text="方案概览", style="Section.TLabel").pack(anchor="w")
        self._metric(panel, "总价值", self.solution.get("totalValue", "—")); self._metric(panel, "状态", self.solution.get("status", "—"))
        metrics = self.solution.get("metrics") or {}; self._metric(panel, "候选摆放", metrics.get("candidates", "—")); self._metric(panel, "覆盖格数", metrics.get("coveredCells", "—"))
        ttk.Separator(panel).pack(fill=tk.X, pady=16); ttk.Label(panel, text="已选物品", style="Section.TLabel").pack(anchor="w")
        self.listbox = tk.Listbox(panel, bg=SURFACE_2, fg=TEXT, selectbackground="#46566c", relief=tk.FLAT, highlightthickness=0, font=("Microsoft YaHei UI", 10), activestyle="none"); self.listbox.pack(fill=tk.BOTH, expand=True, pady=(10, 12)); self.listbox.bind("<<ListboxSelect>>", self._select_item)
        for p in self.solution.get("placements", []): self.listbox.insert(tk.END, f"{p['name']}   {p['w']}×{p['h']}   {p['value']}")
        self.detail = ttk.Label(panel, text="点击右侧物品查看坐标", style="Caption.TLabel", wraplength=250); self.detail.pack(anchor="w")

    def _metric(self, parent, label, value):
        row = ttk.Frame(parent, style="Surface.TFrame"); row.pack(fill=tk.X, pady=(12, 0)); ttk.Label(row, text=label, style="Caption.TLabel").pack(side=tk.LEFT); ttk.Label(row, text=str(value), style="Value.TLabel").pack(side=tk.RIGHT)

    def _draw_board(self):
        self.canvas.delete("all"); self._image_refs.clear(); placements = self.solution.get("placements", []); ox, oy = 28, 26
        for c in range(COLS): self.canvas.create_text(ox + c * STEP + CELL / 2, oy - 12, text=str(c + 1), fill=MUTED, font=("Segoe UI", 9))
        for r in range(ROWS): self.canvas.create_text(ox - 14, oy + r * STEP + CELL / 2, text=str(r + 1), fill=MUTED, font=("Segoe UI", 9))
        for r in range(ROWS):
            for c in range(COLS):
                x, y = ox + c * STEP, oy + r * STEP; self.canvas.create_rectangle(x, y, x + CELL, y + CELL, fill="#263240" if HEART[r][c] else "#10161d", outline=BORDER)
        for index, p in enumerate(placements):
            x, y = ox + p["topCol"] * STEP, oy + p["topRow"] * STEP; x2, y2 = x + p["w"] * CELL + (p["w"] - 1) * GAP, y + p["h"] * CELL + (p["h"] - 1) * GAP
            self.canvas.create_rectangle(x, y, x2, y2, fill=color_for(p["name"], index), outline="#f8fbff")
            photo = self._remote_icon(p.get("icon", ""), max(16, x2 - x - 8), max(16, y2 - y - 26))
            if photo: self.canvas.create_image((x + x2) / 2, y + 4 + (y2 - y - 22) / 2, image=photo)
            self.canvas.create_text((x + x2) / 2, y2 - 10, text=p["name"][:7], fill="#ffffff", font=("Microsoft YaHei UI", 9, "bold")); self.canvas.create_text(x + 5, y + 4, text=str(p["value"]), anchor="nw", fill="#ffffff", font=("Consolas", 8))
        self.canvas.config(width=COLS * STEP + 56, height=ROWS * STEP + 56)

    def _remote_icon(self, url, width, height):
        if not url: return None
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.wegame.com.cn/"})
            with urlopen(request, timeout=8) as response: raw = response.read()
            try:
                from PIL import Image, ImageTk
                image = Image.open(BytesIO(raw)).convert("RGBA"); image.thumbnail((width, height), Image.Resampling.LANCZOS); photo = ImageTk.PhotoImage(image)
            except ImportError: photo = tk.PhotoImage(data=base64.b64encode(raw))
            self._image_refs.append(photo); return photo
        except Exception: return None

    def _select_item(self, _event=None):
        selection = self.listbox.curselection()
        if selection:
            p = self.solution.get("placements", [])[selection[0]]; self.detail.config(text=f"{p['name']}\n尺寸：{p['w']}×{p['h']}\n位置：第 {p['topRow'] + 1} 行，第 {p['topCol'] + 1} 列\n价值：{p['value']}")

    def _reload(self):
        try: self.solution = json.loads((self.root_path / "solution.json").read_text(encoding="utf-8")); self._draw_board()
        except Exception as exc: messagebox.showerror("重新载入失败", str(exc))

def run(path: Path):
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: messagebox.showerror("方案读取失败", str(exc)); return
    App(data, path.parent).mainloop()
