# 共享库接入（Research Exchange）

让本 skill 连上研报共享库 registry：**调研前查库复用**（别人调过的别重复烧钱）、**调研后可选上传共享**。
这是可选层——没配就静默跳过，skill 照常本地工作。

## 配置

文件：`~/.config/ray-deep-research/exchange.json`（可选）

```json
{
  "api": "https://ray-research-registry-api.typefree.workers.dev",
  "invite_code": "inv_xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

- `api`：共享库 API 地址，默认即上面这个（库主的 registry）。一般不用改。
- `invite_code`：你的专属邀请码（找库主要）。**无邀请码 → 共享库功能全部跳过，skill 只用本地。**

**首次询问**：当要用共享库、但 exchange.json 缺 `invite_code` 时，问一次：
> "要连研报共享库吗？有邀请码就粘贴（没有就跳过，只用本地）。"

- 给码 → 写入 exchange.json（`api` 用默认值）。
- 跳过 → 写 `{"invite_code": null}` 记住选择，之后不再问（除非用户主动说要连）。

## 鉴权

每个请求带 `Authorization: Bearer {invite_code}`。
`401` = 码无效或被撤销 → 告知用户"邀请码失效，找库主重发"，跳过共享库、继续本地流程。

## Stage 0.5 · 查共享库（命中就别重跑）

在本地库复用检查之后执行（朋友无 `library_path`、跳过了本地检查的，直接走这步）：

1. `GET {api}/query?topic={主题名}`（URL 编码），带 Bearer。**主题名 = Stage 0 解析出的产品/公司名**（用户叫它什么就用什么），**绝不要传用户整句话**——"SPCX 值得打新吗"归一化后永远匹配不上别名 `spcx`。**只查一次**：查多次会虚增查询分母、扭曲库主的命中率统计；未命中就当 miss 继续调研（miss 会落库，帮库主发现该补的别名）。
2. 解析：`{hit, topic_norm, reports:[{id,title,date,contributor,degraded,url}]}`。
3. **命中（hit=true）** → 一句话告知 + 二选一，**等用户回应**：
   > "共享库里已有 **{contributor}** 的《{title}》（{date}）。要 (a) 直接看现成 / (b) 我重新调研一份？"
   - 选 (a) → `open {reports[0].url}` + `POST {api}/event` body `{"kind":"view","report_id":{id},"topic":"{原始词}"}`（带 Bearer，返回 204）→ 结束本次。
   - 选 (b) → `POST {api}/event` body `{"kind":"rerun","report_id":{id},"topic":"{原始词}"}` → 继续 Stage 1 正常调研。
4. **未命中 / 用户选重跑** → 继续正常调研。
5. **多个命中** → 列前几条（title + date + contributor）让用户挑看哪个，或重跑。

## Stage 5 · 跑完上报 + 上传共享库（可选，交付后）

报告生成、交付给用户之后，若 exchange 已配置：

0. **先静默上报"跑完"**（不问用户）：`POST {api}/event`，带 Bearer，body `{"kind":"run","topic":"{主题名}"}`（**不带 report_id**）→ 204。这是库主统计"上传占比"的分母；失败就算了，不重试不打扰。
1. 问一次：
   > "这份报告要上传到共享库吗？（公开，装了 skill 的人能搜到；私密调研建议不传）"
2. 用户同意 →
   a. **内联**：把报告 HTML 里 `<link ... sidebar.css>`、`<script ... sidebar.js></script>` 替换成内联的 `<style>…</style>` / `<script>…</script>`（R2 直出没有 `../assets`，不内联会 404）。
   b. `content_hash` = 内联后 HTML 的 UTF-8 字节的 **sha256，小写 hex**。
   c. `POST {api}/upload`，带 Bearer + `Content-Type: application/json`，body：
   ```json
   {
     "topic_slug": "{slug}",
     "aliases": ["中文名", "英文名", "ticker"],
     "title": "{报告标题}",
     "date": "{YYYY-MM-DD}",
     "degraded": false,
     "content_hash": "{sha256}",
     "html": "{内联后的完整 HTML}"
   }
   ```
   - `aliases`：来自 Stage 0 已解析的主题别名（中文名 / 英文名 / ticker 的常见叫法），至少 1 个。
   - `degraded`：本次是否降级模式（见 environment.md），true / false。
   - **`contributor` 不用传** —— 服务端按邀请码绑定的昵称记（客户端传了也会被忽略）。
3. 响应 `201 {id,url}`（新增）或 `200 {deduped:true,id}`（同内容已存在）→ 告知"已上传：{url}"。
4. 用户拒绝 / 私密内容 → 不传。

## 降级（共享库故障绝不拖累主流程）

- 未配 exchange.json 或无 `invite_code` → 全部共享库步骤静默跳过。
- registry 超时 / 网络错 / 5xx → 一句"共享库暂时连不上，跳过"，继续本地调研。
- `401` → 提示码失效，跳过。
- **`403` → 静默放弃，不提示、不重试、不当 bug 上报。** 已知现象：部分地区直连 `workers.dev` 时，边缘网络会拦截 POST 请求（同码的 GET /query 往往正常）——不是接口坏了，也不是码的问题。`/event` 是 fire-and-forget 埋点，丢了不影响任何功能；`/upload` 遇 403 则告知用户"当前网络到共享库的上传通道不通，报告已在本地正常交付"。

## 接口契约（与 registry §4 对齐，字段名不要擅自改）

| 接口 | 方法 | 请求 | 响应 |
|------|------|------|------|
| 查询 | `GET /query?topic=` | Bearer | `{hit, topic_norm, reports[]}` |
| 上传 | `POST /upload` | Bearer + JSON | `201{id,url}` / `200{deduped,id}` / `400` |
| 埋点 | `POST /event` | Bearer + `{kind,report_id?,topic}` | `204`（kind：`view`/`rerun` 须带 report_id；`run` 不带） |
