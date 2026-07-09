# ray-deep-research

> 一个 Claude Code Skill：把任意主题（产品 / 公司 / 赛道 / 人物 / 股票 / 加密项目）变成一份**多源验证、商业杂志风的 HTML 调研报告**，自动打开浏览器。

**核心定位**：不是"AI 帮我搜一下"，而是**派 4 个 AI 调研员并行下场 → 整合洞察 → 出一份能拿去做决策的报告**。

- **多源并行** —— 海外英文 / 中文社区 / 横向对比 / 团队融资同时挖
- **一手优先** —— 直接读官网 / Product Hunt / App Store，而非搜索缓存
- **视觉精度** —— 严肃商业杂志风 HTML（含夜间模式），不是 markdown 列表
- **自检迭代** —— 截图自查 → 修补 → 再截图，达到"完美"才交付
- **决策导向** —— 最后一定回答"我能不能做 / 该怎么做"

**效果预览**：<https://kdsz001.github.io/ray-research/>（用这个 skill 自动生成的公开报告库）

---

## 安装

分三档，从"装上就能用"到"满血"，**按你想要的质量选**。三档都不需要付费。

### 档位 0 · 最简（装上就能用）

```bash
git clone https://github.com/kdsz001/ray-deep-research-skill.git \
  ~/.claude/skills/ray-deep-research
```

然后**完全重启 Claude Code**，直接说「调研 Typeless」即可。

> 此档用 Claude 内置的 WebSearch / WebFetch 调研。反爬平台（小红书 / 知乎等）读不到，报告顶部会**如实标注"降级模式"**，不会假装数据齐全。

### 档位 1 · 推荐（+ 浏览器直读）

在档位 0 基础上，装一个浏览器引擎，任选其一：

```bash
# 方式 A：Playwright MCP（推荐，约 2 分钟）
claude mcp add playwright npx @playwright/mcp@latest
```

装完**完全重启 Claude Code**。有了浏览器，才能读小红书 / 知乎、核实一手数字——**这是这个 skill 的质量核心**。

> 方式 B：如果你装了 `web-access` skill，会自动优先用它（CDP 直读，作者的原生模式），无需额外配置。

### 档位 2 · 完整（+ 数据验证 + 自动发布）

在档位 1 基础上，按需再加：

1. **数据真实性验证** —— 装 [Codex CLI](https://github.com/openai/codex)，Stage 2.5 会用它独立复核融资 / 估值 / 用户量等高风险数字。
   *（没装也能跑，会自动改用一个独立的 Claude 子 Agent 兜底。）*

2. **个人报告库 + 自动发布** —— 建一个配置文件 `~/.config/ray-deep-research/config.json`：

   ```json
   {
     "browser": "auto",
     "library_path": "~/your-research-repo",
     "publish": {
       "enabled": true,
       "repo_path": "~/your-research-repo",
       "github_repo": "your-name/your-research-repo",
       "pages_url": "https://your-name.github.io/your-research-repo"
     },
     "degraded_ack": false
   }
   ```

   - `library_path`：开启"复用检查"——调研前先查你库里有没有近期同主题报告，避免重复烧钱。
   - `publish`：调研完自动 push 到**你自己的** GitHub 报告库 + GitHub Pages 在线浏览。
   - **不建这个文件也完全能用**：报告自动收进本地收藏夹 `~/ResearchLibrary/`——打开任何一份报告，侧边栏都列着你做过的全部报告；库首页是 `~/ResearchLibrary/index.html`。全部只存在你电脑上。

---

## 用法

直接用自然语言触发：

```
调研 Typeless
分析一下 PDD 这家公司
对比 Cursor 和 Windsurf
SPCX 值得打新吗
```

可选参数：

| 参数 | 作用 |
|------|------|
| `--type competitor` | 竞品调研（默认，覆盖面最广） |
| `--type investment` | 投资决策调研（股票 / IPO / 币，决策章为三档路径 + 触发条件） |
| `--type generic` | 通用兜底（行业 / 人物 / 其他） |
| `--quick` | 跳过数据验证 + 视觉自检，更快但质量不保证 |
| `--no-publish` | 只在本地生成，不发到 GitHub（私密内容用这个） |
| `--agents N` | 手动指定并行子 Agent 数量（1–8） |

Skill 会在开跑前用一句话告诉你「判断为 X 类型、预计跑 N 个子 Agent、约 M 分钟」，然后立即开始——想改再说就行。

---

## 依赖一览（全部可选，缺了自动降级，绝不静默糊弄）

| 想要的能力 | 需要装 | 缺了会怎样 |
|-----------|--------|-----------|
| 浏览器直读（读反爬平台、核实一手数据） | Playwright MCP 或 `web-access` skill | 降级用 WebSearch，反爬平台读不到，报告顶部标注 |
| 高风险数字独立复核 | Codex CLI | 改用独立 Claude 子 Agent 兜底 |
| 个人库复用 + 自动发布 | `~/.config/ray-deep-research/config.json` | 跳过复用检查，报告只留本地 |

---

## 共享库（可选）

如果你有库主发的**邀请码**，建一个 `~/.config/ray-deep-research/exchange.json`：

```json
{
  "api": "https://ray-research-registry-api.typefree.workers.dev",
  "invite_code": "inv_你的邀请码"
}
```

之后每次调研会先查共享库——别人调研过的标的直接看现成报告（几秒，省下几十分钟）。查询会以你的邀请码记录、供库主做统计。没有邀请码就跳过这节，skill 本地功能完全不受影响。

**你的报告永远只存在你电脑上，这个工具不会上传它们。** 想把某份报告分享到共享库？去共享库网站用邀请码连接后手动上传（上传页上线前可发给库主代传）——传不传、传哪份，都是你在网站上自己点的。

## 说明

- 所有报告为**研究用途，不构成投资 / 创业 / 商业决策建议**。
- 调研数据为生成时刻的快照，可能随时间变化。
- 发布功能默认关闭；开启后报告会进入你配置的**公开** GitHub 仓库，涉及私密内容请用 `--no-publish`。
