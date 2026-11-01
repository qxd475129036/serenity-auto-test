# 登录

- 路由: `/login`
- 文件: `app/login/page.tsx`
- 类型: Client Component（`"use client"`）
- 功能域: [登录 SPEC](../../features/login/SPEC.md)
- UI 语言: 日文（`lang="ja"` 挂在页面根节点；root layout 不变）

## 布局

- 根: `flex min-h-dvh`，左右分栏（`bg-background text-foreground`）。
- 左栏品牌区（仅 lg+ 显示）: `bg-primary text-primary-foreground`，宽 `w-[42%] max-w-2xl`，三段式（顶部 wordmark / 中部标语 / 底部版权）。
- 右栏表单区: `flex-1`，顶部工具行（返回按钮 + 移动端 wordmark），表单卡片垂直水平居中（`max-w-sm`）。

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

### 返回按钮

- 展示: ArrowLeft 图标按钮（表单区顶部工具行左侧）
- 定义: 返回项目首页
- 默认: `variant="ghost"`，`size="icon-sm"`，`aria-label="トップページへ戻る"`
- 交互:
  - 点击后进入 `/`

### 移动端 wordmark

- 展示: Rabbit 图标 + "rabbit" 文本（返回按钮右侧，仅 <lg 显示）
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

### Remember me（ログイン状態を保持）

- 展示: Checkbox 和关联 Label「ログイン状態を保持」
- 定义: 记录是否记住登录状态（作为 `rememberMe` 传给 Better Auth）
- 默认: 初始值 `false`
- 交互:
  - 切换时更新 `remember` 本地状态
  - 提交中或 session 加载中时禁用

### Forgot password（パスワードをお忘れですか？）

- 展示: Link 样式按钮
- 定义: 预留找回密码入口
- 默认: `type="button"`
- 交互:
  - 点击后无业务回调
  - 当前不跳转

### Sign in（ログイン）

- 展示: 占满卡片宽度的主按钮（`size="lg"`）
- 定义: 提交登录表单
- 默认: 主按钮，`type="submit"`
- 交互:
  - 用户名或密码为空时阻止默认提交并显示 `toast.error`（「ユーザー名とパスワードを入力してください。」，不发请求）
  - 用户名和密码均非空时调用 `authClient.signIn.credentials({ username: username.trim(), password, rememberMe: remember })`
  - 提交中按钮禁用并显示 Spinner + `ログイン中…`
  - 成功: `toast.success`（「ログインしました。」）并 `router.refresh()`
  - 失败: `toast.error`（`error.message`；"Invalid username or password" 本地化为「ユーザー名またはパスワードが正しくありません。」，其余原文展示）

### Mock 提示

- 展示: `テスト用（モーク API）：ユーザー名 admin／パスワード password`（卡片下方，仅未登录态显示）
- 定义: 告知当前对接 mock 第三方 API 及测试凭据
- 默认: `text-xs text-muted-foreground`
- 交互: 无

### 已登录态卡片

- 展示: 登录成功后替代表单的卡片（标题 `ログイン済み`）
- 定义: 展示当前用户信息并提供登出
- 默认: `w-full max-w-sm`
- 交互: 无

### 用户名展示

- 展示: label `ユーザー名` + 用户 name（回退 email）
- 定义: 显示当前登录用户名
- 交互: 无

### Token 展示

- 展示: label `Token` + `user.token`（等宽字体）
- 定义: 显示第三方 API 返回的 token
- 交互: 无

### Sign out（ログアウト）

- 展示: 占满卡片宽度的 outline 按钮，带 LogOut 图标
- 定义: 登出当前 session
- 默认: `type="button"`，`variant="outline"`
- 交互:
  - 点击调用 `authClient.signOut()`，`toast.success`（「ログアウトしました。」）后 `router.refresh()`

## 响应式

- lg+（≥1024px）: 左右分栏，品牌面板可见，表单区居中。
- <lg: 品牌面板隐藏，返回按钮行显示紧凑 wordmark，表单区占满宽度，容器保留 `px-6` 边距。
- 卡片使用 `w-full max-w-sm`；页面高度 `min-h-dvh`。

## 本页例外与注意

- 无品牌色：品牌视觉走中性 token（`bg-primary` 深色面板 + `text-primary-foreground`），不引入任意色值；品牌色待定（见 docs/design-system.md）。
- 当前没有主题切换入口，本页不提供主题切换。
- 登录态由 `authClient.useSession()` 判定；session 加载中（`isPending`）时表单禁用。
- 不做路由守卫：未登录访问受保护页面由各页面自行处理。
- 日文由系统字体栈回退渲染（Geist 不含日文 web font；设计系统禁止引入其他 web font）。
