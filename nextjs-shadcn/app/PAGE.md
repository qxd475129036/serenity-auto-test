# 页面: 首页 (/)

路由: `/` ｜ 文件: `app/page.tsx` ｜ 类型: Server Component
功能域: [features/home/SPEC.md](../features/home/SPEC.md)

## 布局

- 整页 flex 居中，内层 `max-w-3xl` 白色内容区（dark: 黑底）。
- 自上而下: Next.js logo → h1（模板引导文案）→ 说明文字（Templates / Learn 外链）→ 按钮区。
- 按钮区: "View Components Demo"（Link 包 Button）｜ "Deploy Now"（外链）｜ "Documentation"（外链）。

## 状态

- 静态页：无 loading / empty / error 状态。
- 响应式: 移动端按钮纵向堆叠、文案居中；`sm:` 起左对齐。

## 本页例外与注意

- 文案仍是 create-next-app 模板（"To get started, edit page.tsx"）；产品定位确定后整页重写，届时同步更新本文件。
- demo CTA 是进入功能页的唯一入口，重写时保留等价入口。
