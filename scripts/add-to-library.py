#!/usr/bin/env python3
"""add-to-library.py — 把一份研报 HTML 收进本地收藏夹（Research Library）。

用法：
  python3 add-to-library.py --html /path/report.html --topic jinghe-jicheng \
      --title "港股 IPO 深度尽调" [--topic-name "晶合集成"] [--date 2026-07-09] \
      [--library ~/ResearchLibrary]

动作（幂等，可重复跑）：
  1. 库不存在 → 创建目录 + 复制 assets（sidebar.css/js 来自 skill 的 references/library-assets/）
  2. 复制报告到 {library}/{topic}/{date}-{topic}.html（同名不同内容自动加 -v2）
  3. 更新 manifest.json（库的唯一权威索引）
  4. 重新生成 assets/sidebar-data.js（window.RS_MANIFEST = ...，file:// 下侧栏的数据通道）
  5. 重新生成 index.html（库首页）

报告只存本地，本脚本不做任何网络请求。
"""

import argparse
import html as html_mod
import json
import shutil
import sys
from datetime import date as date_mod
from pathlib import Path

ASSETS_SRC = Path(__file__).resolve().parent.parent / "references" / "library-assets"
ASSET_FILES = ["sidebar.css", "sidebar.js"]

DEFAULT_SITE = {
    "name": "我的研报库",
    "tagline": "ray-deep-research 本地收藏夹",
    "base_url": None,  # 必须为 null：file:// 下路径因机器而异，靠 sidebar.js 自动推断
    "github": "",
}


def ensure_library(lib: Path) -> None:
    (lib / "assets").mkdir(parents=True, exist_ok=True)
    for name in ASSET_FILES:
        src, dst = ASSETS_SRC / name, lib / "assets" / name
        if not src.exists():
            sys.exit(f"错误：skill 资源缺失 {src}（skill 安装不完整？）")
        if not dst.exists() or src.read_bytes() != dst.read_bytes():
            shutil.copy2(src, dst)


def load_manifest(lib: Path) -> dict:
    path = lib / "manifest.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("site", dict(DEFAULT_SITE))
                data.setdefault("topics", [])
                return data
        except (json.JSONDecodeError, UnicodeDecodeError):
            backup = path.with_suffix(".json.bak")
            shutil.copy2(path, backup)
            print(f"警告：manifest.json 损坏，已备份到 {backup}，重建索引", file=sys.stderr)
    return {"site": dict(DEFAULT_SITE), "topics": []}


def copy_report(src: Path, topic_dir: Path, date: str, topic: str) -> str:
    """复制报告进库；同名同内容直接复用（幂等），同名不同内容加 -v2/-v3。"""
    topic_dir.mkdir(parents=True, exist_ok=True)
    content = src.read_bytes()
    base = f"{date}-{topic}"
    for i in range(1, 100):
        name = f"{base}.html" if i == 1 else f"{base}-v{i}.html"
        target = topic_dir / name
        if not target.exists():
            target.write_bytes(content)
            return name
        if target.read_bytes() == content:
            return name  # 同内容已入库，幂等返回
    sys.exit(f"错误：{base} 同日版本过多（>99），请检查是否在循环入库")


def upsert_manifest(manifest: dict, topic: str, topic_name: str, date: str, filename: str, title: str) -> None:
    entry = next((t for t in manifest["topics"] if t.get("slug") == topic), None)
    if entry is None:
        entry = {"slug": topic, "name": topic_name or topic, "tagline": "", "reports": []}
        manifest["topics"].append(entry)
    elif topic_name:
        entry["name"] = topic_name
    report = next((r for r in entry["reports"] if r.get("file") == filename), None)
    if report is None:
        entry["reports"].append({"date": date, "file": filename, "title": title})
    else:
        report.update({"date": date, "title": title})
    entry["reports"].sort(key=lambda r: r.get("date", ""), reverse=True)
    manifest["topics"].sort(
        key=lambda t: max((r.get("date", "") for r in t.get("reports", [])), default=""),
        reverse=True,
    )


def write_outputs(lib: Path, manifest: dict) -> None:
    (lib / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    data_js = "window.RS_MANIFEST = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n"
    (lib / "assets" / "sidebar-data.js").write_text(data_js, encoding="utf-8")
    (lib / "index.html").write_text(render_index(manifest), encoding="utf-8")


def render_index(manifest: dict) -> str:
    site = manifest["site"]
    esc = html_mod.escape
    total = sum(len(t.get("reports", [])) for t in manifest["topics"])
    sections = []
    for t in manifest["topics"]:
        items = "\n".join(
            f'      <li><a href="{esc(t["slug"])}/{esc(r["file"])}">'
            f'<span class="date">{esc(r.get("date", ""))}</span>{esc(r.get("title", r["file"]))}</a></li>'
            for r in t.get("reports", [])
        )
        sections.append(
            f'  <section>\n    <h2>{esc(t.get("name", t["slug"]))}'
            f' <span class="count">({len(t.get("reports", []))})</span></h2>\n'
            f'    <ul>\n{items}\n    </ul>\n  </section>'
        )
    body = "\n".join(sections) if sections else "  <p>还没有报告。跑一次调研就会自动出现在这里。</p>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(site.get("name", "我的研报库"))}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         max-width: 720px; margin: 0 auto; padding: 48px 24px 80px;
         color: #1a1a1a; background: #fafaf8; line-height: 1.7; }}
  h1 {{ font-size: 28px; margin-bottom: 4px; }}
  .tagline {{ color: #777; margin-top: 0; }}
  h2 {{ font-size: 18px; margin: 32px 0 8px; border-bottom: 1px solid #e2e0da; padding-bottom: 6px; }}
  .count {{ color: #999; font-weight: normal; font-size: 14px; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li a {{ display: flex; gap: 12px; padding: 8px 4px; text-decoration: none; color: inherit;
          border-radius: 6px; }}
  li a:hover {{ background: #f0eee8; }}
  .date {{ color: #999; font-variant-numeric: tabular-nums; flex-shrink: 0; }}
  footer {{ margin-top: 48px; color: #999; font-size: 13px; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #e8e6e3; background: #1e1e1e; }}
    h2 {{ border-color: #3a3a3a; }}
    li a:hover {{ background: #2a2a2a; }}
  }}
</style>
</head>
<body>
<h1>{esc(site.get("name", "我的研报库"))}</h1>
<p class="tagline">{esc(site.get("tagline", ""))} · 共 {total} 份报告 · 全部只存在这台电脑上</p>
{body}
<footer>由 ray-deep-research 自动维护 · 手动改动会在下次入库时被保留（manifest.json 是唯一索引）</footer>
</body>
</html>
"""


def main() -> None:
    p = argparse.ArgumentParser(description="把研报 HTML 收进本地收藏夹")
    p.add_argument("--html", required=True, help="报告 HTML 文件路径（工作目录成品）")
    p.add_argument("--topic", required=True, help="话题 slug（小写短横线，如 jinghe-jicheng）")
    p.add_argument("--title", required=True, help="报告标题")
    p.add_argument("--topic-name", default="", help="话题显示名（如 晶合集成），首次建话题时用")
    p.add_argument("--date", default=date_mod.today().isoformat(), help="报告日期 YYYY-MM-DD，默认今天")
    p.add_argument("--library", default="~/ResearchLibrary", help="库路径，默认 ~/ResearchLibrary")
    args = p.parse_args()

    src = Path(args.html).expanduser()
    if not src.is_file():
        sys.exit(f"错误：找不到报告文件 {src}")
    lib = Path(args.library).expanduser()

    ensure_library(lib)
    manifest = load_manifest(lib)
    filename = copy_report(src, lib / args.topic, args.date, args.topic)
    upsert_manifest(manifest, args.topic, args.topic_name, args.date, filename, args.title)
    write_outputs(lib, manifest)

    print(f"已入库：{lib / args.topic / filename}")
    print(f"库首页：{lib / 'index.html'}")


if __name__ == "__main__":
    main()
