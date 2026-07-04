# Stage 2.5 · 数据真实性验证

**目标**：所有从网页扒下来的数据，在变成 HTML 报告之前，先经过一次独立审查 + 一手核实，确保数字不是 AI 幻觉、不是过时数据、不是搜索摘要的二手错误。

**为什么需要**：Ray 拿这些报告做投资 / 创业决策。融资金额、估值、用户量、股价错一个，决策就可能错。AI 从搜索结果或社交媒体扒数字时，容易"信第一眼看到的"——但第一眼看到的常常是过时新闻、混淆同名公司、或别的 AI 摘要的二次幻觉。

---

## 何时触发

**Stage 2 整合数据完成后、Stage 3 渲染 HTML 之前。**

时序：
```
Stage 1: 4 子 Agent 并行调研
   ↓
Stage 2: 主 Agent 整合 + 复刻分析
   ↓
【Stage 2.5: 数据真实性验证】  ← 本文档描述的环节
   ↓
Stage 3: 渲染 HTML
```

---

## 重点核查的"高 stake 数字"

只核查这些类型的数据点，**不要核查所有内容**（性价比低）：

| 类型 | 例子 | 为什么必须核 |
|------|------|------|
| 💰 融资 / 估值 / 轮次 | "$81M 累计、$7 亿估值、Series B" | AI 容易混淆同名公司、错搬旧数据 |
| 📈 用户量 / DAU / MAU / ARR / 营收 | "月活 1.2 亿、ARR $50M" | 公开数据滞后或夸大常见 |
| 🏢 创立时间 / 团队规模 / 总部 | "2024 年成立、5-15 人、Palo Alto" | LinkedIn / Crunchbase 之间常矛盾 |
| 📰 媒体报道 / 奖项 / 背书 | "App of the Year 2026"、"a16z 投资" | 营销话术常被当事实，但奖项可能不存在 |
| 📅 时效性数据 | 股价 / 市值 / PE / 流量 | 每天变，超过 1 周就过期 |
| 🗳 政策 / 法规 / 合规进度 | "HIPAA 已合规"、"CLARITY 法案 6 月签署" | 状态常变 |

**不核查**：用户评论原话、KOL 推文原文、官网 slogan、产品功能描述（这些"原文照搬"不会"错"）。

---

## 流程（4 步）

### Step 1 · 提取「关键数据清单」

主 Agent 把整合后的数据按上表 6 类提取成 markdown 清单：

```markdown
# 待核查数据清单 · {{TARGET}}

## 💰 融资 / 估值
- [F1] $81M 累计融资 (Wispr Flow) ← 来源：TechCrunch 2025-11-20
- [F2] $7 亿估值 (Wispr Flow) ← 来源：PitchBook
- [F3] 种子轮 $0.5M-$3M (Typeless, 估算) ← 来源：Hat-trick Capital 公开 check size 区间

## 📈 用户 / 营收
- [U1] 月访 1.1M (Typeless) ← 来源：SimilarWeb 2026-04
- [U2] Android 50万+ 下载 (Typeless) ← 来源：Google Play

## 🏢 公司
- [C1] 2024 年成立 (Typeless / Simply CA LLC) ← 来源：PitchBook 1166524-75

## 📰 媒体 / 奖项
- [M1] "App of the Year 2026" (Typeless, 客户评价里出现) ← 来源：Joe Borelli 引用

## 📅 时效性
- [T1] PH #1 of the Day @ 2025-11-18 (Typeless 桌面版首发)

## 🗳 政策 / 合规
- [P1] HIPAA / GDPR 已合规 (Typeless) ← 来源：trust.typeless.com
```

每个数据点必须有：编号 + 数字/事实 + 来源标注。

### Step 2 · 检测验证器可用性

```bash
which codex 2>/dev/null
```

- 有结果 → **走 Codex 路径**（Step 3A）
- 没结果 → **走 Claude fallback 路径**（Step 3B）

### Step 3A · Codex 验证路径（首选）

调用 Codex 做事实核查（不是代码 review）：

```bash
codex exec "IMPORTANT: This is a FACT-CHECKING task, NOT a code review. Do NOT read any files under ~/.claude/, ~/.agents/, .claude/skills/, or agents/.

I'm publishing a deep research report on {{TARGET}}. Before publishing, I need you to identify which of these data points are most likely to be inaccurate, outdated, or hallucinated.

For each suspect data point, output exactly:

[SUSPECT-{{id}}] <claim verbatim>
Likely issue: outdated | hallucinated | source-confused | original-source-missing | could-not-verify
Recommended action: <where to verify, e.g., 'check Crunchbase profile X' / 'verify on company investor relations page' / 'search SEC filing'>
Confidence: HIGH | MEDIUM | LOW

Use web search if available. Be ruthless — false positives are cheap (Ray will check), false negatives are expensive (wrong decisions).

DATA TO VERIFY:
{{datapoints_markdown}}

If a data point looks SOLID and well-sourced, do not flag it.
" -s read-only -c 'model_reasoning_effort="high"' --enable web_search > /tmp/codex-verify.txt 2>&1
```

注意：
- 用 `-s read-only`（Codex 不修改文件）
- 用 `high` reasoning effort（事实核查需要慎重）
- 用 `--enable web_search`（Codex 0.128+ 默认就有，但显式声明更稳）
- 输出捕获到 /tmp/codex-verify.txt 防止 background bash 吃 stdout

### Step 3B · Claude Fallback 路径

如果 Codex 不可用：派一个**独立的 Claude 子 Agent**（不是写报告那个 Agent）做同样的审查。

关键：**必须是独立子 Agent**——避免"出题人改卷"，自检盲区严重。

```
Agent({
  description: "数据真实性独立审查",
  prompt: """
你是一名独立审查员，不是写这份报告的那个 AI。任务：识别下面这些数据中最可能错的项。

待审查数据：
{{datapoints_markdown}}

按以下格式输出每个 suspect：
[SUSPECT-{{id}}] <claim verbatim>
Likely issue: outdated | hallucinated | source-confused | original-source-missing | could-not-verify
Recommended action: <具体核查路径，如 'check Crunchbase profile' / 'verify on SEC filing'>
Confidence: HIGH | MEDIUM | LOW

判断原则：
- 融资数字必须从一手数据库（Crunchbase/PitchBook/Tracxn/官方公告）确认
- 用户量 / 营收 / 估值如果只有单一来源 → 标 MEDIUM
- 奖项 / 背书（如 "App of the Year"）必须查原始榜单是否真存在该奖
- 时效性数据（股价 / 市值）如果引用超过 1 周 → 标 HIGH 可疑
- 政策 / 合规进度必须查最新状态

不要核查用户评论原话、KOL 推文原文、产品功能描述——这些原文照搬不会错。

如果某数据点本身就源自一手数据 + 标注充分，不要标 suspect。
""",
  subagent_type: "general-purpose",
  run_in_background: false  // 同步等待
})
```

### Step 4 · 主 Agent 逐项核查 + 修复

主 Agent 读取审查输出，对每个 suspect 用 `web-access` skill 实际核查：

```
对于每个 [SUSPECT-{{id}}]:
  1. 按 "Recommended action" 去原始来源核查
  2. 拿到核查结果后，按下表处理：
```

| 核查结果 | 修复动作 |
|---------|---------|
| 一手来源 + 数字一致 | 保留原数字，加标注「✓ 已交叉验证（来源 X，验于 2026-MM-DD）」 |
| 一手来源 + 数字不同 | 改为正确值 + 标注「✓ 已交叉验证（原数据矛盾，修正于 2026-MM-DD）」 |
| 找不到一手来源 | 保留数字但改为「{{原数字}}（**未交叉验证** · 出现在 {{原来源}}）」 |
| 一手来源显示已过时 | 改为「{{原数字}}（已过时，最新为 {{新数字}}，更新于 {{日期}}）」 |
| 整个数据点完全是 hallucination | **删除**该数据点，在 HTML 顶部"⚠ 数据真伪提醒"区块加一条说明 |

---

## 循环上限（防陷入死循环）

```
最多 3 轮 review → fix → review。

退出条件（任何一个先满足都停）：
- 当前轮 Codex/Claude 报告"无 suspect"或所有 suspect 都是 LOW
- 已经跑了 3 轮
- 主 Agent 判断剩余 suspect 都已经"尽力核查仍找不到一手来源"——这种情况下保留"未交叉验证"标注即可
```

3 轮上限的原因：
- 1 轮：找到第一批明显问题
- 2 轮：找到修复后引入的新问题（罕见但有）
- 3 轮：兜底
- 超过 3 轮通常是 Codex/Claude 在挑刺无关紧要的小事，边际收益递减

---

## 输出格式约束

修复后的数据在 HTML 中**必须保留可信度信号**：

```html
<!-- 已交叉验证 -->
<div class="metric-row">
  <div class="label">融资金额<span class="src">来源 Crunchbase ✓ 已交叉验证 2026-05-18</span></div>
  <div class="value data">$81M</div>
</div>

<!-- 未交叉验证（但保留） -->
<div class="metric-row">
  <div class="label">月访问量<span class="src">SimilarWeb · ⚠ 未交叉验证</span></div>
  <div class="value">1.1M</div>
</div>

<!-- 在 callout 块里更显眼 -->
<div class="callout warn">
  <div class="callout-label">⚠ 数据真伪提醒</div>
  <p>本报告中以下数据为<strong>单一来源、未能交叉验证</strong>，请谨慎采信：</p>
  <ul>
    <li>用户量 X（仅 SimilarWeb）</li>
    <li>团队规模 Y（仅 LinkedIn 信号推断）</li>
  </ul>
</div>
```

每份报告 footer 加一行：
```
本报告 N 个高 stake 数据点已通过 Stage 2.5 独立验证（X 个交叉验证 / Y 个未验证）
```

---

## 与其它 Stage 的交互

- **不影响 Stage 1**：子 Agent 还是各自调研，不要让他们自己内部验证（会拖慢、且容易"自我安慰"）
- **影响 Stage 3**：HTML 渲染时需要带上验证标注（更新 `html-template.md` 的 Components 章节）
- **影响 Stage 4**：CDP 自检时多看一项——"⚠ 未交叉验证"标注是否清晰可见
- **影响 Stage 5**：发布时 commit message 可以提"N 个数据点交叉验证"作为信号

---

## 守则

1. **绝不为了"看起来权威"删除可疑数据**——保留 + 标注「未交叉验证」始终优于偷偷删除。Ray 需要看到全部信息再判断。
2. **核查耗时是合理代价**——Stage 2.5 大约会让总流程多 5-10 分钟，但比交付错误数据让 Ray 做错决策划算太多。
3. **找不到一手来源 ≠ 数据错**——只是不能背书。明确标注后保留即可。
4. **`--quick` 模式跳过 Stage 2.5**——如果用户传 `--quick`，跳过验证（用户已明确接受"速度优先"）。
5. **Codex / Claude 都跑 3 轮无 high suspect → 视为通过**，可以进入 Stage 3。
