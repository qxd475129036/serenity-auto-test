# 登录

- 路由: `/login`
- 文件: `app/login/page.tsx`
- 类型: Client Component（`"use client"`）
- 功能域: [登录 SPEC](../../features/login/SPEC.md)

## 页面元素

以下字段只记录当前页面实例。组件 API 和通用默认值以 `components/ui/*.tsx` 为准。

### 返回按钮

- 展示: ArrowLeft 图标按钮
- 定义: 返回项目首页
- 默认: `variant="ghost"`，`size="icon-sm"`，`aria-label="Go home"`
- 交互:
  - 点击后进入 `/`

### 登录卡片（未登录态）

- 展示: 居中的登录表单容器
- 定义: 承载用户名/密码登录表单
- 默认: `w-full max-w-sm`
- 交互: 无

### 卡片标题与说明

- 展示: `Sign in to your account` 和 `Enter your credentials to continue.`
- 定义: 说明页面用途
- 默认: 使用 CardHeader、CardTitle 和 CardDescription
- 交互: 无

### 用户名输入

- 展示: Username Label、User 图标和输入框
- 定义: 输入登录用户名
- 默认: `type="text"`，`autoComplete="username"`，placeholder `username`，初始值 `""`
- 交互:
  - 输入时更新 `username` 本地状态
  - 提交中或 session 加载中时禁用

### 密码输入

- 展示: Password Label、Lock 图标和密码框
- 定义: 输入登录密码
- 默认: `type="password"`，`autoComplete="current-password"`，初始值 `""`
- 交互:
  - 输入时更新 `password` 本地状态
  - 提交中或 session 加载中时禁用

### Remember me

- 展示: Checkbox 和关联 Label
- 定义: 记录是否记住登录状态（作为 `rememberMe` 传给 Better Auth）
- 默认: 初始值 `false`
- 交互:
  - 切换时更新 `remember` 本地状态
  - 提交中或 session 加载中时禁用

### Forgot password?

- 展示: Link 样式按钮
- 定义: 预留找回密码入口
- 默认: `type="button"`
- 交互:
  - 点击后无业务回调
  - 当前不跳转

### Sign in

- 展示: 占满卡片宽度的主按钮
- 定义: 提交登录表单
- 默认: 主按钮，`type="submit"`
- 交互:
  - 用户名或密码为空时阻止默认提交并显示 `toast.error`
  - 用户名和密码均非空时调用 `authClient.signIn.credentials({ username: username.trim(), password, rememberMe: remember })`
  - 提交中按钮禁用并显示 `Signing in...`
  - 成功: `toast.success` 并 `router.refresh()`；失败: `toast.error(error.message)`

### 已登录态卡片

- 展示: 登录成功后替代表单的卡片
- 定义: 展示当前用户信息并提供登出
- 默认: `w-full max-w-sm`
- 交互: 无

### 用户名展示

- 展示: label `Username` + 用户 name（回退 email）
- 定义: 显示当前登录用户名
- 交互: 无

### Token 展示

- 展示: label `Token` + `user.token`（等宽字体）
- 定义: 显示第三方 API 返回的 token
- 交互: 无

### Sign out

- 展示: 占满卡片宽度的 outline 按钮，带 LogOut 图标
- 定义: 登出当前 session
- 默认: `type="button"`，`variant="outline"`
- 交互:
  - 点击调用 `authClient.signOut()`，`toast.success` 后 `router.refresh()`

### Demo 提示

- 展示: `Mock third-party API — try username admin / password password.`
- 定义: 告知当前对接 mock 第三方 API 及测试凭据
- 默认: `text-xs text-muted-foreground`
- 交互: 无

## 响应式

- 页面使用 `min-h-screen`，卡片在视口内垂直水平居中。
- 卡片使用 `w-full max-w-sm`；移动端由页面容器保留 `px-4` 边距。
- 当前无额外断点行为。

## 本页例外与注意

- 当前没有主题切换入口，本页不提供主题切换。
- 登录态由 `authClient.useSession()` 判定；session 加载中（`isPending`）时表单禁用。
- 不做路由守卫：未登录访问受保护页面由各页面自行处理。
