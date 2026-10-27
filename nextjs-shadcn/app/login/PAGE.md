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

### 登录卡片

- 展示: 居中的登录表单容器
- 定义: 承载登录表单及演示说明
- 默认: `w-full max-w-sm`
- 交互: 无

### 卡片标题与说明

- 展示: `Sign in to your account` 和 `Enter your credentials to continue.`
- 定义: 说明页面用途和下一步操作
- 默认: 使用 CardHeader、CardTitle 和 CardDescription
- 交互: 无

### 邮箱输入

- 展示: Email Label、Mail 图标和输入框
- 定义: 输入登录邮箱
- 默认: `type="email"`，`autoComplete="email"`，placeholder `you@example.com`，初始值 `""`
- 交互:
  - 输入时更新 `email` 本地状态

### 密码输入

- 展示: Password Label、Lock 图标和密码框
- 定义: 输入登录密码
- 默认: `type="password"`，`autoComplete="current-password"`，初始值 `""`
- 交互:
  - 输入时更新 `password` 本地状态

### Remember me

- 展示: Checkbox 和关联 Label
- 定义: 记录是否记住登录状态
- 默认: 初始值 `false`
- 交互:
  - 切换时更新 `remember` 本地状态
  - 当前不持久化

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
  - 邮箱或密码为空时阻止默认提交并显示 `toast.error`
  - 邮箱和密码均非空时阻止默认提交并显示 `toast.success`
  - 邮箱提交前去除首尾空格，密码不做 trim

### Demo 提示

- 展示: `Demo only — no backend wired yet.`
- 定义: 告知当前页面未接入后端
- 默认: `text-xs text-muted-foreground`
- 交互: 无

## 响应式

- 页面使用 `min-h-screen`，登录卡片在视口内垂直水平居中。
- 卡片使用 `w-full max-w-sm`；移动端由页面容器保留 `px-4` 边距。
- 当前无额外断点行为。

## 本页例外与注意

- 当前没有主题切换入口，本页不提供主题切换。
- 无后端、无 loading、无服务端错误状态，也不发生登录后跳转。
- 接入真实认证时补充 loading、服务端错误、session 和跳转说明。
