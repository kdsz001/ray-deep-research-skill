---
name: ray-deep-research
description: Ray 的深度调研引擎。任意主题（产品 / 公司 / 赛道 / 人物 / 技术 / 股票 / 加密项目）的多源深度调研，产出严肃商业杂志风 HTML 报告并自动打开浏览器。Use when user says '调研 X' / '调查这个产品' / '研究这个项目' / '分析 X 这家公司' / '对比 X 和 Y' / '深度调研' / '帮我看看 X 怎么样' / '想做一个跟 X 类似的产品' / '竞品调研' / '行业调研' / 'deep research' / 'competitive analysis' / 'market research' / '出一份调研报告', or provides a product URL / 公司名 / 赛道关键词 with intent to do thorough multi-source research and get a polished HTML deliverable. 只要交付物是一份完整调研报告就用本 skill（含股票/币的投资决策类调研，不要分流到其它同名 deep-research skill）；唯一例外：加密项目的合约安全 / 土狗快筛 / 撸毛空投等即时操作类问题 → 用 ray-crypto。
---

# Ray 深度调研引擎

把任意调研主题转化为**多源验证 + 视觉化呈现 + 决策导向**的 HTML 报告。

**核心定位**：不是"AI 帮我搜一下"，而是**"派 4 个 AI 调研员并行下场 → 整合洞察 → 出一份能拿去做决策的报告"**。

**与普通 search 的本质区别**：
- 多源并行（海外英文 / 中文社区 / 横向对比 / 团队融资同时挖）
- 一手优先（直接读官网/PH/SimilarWeb/App Store 而非搜索缓存）
- 视觉精度（严肃商业杂志风 HTML，不是 markdown 列表）
- 自检迭代（CDP 截图自查 → 修补 → 再截图，达到"完美"才交付）
- 决策导向（最后一定回答"我能不能做 / 该怎么做"）

---

## 输入

任意形式：
- 产品名（"Typeless"、"Cursor"、"Granola"）
- 公司名（"OpenAI 的 enterprise 业务"、"硅基流动"）
- 赛道关键词（"AI 语音输入法"、"AI 编程工具 2026"）
- 人物（"Sam Altman 最近 6 个月动向"、"Pieter Levels 在做什么"）
- 技术 / 方法论（"MCP 协议生态现状"、"Agent SDK 各家方案对比"）
- URL（官网 / Twitter / GitHub）
- 多个组合（"对比 Wispr Flow 和 Typeless"）

---

## 调用参数

- **无参数**：自动识别主题类型，默认走 `competitor` preset（最常用）
- `--type competitor` —— 强制走竞品调研模板（4 子 Agent，12 章结构，其中中国市场、隐私争议两章按需出现）
- `--type investment` —— 投资决策调研模板（4 子 Agent，12 章结构，决策章为三档路径 + 触发条件）
- `--type generic` —— 强制走通用兜底模板（3 子 Agent，弹性章节）
- `--type industry` —— 行业/赛道调研（无专属 preset，用 generic 模板承载 + 弹性章节）
- `--type person` —— 人物调研（无专属 preset，用 generic 模板承载 + 弹性章节）
- `--quick` —— 跳过 Stage 2.5 数据验证 + Stage 4 CDP 自检 loop，更快但数据与视觉不一定有保证
- `--no-open` —— 生成 HTML 但不自动开浏览器
- `--no-publish` —— 不 push 到 GitHub 仓库（仅本地保留，适合私密内容）
- `--topic <名>` —— 显式指定话题分组名（覆盖自动推断）
- `--agents N` —— 显式指定子 Agent 数量（覆盖自动判断），N = 1-8

---

## 环境自检与模式（开跑前必做）

按 `references/environment.md` 静默完成（秒级）：探测浏览器引擎（web-access → Playwright MCP → 无）+ 读配置文件 `~/.config/ray-deep-research/config.json`（可选），确定本次模式：

- **full**（任一浏览器引擎可用）→ 全流程照常
- **degraded**（无引擎且用户已确认降级）→ WebSearch/WebFetch 尽力调研，报告顶部加"⚠ 未走浏览器直读"标注
- **首次缺引擎** → 停下来引导安装（仅此一次，话术见 environment.md）

子 Agent prompt 里的 `{{BROWSER_ACCESS}}` 占位符按 environment.md 替换表填充。个人库（Stage 0.5）与发布（Stage 5）是否启用同样由配置决定——无配置时跳过 0.5、视同 `--no-publish`。

---

## 工作流（必须按顺序）

### Stage 0 · 主题解析 + preset 选择 + Agent 数量判断

1. **解析输入**：从用户消息提取主题、类型暗示、URL
2. **判类型**：
   - 出现"值不值得买 / 该不该投 / 打不打新 / 投资价值"，或标的是股票 ticker / 上市及拟上市公司 / 主流加密资产 → `investment`
   - 出现"竞品 / 对比 / 想做和 X 一样"→ `competitor`
   - 出现"行业 / 赛道 / 市场" → `generic`（行业调研，弹性章节）
   - 出现具体人名 → `generic`（人物调研，弹性章节）
   - 不确定 → 默认 `competitor`（覆盖面最广，对错都有用）
   - **investment vs competitor 的判据是意图不是标的**："调研 Cursor 想做一个类似的" → competitor；"Cursor 母公司要 IPO 了值得打吗" → investment
3. **加载对应 preset**：读取 `references/preset-{type}.md`
4. **判断 Agent 数量**：按下表自动选；如用户传 `--agents N` 直接用 N（覆盖自动判断）

   | 主题特征 | Agent 数 | 例子 | 预计耗时 |
   |---------|---------|------|---------|
   | 简单事实 / 单点查询 | 1-2 | "Anthropic 最近发了几个 Sonnet 版本"、"X 公司创始人是谁" | 5-8 分钟 |
   | 单一产品 + 普通赛道 | 4 | "调研 Typeless"、"调研 ima" | 15-20 分钟 |
   | 单一产品 + 火热赛道 | 5 | "调研 Cursor"、"调研 Granola"（社区反馈维度多） | 20-25 分钟 |
   | 投资标的（股票 / IPO / 币） | 4-5 | "SPCX 值得打新吗"、"舜宇光学现在能买吗"（业务多元的大公司取 5） | 20-30 分钟 |
   | 跨产品对比 | 5-6 | "Cursor vs Windsurf vs Cline" | 25-30 分钟 |
   | 行业 / 赛道全景 | 6-8 | "AI 编程工具 2026"、"AI 语音输入法赛道" | 30-45 分钟 |
   | 人物 / 个人深度 | 2-3 | "Pieter Levels 在做什么"、"Sam Altman 最近 6 个月动向" | 10-15 分钟 |

   判断规则：
   - 数量 < preset 默认（competitor 4 / investment 4 / generic 3）→ 跑前 N 个 Agent，按 preset prompt 排序优先级取
   - 数量 > preset 默认 → 复用现有 prompts + 增加额外维度（如开发者社区 / 行业分析师视角 / 历史对比 / 监管政策等）

5. **透明告知 + 默认接受**：用一句话告诉用户决策：
   > "准备调研 **X**，判断为 **[Y 类型]**，预计跑 **N 个子 Agent**（约 M 分钟）。开始。"

   然后**立即开始 dispatch，不等用户回应**、**不要弹 AskUserQuestion**（唯一例外：Stage 0.5 复用检查命中已有报告时，先等用户定夺）。用户如果想改才会主动说"用 6 个" / "改用 generic preset"——再调整 + 重新 dispatch。

   这个设计的核心：**默认零摩擦 + 永远透明 + 始终允许 override**。

### Stage 0.5 · 复用检查（避免重复烧钱）

**在 Stage 0 判断之后、Stage 1 dispatch 之前执行。** 这是 Stage 0 "立即 dispatch 不等回应" 的唯一例外——命中已有报告时值得停下来问一句，因为重跑整份成本高（时间 + token）。

**前提**：需要个人报告库（配置 `library_path`，Ray 为 `~/ray-research`）。未配置或目录不存在 → 跳过本步直接进 Stage 1。

1. 直接搜权威索引：`grep -i "{产品/公司名}" ~/ray-research/manifest.json`（中英文名都搜一遍——manifest 是仓库唯一权威索引，比"猜 slug 再 ls 目录"可靠，猜错 slug 会漏检导致整份重跑）
2. 命中后读该话题的 `reports` 数组，拿到最新报告的日期与文件名
3. **若存在近期报告（≤ 30 天）**：用一句话告知 + 给三选项，**等用户回应**：
   > "仓库里已有 **{date}** 的《{title}》。要 (a) 全新重做 / (b) 只更新有变化的部分（融资 / 口碑 / 排名 / 流量）/ (c) 先看旧版？"
4. **无报告 / 报告较旧（> 30 天）/ 用户选 (a)** → 正常进入 Stage 1，dispatch 全部子 Agent
5. **用户选 (b) 只更新** → 只 dispatch 与时效数据相关的子 Agent（团队融资、口碑反馈），复用旧报告的结构性章节（产品定位、技术、竞品格局），整合时把新数据替换进旧版，文件名加 `-v2` 后缀（见 `publish.md` 守则 2）
6. **用户选 (c) 看旧版** → 直接 `open` 旧报告，结束本次调研

**共享库复用（若配了 `~/.config/ray-deep-research/exchange.json`）**：本地库检查之后（朋友无 `library_path`、跳过了本地检查的直接走这步），按 `references/exchange.md` 查共享库 registry —— 命中给"看现成 / 重跑"二选一（看现成则 `open` url + 埋点）。共享库故障绝不阻塞调研。

### Stage 1 · 并行调研编排

按 preset 中的 sub-agent prompts 章节，**一次性 dispatch 所有子 Agent 进入 background**。

子 Agent 调度规则详见 `references/agent-orchestration.md`。核心原则：
- dispatch 前先 `mkdir -p /tmp/ray-research/{slug}`，每个子 Agent 的 prompt 末尾指定输出文件路径（完整结果写文件，返回消息只要 ≤500 字摘要）——防长任务上下文压缩丢素材
- 主 Agent 同时抓官网/主页核心事实（不要等子 Agent）
- 子 Agent 数量 = Stage 0 第 4 步判断结果（不再写死 preset 默认）
- 全部 `run_in_background: true`
- 用 ScheduleWakeup 设 1500s 兜底，task-notification 自动唤醒；唤醒后若仍有子 Agent 未完成，按 `agent-orchestration.md` 的"兜底唤醒后的处置"规则办
- 每个子 Agent 完成时更新 TaskList

### Stage 2 · 整合 + 复刻分析

所有子 Agent 完成后：
1. 读取 `/tmp/ray-research/{slug}/agent-*.md` 全部落盘结果（**不要只凭返回摘要整合**——摘要丢细节），整合成大纲写入同目录 `outline.md`。落盘的意义：上下文被压缩时素材随时可重读，40 分钟的调研不会白跑
2. 按所选 preset 的决策章节模板做战略分析（competitor：复刻可行性 + Path A/B/C；investment：估值 + 三档路径 + 触发条件；generic：actionable insights）
3. 一手来源校验：每个数字至少标注来源；明显幻觉（如"$30M Series A 没有依据"）必须做风险提示

### Stage 2.5 · 数据真实性验证（**必跑**，除非 --quick）

按 `references/data-verification.md` 流程：

1. **提取高 stake 数据清单**：把整合后的数据按 6 类（融资/用户量/公司档案/媒体奖项/时效性/合规）提成 markdown 清单
2. **检测验证器**：`which codex` 有结果 → 走 Codex；没有 → 派独立 Claude 子 Agent 做 fallback
3. **独立审查**：让审查器（Codex 或独立子 Agent）输出 suspect 清单，每条含 likely issue + recommended action + confidence
4. **逐项核查 + 修复**：主 Agent 用浏览器工具去原始来源核查每个 suspect（按 environment.md 当前模式选工具；degraded 模式用 WebFetch 尽力核查，查不到的保留"未交叉验证"标注），按规则处理：
   - 已交叉验证 → 保留 + 加"✓ 已交叉验证"标注
   - 数字不同 → 改正 + 标注
   - 找不到原始来源 → 保留数字 + 标"⚠ 未交叉验证"（**不要删除**）
   - 整个数据是 hallucination → 删除并在 HTML 顶部加"⚠ 数据真伪提醒"
5. **循环上限 3 轮**：review → fix → review，无 HIGH suspect 或 3 轮后退出

**这一步是数据质量的核心防线**。Ray 拿这些报告做投资 / 创业决策，融资 / 估值 / 用户量 / 股价错一个就可能错决策。绝不能跳。

### Stage 3 · 渲染 HTML

**复制 `references/template.html` 骨架，只填内容区**——CSS / JS / 夜间模式 / 打印样式 / sidebar 注入都已在骨架里固定，**不要从零重写样式**（每次重写 2000 行就是每次重新引入 bug 的机会）。组件写法与设计规范见 `references/html-template.md`，章节结构按 preset。

输出路径：`~/Downloads/{主题安全名}-research-{YYYYMMDD}.html`

主题安全名规则：去掉空格 + 中文转拼音/原样 + 全小写 + 短横线连接。

### Stage 4 · CDP 自检 + 迭代（除非 --quick）

按 `references/self-check.md` 流程（web-access 模式专属；playwright 模式可用其截图做简化自检，degraded 模式跳过并在交付时说明——见 environment.md 行为矩阵）：
1. 用 web-access skill 的 CDP API 在后台 tab 加载 HTML
2. 截图首屏 + Quick Facts + 几个关键章节
3. 视觉评估：是否有显示 bug、中文换行不当、对比度不够、章节遗漏
4. 发现问题 → Edit 修补 → 再截图
5. 直到自评满意（Quick Facts 速览板渲染正常 + TL;DR 黑块对比强烈 + 表格信息密度合理）
6. 关闭 CDP tab

### Stage 5 · 发布到 GitHub 仓库 + 交付

按 `references/publish.md` 流程。**前提**：配置文件里 `publish.enabled=true` 才执行；未配置 → 视同 `--no-publish`，跳过 1-4 步只做本地交付（5-7 步）。

1. **决定话题分组名**（优先级：用户 --topic > 产品/公司名 > 赛道短名 > 人物名 > 不确定时让用户确认）
2. **准备文件结构**：复制 HTML 到 `~/ray-research/{topic}/{YYYY-MM-DD}-{slug}.html`
3. **运行 `scripts/add-report.py` 一键更新全部 5 处索引**（manifest.json / 话题 README / 话题 index.html / 主 README / 主 index.html）——**不要手工改**，手工改五处必漏（详见 `publish.md`，含脚本报错时的手工兜底顺序）
4. **git add + commit + push** 到配置的发布仓库 main 分支（Ray：`kdsz001/ray-research`）
5. `open` 打开**仓库里那份** `~/ray-research/{topic}/{file}.html`（除非 --no-open）——不要打开 Downloads 工作副本，sidebar 资源是相对路径，只有仓库目录结构下才能加载
6. PushNotification 通知用户（防止用户已离开）
7. 简短交付总结：核心发现 3 条 + 本地路径 + **GitHub Pages URL**（https://kdsz001.github.io/ray-research/{topic}/{file}）+ 建议下一步

**注意**：仓库公开。如调研涉及用户的私密决策，提前提醒用户，让他选 `--no-publish`。

8. **上传共享库（若配了 exchange）**：交付后按 `references/exchange.md` 问一句"是否上传到共享库"——同意则内联 sidebar + 算 content_hash + `POST /upload`；私密调研不传。共享库故障不影响已完成的本地交付。

---

## Preset 系统

每个 preset 是一个独立 Markdown 文件，包含**5 个必有部分**：

```
1. 适用场景            一句话说清这 preset 处理什么
2. 子 Agent prompts    每个子 Agent 的完整 prompt（直接 inline，不抽象）
3. 章节结构            HTML 报告应该有哪些章节、什么顺序
4. Quick Facts 字段    速览板 12 格的标签 + 数据类型
5. 决策建议格式        最后一章的特定结构（Path A/B/C 或其他）
```

**当前可用 preset**：
- `references/preset-competitor.md` — 竞品调研（默认）
- `references/preset-investment.md` — 投资决策调研（股票 / IPO / 币）
- `references/preset-generic.md` — 通用兜底

**新增 preset 流程**：复制 generic preset → 改 5 个部分 → 在 SKILL.md 加 `--type X` 入口。

---

## References 索引

| 文件 | 何时加载 |
|------|---------|
| `references/environment.md` | **开跑前环境自检（必读）**：模式判定 / 首次引导安装 / {{BROWSER_ACCESS}} 替换表 |
| `references/preset-competitor.md` | 走 competitor preset 时 |
| `references/preset-investment.md` | 走 investment preset 时（股票 / IPO / 币的投资决策） |
| `references/preset-generic.md` | 走 generic preset 时 |
| `references/agent-orchestration.md` | Stage 1 编排子 Agent 时 |
| `references/data-verification.md` | **Stage 2.5 数据真实性验证（必读）** |
| `references/template.html` | **Stage 3 渲染的起点骨架（复制后填内容）** |
| `references/html-template.md` | Stage 3 填内容时的组件与设计规范 |
| `references/self-check.md` | Stage 4 CDP 自检时 |
| `references/publish.md` | Stage 5 发布到 GitHub 时 |
| `references/sample-output.html` | 视觉参照（已含 light + dark 双模式） |
| `references/exchange.md` | **Stage 0.5 查共享库 / Stage 5 上传共享库**（配了 exchange.json 时） |

---

## 风险点 & 守则

1. **不要捏造数字**。融资金额、用户量、估值 — 找不到一手来源就标"未披露 / 估算"，明确标注估算逻辑
2. **不要对营销话术信以为真**。"App of the Year"、"#1 in X"等都要回去 PH/榜单原页面验证
3. **不要忽略中文社区**。即使主体是海外产品，中文圈的反应往往揭示中国市场可行性
4. **不要把"全部一致好评"当真实**。Product Hunt 评论里 maker 互捧严重，真实口碑要看 Trustpilot / Reddit / 知乎
5. **隐私 / 安全争议是必查项**。AI 工具尤其。逆向工程 / 数据上传 / 权限滥用是后来者的品牌切入点
6. **决策导向**。报告最后一定要回答"我能做吗 / 该怎么做"。如果纯描述事实就失去 skill 的价值
7. **不要省 Stage 4 自检**。这是从"完成"到"完美"的关键一步，除非用户显式 --quick
8. **所有难懂的词 + 复杂的概念都要讲人话**。读者是产品型创业者、外行——他常调研自己不懂的领域，报告堆术语等于白做。两条硬规则：
   - **(a) 专业术语首次出现加括号白话注解**。不只金融商业词（轮次名、估值、ARR、PMF、CAC、LTV、PE/VC 阶段等），**也包括技术词和领域黑话**（如 RAG、模型蒸馏、Agent、套壳、扩散模型、L2、TVL 等——凡是外行不能秒懂的都算）。例："种子轮（公司最早期融资，通常几十万到几百万美元）"、"ARR（一年能稳定收多少订阅费）"、"RAG（让 AI 先查资料再回答，类似开卷考试）"。**只在首次出现时加注**，后续不再重复，避免冗余。
   - **(b) 复杂的机制 / 商业模式 / 技术原理，光给定义还不够，必须打个比方**。凡是"读完定义仍会懵"的地方，配一句"就像……"的类比。例："飞轮效应（就像滚雪球：用户越多→数据越多→产品越好→吸引更多用户）"、"套壳（自己不造发动机，买别人的 AI 模型套个壳，类似贴牌）"。
9. **所有财务数字必须有 USD 锚点**。任何非美元数字（人民币 / 日元 / 韩元 / 欧元 / 英镑等）必须以**"原币 + 括号 USD 等价"**形式呈现。例："月付 ¥84（约 $11.7）"、"估值 ¥2000 亿（约 $1.4B）"、"年薪 ¥1500 万（约 $10.4 万）"。引用他人原话（用户评论、KOL 推文、媒体报道）保留原文不动，只对调研员自己写的部分应用此规范
10. **Agent 数量按主题动态调，不要每次都用同一个数**。数量以 Stage 0 那张表为**唯一标准**（不在其它地方重复具体数字，防多处打架）。每次都要在 Stage 0 透明告知用户预计数量，给他 override 机会（说话或 `--agents N`）
11. **料不够时不硬凑**。如果多数子 Agent 都没挖到实质内容（极冷门 / 太新 / 刻意低调的主题），出精简版 + 如实告知用户，绝不填空式扩写编造数字——这直接违背 Stage 2.5 的数据真实原则（详见 `references/agent-orchestration.md` 的"数据严重不足时的兜底"）

---

## 一键自查清单（提交前过一遍）

- [ ] 环境自检已完成、模式已定（degraded 模式：报告顶部已加"⚠ 未走浏览器直读"callout）
- [ ] 主题已确认 + preset 已选择 + 已告诉用户预计时长
- [ ] Stage 0.5 复用检查已做（仓库有 ≤30 天同主题报告则已问用户：重做 / 只更新 / 看旧版）
- [ ] 已按 Stage 0 表格判定的数量并行 dispatch 子 Agent
- [ ] 子 Agent 结果已落盘 `/tmp/ray-research/{slug}/agent-*.md`，整合大纲已写 `outline.md`
- [ ] 主 Agent 同时抓了官网核心事实
- [ ] ScheduleWakeup 兜底已设置
- [ ] 所有子 Agent 完成后才开始整合
- [ ] **Stage 2.5 数据验证已跑**（除非 --quick）：高 stake 数据清单 → Codex/独立子 Agent 审查 → 逐项核查 → 标注"已交叉验证"或"未交叉验证"
- [ ] HTML 包含 Quick Facts 速览 + TL;DR 黑块 + 至少一个时间线/对比表
- [ ] 决策建议有具体行动指南（Path A/B/C 或 30 天 checklist）
- [ ] **外行可懂性**：随机抽查 3 处专业术语/复杂段落，确认都有白话注解或比喻，没有则补上
- [ ] CDP 自检至少 3 张截图（首屏、中段、末段）
- [ ] HTML 基于 `references/template.html` 骨架生成（自动保证 `<main>` 容器、light + dark 双模式、sidebar 注入——填内容时不要改动骨架部分）
- [ ] 已发布到 GitHub 仓库（除非 --no-publish）+ 已运行 `scripts/add-report.py` 更新全部索引
- [ ] 共享库已查（配了 exchange 时；命中已给"看现成 / 重跑"二选一 + 埋点）
- [ ] 跑完已静默报 run 事件 + 已问是否上传共享库（配了 exchange 时）
- [ ] open 命令打开本地 HTML + PushNotification 通知
- [ ] 交付总结 ≤ 250 字，含 3 条核心发现 + 本地路径 + GitHub Pages URL
