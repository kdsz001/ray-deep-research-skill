# HTML 视觉模板 · 严肃商业杂志风

**核心设计哲学**：不是 marketing landing page，是一份给决策者看的报告。**严肃 + 高级 + 信息密度高**。

## 使用方式（最重要：先复制骨架，再填内容）

**每次出报告都从 `references/template.html` 复制起步，不要从零写 HTML**——每次重写 2000 行 CSS/JS 就是每次重新引入 bug 的机会（`<main>` 命名坑就是这么踩的）。

1. `cp references/template.html ~/.cache/ray-deep-research/{slug}/report.html`（工作目录，见 checkpoint.md）
2. 全文搜索 `{{ }}` 占位符逐个替换（title / topbar / hero / Quick Facts / footer）
3. 按 preset 章节结构在 `<article>` 内增删 `<section>`——**一章一章分次写入文件，每写完一章更新 STATE.md**（防爆窗，见 checkpoint.md），绝不一次输出整份；各组件标准写法直接从文件底部 `<template id="component-examples">` 块里复制出来填数据
4. 交付前删除底部 `<template id="component-examples">` 整块
5. **骨架部分不要动**：`<head>` 内全部 CSS / 防 FOUC 脚本 / sidebar 注入三行 / 主题切换按钮 / 底部 JS

本文件其余部分是骨架的设计规范说明——填内容时拿不准"该用哪个组件 / 什么颜色"再查，不需要照着重写样式。

## 设计 Token

```css
:root {
  /* 暖色奶白纸张感 */
  --bg: #f6f3ec;
  --bg-paper: #fbf9f4;
  --bg-card: #ffffff;
  --bg-dark: #14110d;
  --bg-dark2: #1f1b16;

  /* 深墨色文字 */
  --ink: #14110d;
  --ink-2: #2c2620;
  --muted: #6e6358;
  --light: #a39787;

  /* 分隔线 */
  --rule: #14110d;
  --rule-light: #d8d1c2;

  /* 强调色（克制使用） */
  --accent-warn: #a73121;   /* 红：警告/差评/风险 */
  --accent-data: #1c4d6b;   /* 蓝：数据/链接 */
  --accent-pos: #2c5e3f;    /* 绿：优势/积极 */
  --accent-yellow: #c89a2c; /* 金：路径/装饰 */

  /* 字体 */
  --serif: "Source Serif 4", "Source Serif Pro", "Charter", "Iowan Old Style", Georgia, serif;
  --sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --mono: "JetBrains Mono", "SF Mono", "Menlo", "Consolas", monospace;

  --max-w: 820px;
}
```

**字体加载**：用 Google Fonts 加载 Source Serif 4 + Inter + JetBrains Mono。中文走系统字体（PingFang SC / Microsoft YaHei）。

## 排版规则

- 大标题（h1）→ 衬线 600 78px / line-height 1.0 / 字距 -0.03em
- 章节标题（h2）→ 衬线 600 44px
- 子标题（h3）→ 衬线 600 24px
- 标签（h4）→ 无衬线 600 14px uppercase 字距 0.08em
- 正文 → 无衬线 16px / line-height 1.7
- 数字 → 衬线 36px / line-height 1
- 等宽 → mono 11px uppercase（用于眉标、来源、章节编号）

## ⚠️ 主容器命名硬约束（最高优先级）

**报告的主内容容器（包含 nav.toc + article 两列 grid 的那个外层 div）必须用 `<main>` 元素**，不能用 `<div class="layout">` / `<div class="container">` / 其它任意命名。

```html
<!-- ✅ 正确：用 main 元素 -->
<main>
  <nav class="toc">...</nav>
  <article>
    <section id="...">...</section>
    ...
  </article>
</main>

<!-- ❌ 错误：不要用 div.layout 或 div.container -->
<div class="layout">
  <nav class="toc">...</nav>
  <article>...</article>
</div>
```

**为什么硬约束**：仓库 `assets/sidebar.css` 在 sidebar 接管时会用 `body.rs-active main` 选择器把 grid 改成单列。容器命名不一致 → sidebar 注入后会出现"内容挤到左边窄列、右边大片空白"的视觉灾难（2026-05-16 alphabet/hyperliquid/linde 等报告踩过这个坑）。

`assets/sidebar.css` 同时兜底了 `.layout` 和 `div.container`，但**正确做法是从源头用 `<main>`**，不要依赖兜底选择器。

CSS 中也要对应用 `main { ... }`，不要用 `.layout { ... }`：

```css
/* ✅ 正确 */
main {
  max-width: 1240px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 60px;
  padding: 60px 32px;
}

/* ❌ 错误 — sidebar.css 的 reset 规则可能匹配不上 */
.layout { ... }
```

---

## 必有结构（每份报告都要有）

### 1. Top metadata bar
顶部一条窄横条，等宽小字：报告名 / 调研日期 / 版本号。

### 2. Hero（首屏）
- 左侧：eyebrow（accent-warn 色 + 短横线）→ h1（衬线 + 一个 italic em 强调词，accent-warn 色）→ subtitle（衬线 italic 22px muted）
- 右侧：hero-meta（mono 小字 dl 列表，含调研对象/深度/覆盖平台/字数/读者）

### 3. Quick Facts 速览板（hero 后立刻出现）
**这是与普通报告最大的差异化**——给读者"10 秒看完"的能力。
- 黑色背景大块
- 顶部 eyebrow（金色）+ italic 标题（"X at a Glance"）
- 12 格 grid（手机 2 列 / 平板 3 列 / 桌面 6 列）
- 每格：mono label（深色背景上的灰）+ 衬线大数字（带 unit）+ sub 注释
- 最后一格固定为红色 verdict cell（如"不建议正面复刻"）

### 4. Sticky TOC（左侧）
- 桌面 200px 宽，sticky top:40px
- mono small 字体，编号 01-N
- 当前章节 hover/active 高亮（红色 + bold）
- IntersectionObserver 跟随滚动自动高亮

### 5. 章节（按 preset 决定数量和顺序）
每章必有：
- 章节编号 + 标题（mono 红字 + 横线）
- h2 衬线大字
- 正文 + 各种 component（见下）

### 6. Footer
- 黑色背景
- 数据来源列表（mono small，2 列）
- footer-meta：报告生成信息 + 免责声明

## 关键 Components

### TL;DR 黑块
```html
<div class="tldr">
  <!-- 浮起 TL;DR 红色 ribbon -->
  <h3>...</h3>
  <ol>...</ol>
</div>
```
特征：black bg + cream text + 红色 ribbon "TL;DR" 浮在左上。

### Stats 卡片网格
3 列 grid，每格：mono label + 衬线 36px 大数 + 注释。颜色：默认 ink、`.warn` 红、`.data` 蓝、`.pos` 绿。

### Metric List（一行一个数据）
顶底各一条粗黑横线，中间薄横线。左侧 label（含 source 灰字），右侧大数字。视觉效果像金融报表。

### Two-col 卡片（好评 vs 差评）
左右两张白卡片。标题前缀 `.pos` 用绿圆 ✓，`.warn` 用红圆 !。列表小字 14px。

### 引用 Quote
左侧 3px 红竖线 + 衬线 italic 18px + 下方 attribution（"— "前缀）。

### Score 条
- 容器：1px 黑边白底
- 每行：name（衬线 600）+ bar（8px 高，浅色底 + 填充）+ 右侧数字
- 填充色按性质：`.pos` 绿 / `.warn` 红 / 默认深蓝

### 横向对比表格
- thead：mono 小字 uppercase，2px 黑底线
- tbody：14px，行间薄横线，最后一行 1px 黑横线
- 第一列：`.product-name` 衬线粗体 + 可选 `.tag` 小标签
- 高亮行（如调研对象）：`background: rgba(167, 49, 33, 0.04)`

### Callout 块
左侧 3px 竖线 + paper 浅底。`.warn` 红 / `.data` 蓝 / 默认黑。
顶部 mono uppercase label + `.callout-quote` 衬线 italic 17px。

### 数据可信度标注（Stage 2.5 验证结果必须带进 HTML）
高 stake 数字在 label 的 `.src` 灰字里带验证状态；未验证项汇总进一个 `.callout.warn` 块（骨架组件示例库里已有"⚠ 数据真伪提醒"示例）。

```html
<!-- 已交叉验证：在来源后加 ✓ + 日期 -->
<div class="label">融资金额<span class="src">Crunchbase ✓ 已交叉验证 2026-05-18</span></div>

<!-- 未交叉验证：来源后加 ⚠ 标记（保留数字，不删除） -->
<div class="label">月访问量<span class="src">SimilarWeb · ⚠ 未交叉验证</span></div>
```

footer 加一行汇总：`本报告 N 个高 stake 数据点已通过 Stage 2.5 独立验证（X 个交叉验证 / Y 个未验证）`。完整规则与处理表见 `data-verification.md` 的"输出格式约束"。

### 时间线（Timeline）
3 列 grid：日期（mono 右对齐）+ dot（中间垂直线 + 圆点）+ 内容（衬线粗 title + 14px 描述）。
dot 颜色：默认黑边 / `.warn` 红 / `.data` 蓝——颜色递进可叙事。

### Path 卡片（决策路径详细方案）
2 列 grid 白卡片。`.a` 顶部 4px 绿 border / `.c` 红 border。
每张：mono path-num + 衬线 h4 + 简短 p + 项目列表。

### Verdict 黑块（决策章节用）
黑色大块。顶部金字 verdict-title → 衬线大 h3 → 段落 → 3 列子卡片（verdict-options），每张含 mono num + 衬线 h4 + 14px 简介。

### Divider Quote
章节之间的金句。center align + 衬线 italic 22px muted + 上下两条短横线装饰。

## 响应式断点

```css
@media (max-width: 1100px) {
  /* TOC 折叠到顶部，hero 单列，verdict 单列，Quick Facts 3 列 */
}
@media (max-width: 720px) {
  /* hero 字号缩小，Quick Facts 2 列，所有 grid 单列 */
}
```

## 打印样式（必须有）

```css
@media print {
  /* 顶栏/TOC/footer 隐藏 */
  /* 黑色块改白底黑字，hero 后分页 */
  /* 链接去下划线和颜色 */
  /* section 避免跨页打断 */
}
```

## 夜间模式（必有）

### 设计哲学
**不是简单的"全部反色"**——而是把"反色块"反相：
- Light 模式：主体浅奶白，反色块（TL;DR / Quick Facts / verdict / footer）深黑
- Dark 模式：主体深咖墨，反色块变浅（米白色），保持视觉对比层次

### 实现要点

1. **独立 inverse tokens**（在 `:root` 里定义，`[data-theme="dark"]` 反相）：
```css
:root {
  --bg-inverse: #14110d;            /* light: 深 */
  --ink-on-inverse: #f6f3ec;        /* light: 浅文字 */
  --text-on-inverse: rgba(246, 243, 236, 0.85);
  --muted-on-inverse: rgba(246, 243, 236, 0.7);
  --faint-on-inverse: rgba(246, 243, 236, 0.55);
  --light-on-inverse: rgba(246, 243, 236, 0.5);
  --rule-on-inverse: rgba(246, 243, 236, 0.18);
  --accent-yellow-on-inverse: #c89a2c;
}
[data-theme="dark"] {
  --bg-inverse: #ede5d3;            /* dark: 浅 */
  --ink-on-inverse: #14110d;        /* dark: 深文字 */
  --text-on-inverse: rgba(20, 17, 13, 0.85);
  /* ... 余略 */
}
```

2. **反色块（.tldr / .verdict / .quickfacts-wrap / footer / .qf-cell / .verdict-option）必须用 inverse tokens**，不要用 `var(--bg-dark)` + `var(--bg)`。

3. **强调色（accent-warn / data / pos）在 dark mode 下要更亮**（`#a73121` → `#e87a5f` 等）以保持对比度。

4. **防 FOUC 启动 JS**（必须在 `<head>` 内同步执行，body 渲染前就设好主题）：
```html
<script>
(function() {
  try {
    var saved = localStorage.getItem('ray-theme');
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var theme = saved || (prefersDark ? 'dark' : 'light');
    if (theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  } catch (e) {}
})();
</script>
```

5. **右上角浮动切换按钮**（fixed top-right，36px 圆形，太阳/月亮 SVG 图标，dark 模式下切显图标）。

6. **平滑过渡**：在 body / 反色块 / 卡片元素加 `transition: background-color 0.2s, color 0.2s, border-color 0.2s`。

7. **打印样式覆盖**：dark 模式下打印应改回浅底（`@media print { body { background: white; } /* ... */ }`）+ 隐藏切换按钮（`#theme-toggle { display: none; }`）。

### 完整实现见 `references/sample-output.html`

如果要改设计，**先开 sample-output.html 在 light + dark 两模式都跑一遍 CDP 截图**，确认双模式都正常。

## JS 行为（minimal）

只加几段必要的 JS：（1）防 FOUC 主题初始化（head 内）（2）切换按钮点击 + 系统偏好变化跟随（3）IntersectionObserver 让 TOC 自动跟随当前章节高亮。**不引入任何外部 JS 库**（保持单文件、可离线、可永久存档）。

```js
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      document.querySelectorAll('nav.toc a').forEach(link => {
        link.style.color = '';
        link.style.fontWeight = '';
      });
      const activeLink = document.querySelector(`nav.toc a[href="#${id}"]`);
      if (activeLink) {
        activeLink.style.color = 'var(--accent-warn)';
        activeLink.style.fontWeight = '600';
      }
    }
  });
}, { rootMargin: '-30% 0px -60% 0px' });
document.querySelectorAll('section[id]').forEach(s => observer.observe(s));
```

## 反 AI Slop 清单

避免：
- ❌ 每个章节都用 emoji 标题（除非真的需要）
- ❌ 渐变色背景 / 玻璃拟物 / 霓虹边框
- ❌ 圆角太大 / 阴影太柔
- ❌ "Get started for free"等 CTA 按钮
- ❌ 装饰性插画 / 图标网格
- ❌ Tailwind 默认配色（slate-50 / blue-500 等）

要的：
- ✅ 衬线大标题 + italic 强调词的杂志感
- ✅ 严肃黑红配色 + 极少量金/绿/蓝点缀
- ✅ 等宽字体作"声音色调"做眉标
- ✅ 数字大、留白多、分隔线粗
- ✅ 高对比表格、分明的章节切割

## 参考样板

- `references/template.html` — **生成新报告的起点骨架**（CSS/JS 与 sample 同源，内容区为占位符 + 组件示例库）
- `references/sample-output.html` — 完整成品参照（含 light + dark 双模式），看"填好后长什么样"时用；如要改设计，先在它上面跑 light + dark 双模式 CDP 截图确认，再同步改 template.html
