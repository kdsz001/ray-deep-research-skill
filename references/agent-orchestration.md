# 多 Agent 并行编排规则

## 核心原则

**并行子 Agent 是这个 skill 的真正引擎**（数量按 SKILL.md Stage 0 表格动态定）——它们才是节省时间的部分。主 Agent 不要替子 Agent 做调研，主 Agent 只做 3 件事：
1. 调度（dispatch + 设兜底）
2. 整合（拿到所有结果后做战略分析）
3. 渲染（HTML + 自检）

## 一次性 Dispatch 全部子 Agent

**关键**：所有子 Agent 必须在同一条消息里 `run_in_background: true` 全部 dispatch 出去——不要串行（一个完成再发下一个），那会浪费 60-80% 时间。

主 Agent 同时可以干这些（不冲突）：
- WebFetch 抓官网首页 / pricing 页 / about 页
- WebFetch 抓一两篇关键评测文章
- TaskCreate 建立任务清单

不可以干这些（会与子 Agent 冲突）：
- 重复子 Agent 已经在做的工作（如自己再去搜 PH 评论）
- 给子 Agent 没明确说要做的工作（让它"顺便"做更多）

## 子 Agent prompt 写法守则

参考 web-access skill 的 sub-agent prompt 守则：

1. **目标导向，不规定步骤**：写"获取 / 调研 / 了解"，不要写"搜索 / 抓取 / 爬取"。后者会把子 Agent 锚到 WebSearch，错过 CDP 直访的机会。
2. **必须 inline 完整 prompt**，不要写"按照 X 文档执行"——子 Agent 拿不到主 Agent 的上下文。
3. **每个 prompt 必须包含 `{{BROWSER_ACCESS}}` 能力指令段**（dispatch 时按 `environment.md` 替换表填充）——不然子 Agent 不会主动用浏览器直读。
4. **明确输出格式**：要求中文 + 结构化 + 带来源链接 + 没找到就说没找到。
5. **明确边界**：告诉子 Agent 不要做哪些事（如不要重复其它 Agent 的工作、不要瞎编数字）。
6. **指定落盘文件**：prompt 末尾给出输出文件路径（见下节"结果落盘"），完整结果写文件，返回消息只要摘要。

## 结果落盘（防上下文压缩丢素材）

**为什么**：行业全景模式 6-8 个 Agent 跑 30-45 分钟，回来的素材量巨大。主 Agent 的上下文（工作记忆）满了会被自动压缩，压掉的往往正是某个子 Agent 的原始素材——到 Stage 3 写报告时只剩模糊印象，调研等于白跑。落盘后文件随时可重读，不怕压缩。

**怎么做**：
1. dispatch 前：`mkdir -p /tmp/ray-research/{slug}`（slug 同 publish 话题名）
2. 每个子 Agent 的 prompt 末尾加一段：
   > 把完整调研结果（含全部来源链接）写入文件 `/tmp/ray-research/{slug}/agent-{x}.md`，然后在返回消息里只写 ≤500 字核心摘要 + 这个文件路径。
3. Stage 2 整合时：主 Agent 用 Read 读全部 `agent-*.md` 落盘文件（**不要只凭返回摘要整合**），整合大纲写入同目录 `outline.md`
4. 失败重试时，旧文件就是"上次调研到哪了"的证据，重派的 Agent 可以接着补

## 兜底唤醒后的处置（1500s 到点子 Agent 还没齐）

ScheduleWakeup 唤醒后先查 TaskList / TaskOutput，按情况办：

| 情况 | 处置 |
|------|------|
| 全部已完成（只是通知漏发） | 正常进 Stage 2 |
| 少数未完成（≤ 1/3），其余已齐 | 再设一次 1500s 唤醒，**最多再等一轮**；第二次到点仍未完成 → 停掉该 Agent，检查其落盘文件里已有的部分结果，够用就带着用、不够就按"失败重试"重派一次 |
| 多数未完成 | 再设一次 1500s 唤醒等待，不要立即批量重派（重派 = 成本翻倍）；第二次到点仍未完成 → 如实告知用户现状，问继续等还是带现有素材出精简版 |

**原则：宁可出"标注了缺失维度"的报告，不要无限等待，也不要假装素材齐了。** 带病整合时必须在报告顶部 callout 注明"X 维度调研未完成，本章基于部分素材"。

## 兜底 ScheduleWakeup

**所有子 Agent dispatch 后立刻设 ScheduleWakeup**：
- delaySeconds: **1500** (25 分钟)——子 Agent 一般在 5-15 分钟完成，1500s 是兜底
- prompt: 普通模式写"继续 ray-deep-research 调研 {主题}：检查子 Agent 完成状态，按 agent-orchestration.md 的兜底处置规则继续流程"；loop 模式则传原始 /loop 指令 verbatim
- reason: 简短说明"在等 N 个子 Agent 完成"

子 Agent 完成时 task-notification 会自动唤醒主 Agent，**不必到点**。

## TaskList 状态管理

每个子 Agent 启动 → TaskUpdate 状态为 `in_progress`
每个子 Agent 完成 → TaskUpdate 状态为 `completed` + 用 task-notification 里的核心发现做简短回复

## 整合时机

**所有子 Agent 都完成后才开始整合**——不要边收边写，会导致后到的数据反复推翻已写内容。

整合前的 sanity check：
- 哪两个子 Agent 的结论矛盾？（必须 reconcile）
- 哪些数字来源唯一？（标注为"未交叉验证"）
- 哪些是 AI 摘要 hallucination？（特别是融资金额）

## 子 Agent 数量调节

**数量判断以 SKILL.md Stage 0 的表格为唯一标准**（那张表更细、带预计耗时）。本文件不再重复，避免两处数字打架。

competitor preset 默认 4，investment preset 默认 4，如果主题特别简单可以减；generic preset 默认 3。

## 失败重试

如果某个子 Agent 完成时返回的内容明显不足（如 < 500 字 / 没有任何来源链接 / 全部"未找到"）——**重新 dispatch 一次同主题的子 Agent**，prompt 里加："上次调研结果不足，请更主动地用 CDP 浏览器访问真实页面。"

不要因为单个子 Agent 失败就放弃整个调研。

## 数据严重不足时的兜底

区别于上面的"单个 Agent 失败"——这里指**多数子 Agent 都返回"信息很少 / 大量未找到"**（常见于极冷门产品、刚上线的新品、刻意低调的公司、已停运项目）。

**不要硬撑 12 章**——填空式扩写最容易编造数字，直接违背 Stage 2.5 的数据真实原则。改为：

1. 出一份**精简版**：只保留有真实素材支撑的章节（通常是 Hero + Quick Facts + 有限的公司档案 + 决策建议），砍掉没料硬凑的章节
2. 报告顶部加一条 callout：「⚠ 本主题公开信息有限，以下为可获取范围内的调研，未覆盖部分已注明」
3. 交付时如实告诉用户："{主题} 公开信息太少，做了精简版而非完整报告"
4. 给出"为什么信息少"的判断（太新 / 太小众 / 刻意低调 / 已停运）——这本身对决策也有价值
