# 环境自检与模式判定（开跑前必做）

**为什么有这一层**：本 skill 的质量核心是浏览器直读（反爬平台、一手数字），但浏览器引擎因机器而异。原则：**一份代码，按环境自动分档；缺引擎时主动引导安装，不静默降级**——静默降级等于把用户默默留在低质量档。

---

## 配置文件

路径：`~/.config/ray-deep-research/config.json`（**可选**——不存在时全部走默认值，skill 照常能跑）。

```json
{
  "browser": "auto",
  "library_path": "~/ray-research",
  "publish": {
    "enabled": true,
    "repo_path": "~/ray-research",
    "github_repo": "kdsz001/ray-research",
    "pages_url": "https://kdsz001.github.io/ray-research"
  },
  "degraded_ack": false
}
```

（上面是 Ray 本人的配置示例。）

**无配置文件时的默认**：`browser: auto`（按下节探测）；无个人库 → 跳过 Stage 0.5；无 publish 配置 → 视同 `--no-publish`（只本地交付）；`degraded_ack: false`。

---

## 探测顺序（每次开跑时静默完成，秒级，不打扰用户）

1. **web-access skill 存在？** `test -e ~/.claude/skills/web-access/SKILL.md` → 模式 = **full / web-access**（CDP 直读，Ray 的原生模式）
2. **Playwright MCP 可用？** 检查会话工具列表是否含 `mcp__playwright__*`（deferred 工具也算；不确定时用 ToolSearch 搜 "playwright"）→ 模式 = **full / playwright**
3. **都没有** → 看配置 `degraded_ack`：
   - `true`（用户此前已确认降级）→ 模式 = **degraded**，直接开跑，报告按规则标注
   - `false` / 无配置 → **首次引导**（下节），这是唯一允许停下来问的时刻

---

## 首次引导（仅当两种引擎都缺、且用户从未确认过降级时，问一次）

> 检测到你还没有浏览器工具。本 skill 的核心能力（读小红书/知乎、核实一手数据）需要它。
> **(a) 现在安装 Playwright MCP（推荐，约 2 分钟）**：在终端运行
> `claude mcp add playwright npx @playwright/mcp@latest`
> 装完**完全重启 Claude Code**，再重新发起调研即可。
> **(b) 本次先用降级模式跑**：质量打折，报告顶部会如实标注；可记住这个选择（下次不再问）。
> **(c) 取消本次调研。**

- 用户选 (b) 且同意记住 → 写 `degraded_ack: true` 进配置文件（目录不存在先创建）。
- **登录态提示**（浏览器模式下按需说一次）：读小红书/知乎等平台的登录内容，需要用户在被控浏览器里**登录一次自己的账号**（一次性）。skill 永远不索取、不传输任何账号密码。

---

## `{{BROWSER_ACCESS}}` 替换表（Stage 1 dispatch 子 Agent 时按当前模式替换占位符）

**web-access 模式**：
> 必须加载 web-access skill 并遵循指引。

**playwright 模式**：
> 用 Playwright MCP 浏览器工具打开真实页面读取内容（工具名前缀 `mcp__playwright__`，未加载时先用 ToolSearch 搜 "playwright" 加载）。反爬平台（小红书 / 知乎 / Product Hunt 评论区 / Reddit 等）必须用浏览器直读，不要只依赖搜索摘要。某平台需要登录而浏览器未登录时，如实报告"该平台需登录，未能读取"，绝不编造。

**degraded 模式**：
> 本次环境无浏览器工具（降级模式）：用 WebSearch + WebFetch 尽力调研。搜索摘要不可全信——关键数字必须找到至少两个独立来源交叉印证，只有单一来源就标注"未交叉验证"。打不开的反爬平台（小红书 / 知乎 / 即刻等）如实写"无法访问"，绝不编造该平台的内容。

---

## 模式 × 各 Stage 行为

| Stage | full / web-access | full / playwright | degraded |
|-------|------------------|-------------------|----------|
| 0.5 复用检查 | 看 `library_path` 配置，无则跳过 | 同左 | 同左 |
| 1 子 Agent | 替换表第 1 段 | 替换表第 2 段 | 替换表第 3 段 |
| 2.5 数据验证 | 照常（Codex/Claude 审查与浏览器无关）；主 Agent 用 web-access 核查 | 照常；主 Agent 用 playwright 工具核查 | 照常跑审查；核查用 WebFetch 尽力，查不到的保留"未交叉验证"标注 |
| 4 CDP 自检 | 照 `self-check.md` 跑 | 可用 playwright 截图做简化自检（可选）；不可行则跳过并在交付说明 | 跳过，交付总结注明"未做视觉自检" |
| 5 发布 | 看 `publish` 配置，未配置视同 `--no-publish` | 同左 | 同左 |

---

## degraded 模式的诚实标注（铁律，不可省）

1. 报告顶部加 callout：
   > ⚠ 本报告为**降级模式**产物（未走浏览器直读）：数据可信度低于满血模式，中文社区章节可能缺失，关键数字请自行复核。
2. 交付总结里明说本次是降级模式、错过了什么。
3. 反爬平台内容大概率缺失 → 相关章节如实精简，套用 `agent-orchestration.md` 的"数据严重不足时的兜底"，不硬凑。
4. 元数据记 `degraded: true`（为将来共享库的可信度标注预留）。

---

## 给维护者

新增一种浏览器引擎（如 Chrome MCP）时：在"探测顺序"插入一行 + 在"替换表"加一段指令，其余不动。
