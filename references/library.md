# 本地收藏夹（Research Library）

Stage 5 的**默认交付方式**（没配 `publish.enabled=true` 的用户都走这条路）：每份研报自动收进用户电脑上的一个库文件夹，打开任何一份报告，侧边栏列出 TA 做过的全部报告——像收藏夹。

**隐私边界（产品级决定，勿改）**：入库全程不联网、不上传，报告只存在用户电脑上。skill 里没有任何"传出去"的入口；用户想分享到共享库 → 自己去共享库网站手动上传（见 `exchange.md` 的"分享"节）。一句话：**电脑里的都是自己的，网站上的都是自己亲手传的。**

## 目录结构

```
~/ResearchLibrary/                  ← 默认位置；config.json 的 library_path 可改
├── index.html                      库首页（脚本生成，勿手改）
├── manifest.json                   唯一权威索引（脚本维护，勿手改）
├── assets/
│   ├── sidebar.css                 侧栏样式（来自 skill references/library-assets/）
│   ├── sidebar.js                  侧栏渲染（同上，本地收藏夹改造版）
│   └── sidebar-data.js             清单数据（每次入库重新生成）
└── {topic}/
    └── {YYYY-MM-DD}-{slug}.html    报告本体
```

## 入库流程（Stage 5 · A 路）

一条命令，全自动，**不要手工改清单文件**（老站教训：手工改多处索引必漏）：

```bash
python3 {skill 目录}/scripts/add-to-library.py \
  --html ~/.cache/ray-deep-research/{slug}/report.html \
  --topic {slug} --topic-name "{中文显示名}" \
  --title "{报告标题}" --date {YYYY-MM-DD}
```

脚本动作：首次自动建库（含复制 assets）→ 复制报告 → 更新 manifest.json → 重新生成 sidebar-data.js 和 index.html。幂等，重复跑不产生重复条目；同日同题不同内容自动加 `-v2`。

之后 `open` **库里那份**报告交付（不要开工作目录副本——侧栏资源是 `../assets/` 相对路径，只在库结构下能加载）。

## 为什么侧栏能"打开任何一份都是最新列表"

报告 HTML 里**不写死**历史列表，只带三行引用（template.html 骨架已含）：

```html
<link rel="stylesheet" href="../assets/sidebar.css">
<script src="../assets/sidebar-data.js"></script>
<script defer src="../assets/sidebar.js"></script>
```

清单只存在 `sidebar-data.js` 一个文件里，每次入库重新生成——所有新旧报告打开时读的都是同一份最新清单，旧报告一个字节都不用改。

**技术硬约束（改动前必知）**：本地双击打开的 HTML 是 `file://` 协议，浏览器**拦截 fetch/XHR 读本地文件**（老站 sidebar.js 的 fetch manifest.json 方案在本地会静默失败），但 `<script src>` 相对路径**不受限**——这就是清单走 sidebar-data.js 而不走 fetch 的原因。改造版 sidebar.js 优先读 `window.RS_MANIFEST`，没有才 fetch 兜底（http 环境用）。

## 与发布模式（B 路）的关系

| | A 路 · 本地收藏夹（默认） | B 路 · GitHub 发布（Ray） |
|---|---|---|
| 触发 | 无 publish 配置 | `publish.enabled=true` |
| 位置 | `~/ResearchLibrary`（或 library_path） | `~/ray-research` git 仓库 |
| 索引脚本 | skill 自带 `add-to-library.py` | 仓库自带 `add-report.py`（5 处索引） |
| 侧栏数据 | sidebar-data.js（file:// 可用） | fetch manifest.json（Pages 在线可用） |
| 可见性 | 只有本人 | 公开网页 |

两条路结构同构（`{topic}/{date}-{slug}.html` + assets/），朋友哪天想把收藏夹变成公开网站，目录原样可迁。

## Stage 0.5 联动

有了收藏夹，"避免重复烧钱"检查对所有用户生效：`grep -i "{主题名}" {库路径}/manifest.json`，命中 ≤30 天的报告就先问用户（重做 / 只更新 / 看旧版），规则见 SKILL.md Stage 0.5。
