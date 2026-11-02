# 首页（工作台）

- 路由: `/`
- 文件: `app/(app)/page.tsx`
- 类型: Server Component（顶部导航 `components/app/app-header.tsx` 为 Client Component）
- 功能域: [首页 SPEC](../../features/home/SPEC.md)、[业务后台 SPEC](../../features/back-office/SPEC.md)

## 页面元素

以下字段只记录当前页面实例。组件 API 和通用默认值以 `components/ui/*.tsx` 为准。

### 顶部导航

- 展示: 页面顶部固定的全局导航条（`sticky top-0 z-40`，下边框 + 背景模糊）
- 定义: 提供业务模块切换与登出入口
- 默认: 由 `app/(app)/layout.tsx` 渲染 `AppHeader`，作用于路由组内全部页面
- 交互: 无（容器本身不响应点击）

### 品牌标识 rabbit

- 展示: 顶部导航左侧，`RabbitIcon` + `rabbit` 文字
- 定义: 返回工作台首页
- 默认: `Link href="/"`，`font-heading text-lg font-semibold tracking-tight`
- 交互:
  - 点击后回到 `/`

### 模块下拉菜单

- 展示: 桌面（`lg` 起）导航中的 6 个下拉项：権限（ユーザー）管理、マスタ管理、請求業務管理、代引業務管理、弁済業務管理、明細ダウンロード
- 定义: 展开进入各子模块
- 默认: `NavigationMenuTrigger`；子项为 `NavigationMenuLink` 包裹 `Link`，含图标、名称、一行说明；下拉面板 `viewport={false}`，锚定当前触发器（左对齐，下方 `mt-1.5`）
- 交互:
  - 点击或键盘聚焦触发器展开下拉；选择子项跳转对应路由
  - 当前分组含 2–4 个子项，数据来自 `components/app/nav-config.ts`

### 移动端菜单

- 展示: `lg` 以下显示菜单图标按钮（`Button variant="ghost" size="icon"`）
- 定义: 在窄屏打开业务菜单抽屉
- 默认: `aria-label="メニューを開く"`；`Sheet side="left"`，按 `NAV_GROUPS` 分组列出全部子模块链接
- 交互:
  - 点击按钮打开抽屉
  - 点击任一链接后关闭抽屉并跳转
  - Esc 或点击遮罩关闭

### 登出按钮

- 展示: 顶部导航右侧，`ログアウト` 按钮（带 LogOut 图标）
- 定义: 退出当前登录态
- 默认: `variant="outline"`、`size="sm"`、`aria-label="ログアウト"`（复用 `components/login/sign-out-button.tsx`）
- 交互:
  - 点击调用 `authClient.signOut()`，成功后 `router.replace("/login")`

### 页面标题

- 展示: `ダッシュボード`
- 定义: 标识当前页面为登录后的工作台
- 默认: `h1`，`font-heading text-2xl font-semibold tracking-tight`；下方说明文字「業務メニューから各機能へ移動できます。」
- 交互: 无

### 模块分组

- 展示: 6 个分组：権限（ユーザー）管理、マスタ管理、請求業務管理、代引業務管理、弁済業務管理、明細ダウンロード
- 定义: 按业务域聚合功能入口
- 默认: 分组标题 + `Separator` + 卡片网格（`grid gap-4 sm:grid-cols-2 lg:grid-cols-3`）
- 交互: 无

### 功能卡片

- 展示: 15 个模块的入口卡片（图标、标题、说明、右箭头）
- 定义: 进入对应模块页面
- 默认: `Link` 包裹 `Card`，整卡可点击；悬停时边框加深、箭头右移
- 交互:
  - 点击后跳转到 `nav-config.ts` 中定义的 `href`
  - 当前 15 个模块均跳转到统一「準備中」占位页

### 组件一覧（開発用）

- 展示: 页脚文本链接「コンポーネント一覧（開発用）」
- 定义: 进入 shadcn 组件演示页
- 默认: `Link href="/demo"`，`text-sm text-muted-foreground`，悬停下划线
- 交互:
  - 点击后进入 `/demo`

## 响应式

- `lg` 起显示桌面下拉导航；`lg` 以下隐藏导航，改用左侧抽屉菜单。
- 卡片网格：手机单列、`sm` 两列、`lg` 三列。
- 顶部导航高度固定 `h-14`，内容区左右内边距 `px-4 / sm:px-6 / lg:px-8`。

## 本页例外与注意

- 页面为纯静态 Server Component，无数据请求、无 loading/empty/error 状态。
- 全部 15 个模块均已有占位页；代引・弁済・明細 各含 2 个通用占位页。
- `/demo`、`/login` 不在 `(app)` 路由组内，不显示顶部导航。
- 首页受根级 `proxy.ts` 登录守卫保护：未登录访问 `/` 会被重定向到 `/login`。
