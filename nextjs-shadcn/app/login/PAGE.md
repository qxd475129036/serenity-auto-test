# 页面: 登录 (/login)

路由: `/login` ｜ 文件: `app/login/page.tsx` ｜ 类型: Client Component（`"use client"`）
功能域: [features/login/SPEC.md](../../features/login/SPEC.md)

## 布局

- 整页垂直水平居中（`min-h-screen` + flex center），背景 `bg-background`。
- 左上返回: Link 包 Button（ghost icon，`ArrowLeftIcon`，aria-label "Go home"）回首页 `/`。
- 主体: 单个 Card（`max-w-sm`），CardHeader（标题 "Sign in to your account" + 描述）+ CardContent（表单）。
- 表单: Field/FieldLabel/FieldGroup + InputGroup（前缀图标 Mail/Lock）的邮箱、密码两个字段；
  Checkbox "Remember me" + Label（htmlFor/id 关联）；"Forgot password?" 为 Button link 变体（type="button"）。
- 提交按钮: Button（default，`type="submit"`，`w-full`）。
- 页脚小字: "Demo only — no backend wired yet."（muted-foreground）。
- 本页自行渲染 `<Toaster />` 与 `<DirectionProvider dir="ltr">`（同 demo 页模式）。

## 交互模式

- 邮箱/密码/记住我均为本地 `useState`。
- 提交: `preventDefault`；空值 → `toast.error`；非空 → `toast.success("Signed in as {email} (demo)")`。
- 无后端、无 loading 态、无路由跳转（骨架阶段）。

## 状态

- 无 loading / empty / error 页面状态；校验失败用 toast 反馈。

## 响应式

- 单列居中卡片，`max-w-sm`；移动端全宽（`px-4`）。无额外断点行为。

## 本页例外与注意

- 本路由原为 `/demo1`（组件演示变体页，与 `/demo` 仅一行副标题差异），2026-10 改作登录页，原变体页内容不保留（`/demo` 已是真相源）。
