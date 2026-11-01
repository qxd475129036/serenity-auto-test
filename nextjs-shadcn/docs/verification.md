# 验证要求

## 验证命令

| 命令 | 作用 |
|---|---|
| `npm run typecheck` | TypeScript 类型检查（`tsc --noEmit`） |
| `npm run lint` | ESLint（next core-web-vitals + typescript） |
| `npm run build` | 生产构建（含全部静态页面编译）；Codex 沙箱内改用 `npx next build --webpack`（见"沙箱执行流程"） |
| `npm run dev` | 本地开发（浏览器人工验证）；必须监听 3000 端口（env 硬编码，见"沙箱执行流程"） |

当前未引入测试框架（无 vitest/jest）。引入前，**验证三件套 = typecheck + lint + build**；引入后在此补充测试命令并升级三件套为四件套。

## 沙箱执行流程（Codex 桌面环境）

在 Codex 沙箱内执行"验证三件套 + UI 截图"时，按此顺序执行，提权次数固定为 3 次（构建、起服务、截图），避免反复试错:

| 步骤 | 命令 | 提权 | 说明 |
|---|---|---|---|
| 1 | `npm run typecheck` | 否 | 无网络依赖 |
| 2 | `npm run lint` | 否 | 前两步任一失败先修，不要跑构建 |
| 3 | `npx next build --webpack` | 是 | ① next/font/google 构建时需联网拉 Geist 字体；② Next 16 默认 Turbopack 构建的 worker 端口绑定报 "binding to a port — Operation not permitted"，`--webpack` 绕开 |
| 4 | dev server（端口 3000） | 视情况 | 优先复用既有 dev server（见下） |
| 5 | Playwright 截图脚本 | 是 | 无头 Chrome 子进程管控在沙箱内受限（见下） |

### 验证服务器: 端口必须 3000

- `.env.local` 的 `NEXT_PUBLIC_APP_URL` 与 `THIRD_PARTY_API_URL` 硬编码 `http://localhost:3000`。auth 流程（登录/登出/session）只有服务跑在 3000 才通；换端口（如 `PORT=3123 npm run start`）登录会"静默失败"——客户端请求打到无人监听的 3000。
- 起服务前先 `lsof -ti:3000`:
  - 已占用且进程 cwd 是本仓库（`lsof -p <pid> | grep cwd` 确认）→ 复用既有 dev server，不要 kill（用户浏览器可能连着）。
  - 空闲 → 提权启动 `npm run dev`（默认 3000）；验证完成后，自己起的才停。
- 沙箱内 `curl localhost` 不可靠（回环受限，返回 000）；判断端口状态用 `lsof`，需要 HTTP 探测时提权。
- 用生产构建（`next start`）验证时同理: 必须监听 3000（NEXT_PUBLIC_* 在构建时注入）。

### Playwright 截图: 用 workspace 自带运行时

- 项目未安装 playwright 依赖；不要用 `npx playwright`（沙箱内会挂起在联网下载）。
- 用 Codex workspace 自带运行时（路径漂移时以 `load_workspace_dependencies` 返回为准）:
  ```bash
  NODE=/Users/quxd/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
  NM=/Users/quxd/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules
  NODE_PATH=$NM $NODE shot.js
  ```
  脚本内 `require("playwright")`，`chromium.launch({ channel: "chrome" })` 走系统 Google Chrome。
- 脚本必须以提权方式运行（沙箱内 Chrome 子进程 SIGABRT / kill EPERM）。
- 脚本里用 `page.on("console")` / `page.on("pageerror")` 收集 console 错误，作为"无 console 错误"的证据。
- 截图输出写到 `/private/tmp/...`；visualizations 目录注意用实际磁盘路径（`2026-11-01` 斜杠日期），`2026-11-01` 连字符路径写入会报 no such file。

### 已知行为（非 bug，验收时别误判）

- 登录成功后 `router.refresh()` 不保证立即渲染已登录卡片（better-auth 客户端 session 状态更新时机）；硬刷新后展示。SPEC 验收口径是"页面刷新后展示已登录态"。
- 错误密码场景 console 会有一条 `401 (UNAUTHORIZED)` resource 报错，属预期。

### 沙箱小坑速查

| 现象 | 处理 |
|---|---|
| `ps -p <pid>` 报 operation not permitted | 用 `ps aux \| grep`（已批 prefix: `ps aux`） |
| 构建报 Google Fonts 拉取失败 | 构建命令提权（联网） |
| Turbopack 构建报端口绑定 Operation not permitted | `npx next build --webpack` |
| `npx <pkg>` 挂起 | 项目缺依赖时 npx 会联网下载；改用 workspace 运行时 + NODE_PATH |
| 写 visualizations 的 `2026-11-01` 路径失败 | 用 `/private/tmp` 或斜杠日期路径 |

## 提交前检查清单

- [ ] `npm run typecheck && npm run lint && npm run build` 全部通过（沙箱内 build 用 `npx next build --webpack` 提权执行，见"沙箱执行流程"）
- [ ] 改动未超出任务范围（对照 SPEC 目标/非目标）
- [ ] 页面级改动已在浏览器人工验证（默认亮色 + 本次涉及的移动端视口）
- [ ] 规则若有变化，同步更新对应 SPEC / PAGE / docs 文档

当前项目没有主题切换入口，暗色验收暂停；启用主题能力后再恢复暗色检查。

## 证据格式

任务完成汇报时必须给出:

1. 验证三件套的输出（可只贴关键行: 通过/失败 + 错误摘要）。
2. UI 变更: 截图（默认亮色；涉及响应式时加移动端；主题能力启用后补充暗色）。
3. 改动文件清单（一行一个路径，标注新增/修改）。
