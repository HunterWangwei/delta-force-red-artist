from __future__ import annotations

import json
import time
from urllib.request import Request, urlopen

WELFARE_URL = "https://www.wegame.com.cn/helper/df/welfare/"
GOODS_LIST_URL = "https://jsonschema.qpic.cn/f17859b917badfa9a083ad92c9eca90b/909d661bec5433db696cfc822e87c22f/goods_list"
API_MARKER = "GetPeriodLoots"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
    "Safari/537.36"
)

def fetch_goods(timeout: float = 30) -> dict[str, dict]:
    req = Request(GOODS_LIST_URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        raw = json.loads(response.read().decode("utf-8"))
    out = {}
    for row in raw.get("list", []):
        iid = str(row.get("id") or "").strip()
        if not iid:
            continue
        fmt = str(row.get("format") or "")
        shape = None
        if "*" in fmt:
            a, _, b = fmt.partition("*")
            try: shape = (int(a), int(b))
            except ValueError: pass
        # goods_list 当前只提供 label/format/id；图片通常在 GetPeriodLoots.loots[].icon。
        out[iid] = {"name": str(row.get("name") or row.get("label") or row.get("title") or ""), "shape": shape, "icon": str(row.get("icon") or row.get("image") or row.get("url") or "")}
    return out

def login_and_fetch(timeout: float = 180) -> tuple[list[dict], dict[str, dict]]:
    from playwright.sync_api import sync_playwright
    captured: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # 与原项目保持一致：新窗口、中文环境和固定 UA，不复用本机 Chrome 用户目录。
        context = browser.new_context(user_agent=UA, locale="zh-CN")
        page = context.new_page()
        def on_response(response):
            if API_MARKER not in response.url or response.status != 200:
                return
            try:
                data = response.json()
                if isinstance(data, dict) and isinstance(data.get("loots"), list): captured.append(data)
            except Exception: pass
        page.on("response", on_response)
        page.goto(WELFARE_URL, wait_until="domcontentloaded", timeout=120000)
        end = time.time() + timeout
        while time.time() < end and not captured:
            page.wait_for_timeout(500)
        if not captured:
            raise RuntimeError("登录等待超时，未捕获 GetPeriodLoots")
        loots = max(captured, key=lambda x: len(x.get("loots", []))).get("loots", [])
        goods = fetch_goods()
        browser.close()
        return loots, goods
