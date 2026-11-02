# 登录

- 路由: `/login`
- 文件: `app/login/page.tsx`
- 类型: Client Component（`"use client"`）
- 功能域: [登录 SPEC](../../features/login/SPEC.md)
- UI 语言: 日文（`lang="ja"` 挂在页面根节点；root layout 不变）

## 布局

- 根: `flex min-h-dvh`，左右分栏（`bg-background text-foreground`）。
- 左栏品牌区（仅 lg+ 显示）: `bg-primary text-primary-foreground`，宽 `w-[42%] max-w-2xl`，三段式（顶部 wordmark / 中部标语 / 底部版权）。
- 右栏表单区: `flex-1`，顶部工具行（移动端 wordmark），表单卡片垂直水平居中（`max-w-sm`）。

## 页面元素

以下字段只记录当前页面实例。组件 API 和通用默认值以 `components/ui/*.tsx` 为准。

### 品牌面板（左侧，lg+）

- 展示: 深色面板：`BrandMark`（Rabbit 图标 chip + "rabbit" wordmark）、"社内申請システム" 副标、标语「申請から承認まで、ひとつの窓口。」、说明文、版权行
- 定义: 传达系统身份与用途
- 默认: `hidden lg:flex`，`bg-primary text-primary-foreground`
- 交互: 无（纯展示）

### 页面标题

- 展示: `sr-only` 的 `<h1>`「rabbit 社内申請システム - ログイン」
- 定义: 页面唯一 h1，全视口可见（屏幕阅读器/SEO）
- 交互: 无

### 移动端 wordmark

- 展示: Rabbit 图标 + "rabbit" 文本（表单区顶部工具行，仅 <lg 显示）
- 定义: 品牌面板隐藏时的品牌标识
- 默认: `lg:hidden`
- 交互: 无

### 登录卡片（未登录态）

- 展示: 登录表单容器（Card）
- 定义: 承载用户名/密码登录表单
- 默认: `w-full max-w-sm`
- 交互: 无

### 卡片标题与说明

- 展示: `ログイン` 和 `会社アカウントでサインインしてください。`
- 定义: 说明页面用途
- 默认: 使用 CardHeader、CardTitle 和 CardDescription
- 交互: 无

### 用户名输入

- 展示: ユーザー名 Label、User 图标和输入框
- 定义: 输入登录用户名
- 默认: `type="text"`，`autoComplete="username"`，placeholder `ユーザー名`，初始值 `""`
- 交互:
  - 输入时更新 `username` 本地状态
  - 提交中或 session 加载中时禁用

### 密码输入

- 展示: パスワード Label、Lock 图标和密码框
- 定义: 输入登录密码
- 默认: `type="password"`，`autoComplete="current-password"`，placeholder `パスワード`，初始值 `""`
- 交互:
  - 输入时更新 `password` 本地状态
  - 提交中或 session 加载中时禁用

### 密码显隐切换

- 展示: 密码框内右侧的 Eye/EyeOff 图标按钮（`InputGroupAddon align="inline-end"` + `InputGroupButton`）
- 定义: 切换密码可见性（`showPassword` 本地状态）
- 默认: 初始 `false`（隐藏）；`aria-label` 随状态切换，`aria-pressed` 反映状态
- 交互:
  - 点击切换输入框 `type` 在 `password`/`text` 之间
  - 提交中或 session 加载中时禁用

### Sign in（ログイン）

- 展示: 占满卡片宽度的主按钮（`size="lg"`）
- 定义: 提交登录表单
- 默认: 主按钮，`type="submit"`
- 交互:
  - 用户名或密码为空时阻止默认提交并显示 `toast.error`（「ユーザー名とパスワードを入力してください。」，不发请求）
  - 用户名和密码均非空时调用 `authClient.signIn.credentials({ username: username.trim(), password })`
  - 提交中按钮禁用并显示 Spinner + `ログイン中…`
  - 成功: `toast.success`（「ログインしました。」）并 `router.replace(next)`（无 `next` 时回 `/`）
  - 失败: `toast.error`（`error.message`；"Invalid username or password" 本地化为「ユーザー名またはパスワードが正しくありません。」，其余原文展示）

### Mock 提示

- 展示: `テスト用（モーク API）：ユーザー名 admin／パスワード password`（卡片下方）
- 定义: 告知当前对接 mock 第三方 API 及测试凭据
- 默认: `text-xs text-muted-foreground`
- 交互: 无

## 响应式

- lg+（≥1024px）: 左右分栏，品牌面板可见，表单区居中。
- <lg: 品牌面板隐藏，顶部工具行显示紧凑 wordmark，表单区占满宽度，容器保留 `px-6` 边距。
- 卡片使用 `w-full max-w-sm`；页面高度 `min-h-dvh`。

## 本页例外与注意

- 无品牌色：品牌视觉走中性 token（`bg-primary` 深色面板 + `text-primary-foreground`），不引入任意色值；品牌色待定（见 docs/design-system.md）。
- 当前没有主题切换入口，本页不提供主题切换。
- 登录态由 `authClient.useSession()` 判定；session 加载中（`isPending`）时表单禁用。
- 路由守卫由根级 `proxy.ts` 实现：未登录访问受保护页面会跳转到 `/login?next=<原路径+query>`；本页从 `next` 读取回跳目标并做站内路径校验，非法值回退 `/`。
- 已登录用户访问本页会立即 `router.replace(next)`（默认 `/`），不展示登录表单。
- 日文由系统字体栈回退渲染（Geist 不含日文 web font；设计系统禁止引入其他 web font）。
