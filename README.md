# 三角洲行动-大红艺术家

一个面向「三角洲行动」大红活动的爱心格方案工具。程序打开独立浏览器窗口，等待用户完成登录后监听页面实际发出的 `GetPeriodLoots` 响应，再从远端 `goods_list` 获取物品名称和矩形尺寸，使用 OR-Tools 计算高价值摆放方案，最后打开 Tkinter 结果窗口。

## 特点

- 不读取本地 Excel、物品图鉴或本地图片作为运行时输入。
- 物品名称、尺寸来自远端 `goods_list`。
- 当前周期数量、价值和图片链接来自 `GetPeriodLoots`。
- 新浏览器窗口保留旧版的中文 locale 和 User-Agent 配置。
- 求解器、网络集成和 UI 分层，方便单独替换。
- 图片下载失败时仍显示色块和文字，不影响方案生成。

## 项目结构

```text
大红艺术家_v2/
├─ main.py                  # 唯一启动入口
├─ core/
│  ├─ grid.py               # 爱心格掩码
│  └─ solver.py             # CP-SAT 矩形摆放模型
├─ integrations/
│  └─ wegame.py             # 登录窗口、GetPeriodLoots、goods_list
├─ ui/
│  └─ app.py                # Tkinter 方案展示
├─ requirements.txt
├─ LICENSE
└─ .gitignore
```

## 环境要求

- Windows 10/11
- Python 3.11、3.12 或 3.13
- 可访问 WeGame 和物品图片 CDN 的网络
- 已安装并登录 QQ 客户端（快捷登录是否出现由 WeGame/QQ 页面决定）

建议使用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 运行

```powershell
python main.py
```

程序会打开一个独立 Chromium 窗口：

1. 在窗口中完成 QQ/扫码登录。
2. 等待活动页发出 `GetPeriodLoots` 请求。
3. 程序自动获取远端物品目录并求解。
4. 方案窗口显示爱心格位置、图片、价值和物品明细。

`solution.json` 只作为运行过程中的临时输出，已被 `.gitignore` 排除，不应提交登录数据或个人活动结果。

## 发布 exe

构建机需要 Python 3.12 或 3.13。不要使用 Python 3.14 构建 OR-Tools 冻结版。

在 PowerShell 执行：

```powershell
.\build_windows.ps1
```

脚本会创建构建虚拟环境、安装依赖、下载 Chromium，并生成：

```text
dist\\三角洲行动-大红艺术家\\三角洲行动-大红艺术家.exe
```

发布时请压缩整个 `dist\\三角洲行动-大红艺术家` 文件夹，而不是只复制 exe。用户机器不需要安装 Python、pip、Playwright 或 Chromium。

PyInstaller 会把 Python 解释器和依赖放入发布包；Playwright Chromium 通过 `PLAYWRIGHT_BROWSERS_PATH=0` 在构建阶段一并收集。这样发布包会比较大，但目标电脑无需额外安装运行环境。

## 数据来源

### GetPeriodLoots

用于当前周期数据：物品 ID、当前拥有数量、单件价值和 `icon` 图片 URL。

### goods_list

用于公共物品目录：`id`、`label`、`format`，例如 `2*3`。

如果远端目录中缺少某件物品的 `format`，程序会直接报错，不会读取本地清单猜测形状。

## 常见问题

### 提示 Playwright 找不到浏览器

执行：

```powershell
python -m playwright install chromium
```

### 登录后没有捕获物品

确保活动页已经加载出本周期物品列表，并在登录完成后保持窗口打开一段时间。不要短时间重复扫码，QQ/WeGame 可能触发环境风险限制。

### 图片没有显示

图片来自 `GetPeriodLoots.loots[].icon`。如果 CDN 请求失败，方案仍会显示色块和名称；终端会输出图片加载异常。

## 安全与合规

- 本项目不保存 QQ Cookie、登录凭据或浏览器用户目录。
- 不要提交 `solution.json`、Cookie、日志或任何个人活动数据。
- 本项目仅用于个人信息整理和方案计算，请遵守相关平台的服务条款。

## License

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
