# Stage 4 · CDP 自检 + 迭代 Loop

**这是从"完成"到"完美"的关键一步**。除非用户显式 `--quick`，必须执行。

## 前置条件

- HTML 已生成在 `~/Downloads/{name}-research-{YYYYMMDD}.html`
- web-access skill 的 CDP Proxy 已运行（如未运行，先 `bash ~/.claude/skills/web-access/scripts/check-deps.sh`）

**sidebar 资源 404 属预期，不要修**：自检阶段报告还在 Downloads，`<head>` 里的 `../assets/sidebar.css` / `sidebar.js` 是为发布后的仓库目录结构准备的相对路径，此时 404 是正常的（静默失败，不影响主体渲染）。不要因此改路径或删注入——发布到 `~/ray-research/{topic}/` 后它们自然生效。

**CDP 起不来时的降级**：check-deps 修复后 CDP 仍不可用 → **跳过本 Stage，照常走 Stage 5 交付**，但交付总结里必须明确写"本次未做视觉自检，建议自己打开报告过一眼"。不要因为自检环节挂了卡住整个交付，也不要假装自检过了。

## 自检流程（5 步）

### Step 1 · 在后台 tab 加载 HTML

```bash
curl -s "http://localhost:3456/new?url=file://$HOME/Downloads/{file}.html"
# 拿到 targetId
```

### Step 2 · 截关键 5 张图

**重要**：先禁用 smooth 滚动，否则截图捕获到的是滚动中状态。

```bash
curl -s -X POST "http://localhost:3456/eval?target={ID}" -d 'document.documentElement.style.scrollBehavior = "auto"'
```

5 张图位置：
1. **首屏（y=0）**：Hero 完整呈现
2. **Quick Facts（y≈900）**：12 格速览板
3. **TL;DR + 章节衔接（y≈1500）**：黑块 + 后续章节
4. **核心组件（按主题挑）**：竞品对比表 / 时间线 / Path 卡片 — 选最复杂的那个
5. **末端（y≈doc.scrollHeight - 1000）**：决策建议黑块 + footer

每张图：
```bash
curl -s -X POST "http://localhost:3456/eval?target={ID}" -d 'window.scrollTo(0, {y}); window.scrollY'
sleep 0.4
curl -s "http://localhost:3456/screenshot?target={ID}&file=/tmp/check-{n}.png"
# 用 Read 工具读 PNG
```

### Step 3 · 视觉评估清单

对每张图回答：

- [ ] **首屏**：标题字号合理？italic em 强调词是否突出？右侧 meta 完整？
- [ ] **Quick Facts**：12 格是否对齐？数字是否清晰？最后一格红 verdict 是否醒目？暗色背景对比是否够？
- [ ] **TL;DR**：黑块是否真黑（不是灰）？红色 ribbon "TL;DR" 浮在角上？正文行高是否舒服？
- [ ] **核心组件**：表格是否信息密度高但不拥挤？时间线 dot 颜色是否对？path 卡片顶部 border 是否显眼？
- [ ] **末端**：决策黑块对比是否强？三选项卡片是否平衡？footer 来源链接是否完整？

通用问题：
- [ ] **外行可懂性**：抽查 2-3 个专业术语 / 复杂段落，是否都有白话注解或"就像……"的比方？没有则补上
- [ ] 中文换行有无尴尬位置（"该不"、"你的"等被打断）？
- [ ] 数字单位是否一致（M/K/百万 不要混用）？
- [ ] 链接颜色是否清晰可点？
- [ ] sticky TOC 是否高亮当前章节？

### Step 4 · 迭代修补

发现问题 → 用 Edit 工具修 HTML → 不需要重新 dispatch CDP，直接刷新：
```bash
curl -s "http://localhost:3456/navigate?target={ID}&url=file://$HOME/Downloads/{file}.html"
sleep 0.5
# 重新截图验证
```

**常见问题与修法**：
- 中文换行尴尬 → 加 `word-break: keep-all` 或显式 `<br>`
- Quick Facts 单行太挤 → 加大格子 `min-height` 或减少格子数
- 时间线日期与 dot 不对齐 → 检查 `.tl-row` grid template 的 column width
- 黑块对比不够 → 改 `--bg-dark` 更深 / 提高 `color: rgba(255,255,255,X)` 的 X 值
- 表格在小屏溢出 → `.table-wrap { overflow-x: auto }` 已有，确认表格 min-width 是否过大

### Step 5 · 关闭 CDP tab + 交付

```bash
curl -s "http://localhost:3456/close?target={ID}"
```

**自检停止条件**：
- 所有 5 张图都满足清单
- 或迭代了 ≥ 3 轮（防止无限优化陷入完美主义）
- 或迭代后视觉变化已经很小（marginal returns）

## 移动端验证（当前不做）

web-access 的 CDP proxy 没有视口/设备模拟接口（`window.resizeTo` 在无界面浏览器里无效），所以**不在自检里截手机图**——避免"以为验过手机端、实际截的还是宽屏"的假动作。移动端布局靠 `html-template.md` 的响应式断点（1100px / 720px）保证，需要人工确认时再用真机或浏览器手动开。

## 与本次手动报告的对比基准

每次自检的最终质量应不低于 `references/sample-output.html`（skill 自带的稳定样板，含 light + dark 双模式）的水平。
具体的标杆：
- Hero 标题杂志感
- Quick Facts 12 格清晰
- TL;DR 黑块对比强
- 至少一个 timeline 或对比表
- 决策建议三选项 + 详细行动卡
- footer 来源完整
