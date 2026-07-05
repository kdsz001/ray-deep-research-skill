# Stage 5 · 发布到 GitHub 仓库

调研报告生成 + 自检完成后，**自动同步到公开仓库** `kdsz001/ray-research`。让用户能用 URL 分享给别人。

**前提（通用版）**：本流程仅在配置文件（`~/.config/ray-deep-research/config.json`，见 `environment.md`）里 `publish.enabled=true` 时执行；未配置 → 视同 `--no-publish`，整个文件跳过。下文所有仓库路径 / URL 均为 Ray 的配置示例值，实际以配置为准。

## 仓库信息

- **路径**：`~/ray-research/`（已 clone）
- **GitHub URL**：https://github.com/kdsz001/ray-research
- **GitHub Pages**：https://kdsz001.github.io/ray-research/
- **可见性**：公开 Public
- **结构**：`{话题名}/{YYYY-MM-DD}-{slug}.html` + 每个话题一个 README.md

## 发布流程（5 步）

### Step 1 · 决定话题分组名

规则（按优先级）：
1. 用户在调用时显式指定 `--topic <名>` → 用这个名
2. 调研对象是单一产品/公司 → 用其名（小写 + 短横线，如 `typeless`、`wispr-flow`）
3. 调研对象是行业/赛道 → 用赛道短名（如 `ai-voice-input`、`ai-coding`）
4. 调研对象是人物 → 用人名（如 `pieter-levels`）
5. 不确定 → 在 Stage 0 让用户确认

**话题已存在时**：直接放进已有目录，文件名前缀日期保证不冲突。

### Step 2 · 准备文件结构 + 注入 sidebar

```bash
TOPIC="typeless"
DATE=$(date +%Y-%m-%d)
TARGET_DIR="$HOME/ray-research/$TOPIC"
TARGET_FILE="$TARGET_DIR/$DATE-$TOPIC.html"

mkdir -p "$TARGET_DIR"
cp "$LOCAL_REPORT" "$TARGET_FILE"
```

**生成报告 HTML 时必须在 `<head>` 注入这两行**（让全局 sidebar 生效）：

```html
<link rel="stylesheet" href="../assets/sidebar.css">
<script defer src="../assets/sidebar.js"></script>
```

放在 Google Fonts 的 `<link>` 之后、防 FOUC 主题 `<script>` 之前。**用相对路径 `../assets/`**（不要绝对 `/ray-research/...`，避免本地 file:// 协议失效）。

如果是话题 index.html 也加同样两行。如果是主 index.html（仓库根）—— 不加，主页本身是 landing 不需要 sidebar。

### Step 3 · 一条命令更新全部索引

仓库启用了 `.nojekyll`，每个目录都要有 index.html 入口 + README.md（GitHub 代码视图），外加 manifest.json 驱动全局 sidebar——一共 5 处索引。**全部用脚本统一更新，不要手工改**（手工改五处必漏，曾导致"报告上传了但 sidebar 看不到"）：

```bash
cd ~/ray-research

# 已有话题追加报告：
python3 scripts/add-report.py \
  --topic typeless --date 2026-06-11 \
  --file 2026-06-11-typeless-v2.html --title "更新版竞品调研"

# 新话题首次发布（多 4 个参数）：
python3 scripts/add-report.py \
  --topic wispr-flow --date 2026-06-11 \
  --file 2026-06-11-wispr-flow.html --title "初版竞品调研" \
  --topic-name "Wispr Flow" --tagline "AI 语音输入 · 竞品调研" \
  --desc "主页话题卡片的一段简介（80-150 字，含核心数字与判断）" \
  --conclusion "核心结论 1" --conclusion "核心结论 2" --conclusion "核心结论 3"
```

脚本一次更新 5 处：**manifest.json**（权威数据源）→ **话题 README.md** → **话题 index.html**（新话题自动从模板创建）→ **主 README.md** INDEX 区块 → **主 index.html** 话题卡片（报告数以 manifest 为准自动纠偏）。

脚本只追加、不重写，不会覆盖用户手工改过的内容。**脚本报错时的手工兜底**：按 manifest.json → 话题 README → 话题 index.html → 主 README → 主 index.html 的顺序手工补，格式参照 `typeless/` 话题的现有文件；其中 manifest.json 最关键（漏了 sidebar 就看不到新报告）。

### Step 4 · git commit + push

```bash
cd ~/ray-research
git add -A
git commit -m "$(cat <<'EOF'
feat({{topic}}): 新增 {{date}} {{title}}

{{核心结论 1-2 句}}

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin main
```

不要用 `--no-verify` / `--no-gpg-sign`（除非用户要求）。

### Step 5 · 告诉用户 URL

交付总结里必须包含：
```
本地路径：~/ray-research/{topic}/{file}
在线浏览：https://kdsz001.github.io/ray-research/{topic}/{file}（Pages build 约 30s-2min 后可访问）
仓库主页：https://github.com/kdsz001/ray-research
```

## 守则

1. **私密内容警告**：仓库是 Public——如果用户调研内容含私密决策（如自己公司战略、客户名单），先告知"这会发布到公开 GitHub"再继续，让用户决定要不要 `--no-publish`。
2. **同名报告处理**：同一天针对同一话题再做调研，文件名加 `-v2` / `-revised` 等后缀（如 `2026-05-10-typeless-v2.html`），不覆盖旧版。
3. **不要篡改用户已有内容**：仓库可能含有用户手动修改 / 添加的话题分组 / README。只 add / append，不 overwrite。
4. **commit 失败处理**：如果 push 被拒绝（remote 有新提交），先 `git pull --rebase origin main` 再 push。
5. **用户传 `--no-publish`** → 跳过 Stage 5，仅本地保留。

## 失败情况

- gh CLI 未认证 → 提示用户 `gh auth login`，本次跳过 publish
- 网络失败 → 本地 commit 完成但 push 失败，告知用户"已提交本地，下次 push"
- 仓库不存在 → 提示用户先运行初始 setup（不要自动创建）
