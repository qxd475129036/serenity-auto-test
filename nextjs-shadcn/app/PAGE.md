# 首页

- 路由: `/`
- 文件: `app/page.tsx`
- 类型: Server Component
- 功能域: [首页 SPEC](../features/home/SPEC.md)

## 页面元素

以下字段只记录当前页面实例。组件 API 和通用默认值以 `components/ui/*.tsx` 为准。

### Next.js logo

- 展示: Next.js 品牌图片
- 定义: 标识当前页面来自 create-next-app 模板
- 默认: `/next.svg`，`100 × 20`，启用 `priority`
- 交互: 无

### 主标题

- 展示: `To get started, edit the page.tsx file.`
- 定义: 提示开发者从页面入口开始修改
- 默认: 使用模板 h1 样式，`max-w-xs`
- 交互: 无

### 说明文字

- 展示: 模板引导文案
- 定义: 引导开发者查找模板和学习资料
- 默认: `Looking for a starting point or more instructions?`
- 交互: 无

### Templates

- 展示: 说明文字中的 Templates 链接
- 定义: 打开 Vercel Templates
- 默认: 外部文本链接，当前标签页打开
- 交互:
  - 点击后打开 Vercel Templates

### Learning center

- 展示: 说明文字中的 Learning center 链接
- 定义: 打开 Next.js Learn
- 默认: 外部文本链接，当前标签页打开
- 交互:
  - 点击后打开 Next.js Learn

### View Components Demo

- 展示: 主操作按钮
- 定义: 进入 shadcn 组件演示页
- 默认: `Link` 包裹 `Button`，`size="lg"`
- 交互:
  - 点击后进入 `/demo`

### Deploy Now

- 展示: Vercel 图标和 Deploy Now 文案
- 定义: 打开 Vercel 新建项目页面
- 默认: 外链，新标签页打开，带 `noopener noreferrer`
- 交互:
  - 点击后在新标签页打开 Vercel 新建项目页面

### Documentation

- 展示: Documentation 操作项
- 定义: 打开 Next.js 文档
- 默认: 外链，新标签页打开，带 `noopener noreferrer`
- 交互:
  - 点击后在新标签页打开 Next.js 文档

## 响应式

- 移动端内容居中，操作按钮纵向排列。
- `sm:` 起内容左对齐，操作按钮横向排列。

## 本页例外与注意

- 页面仍是 create-next-app 模板，使用部分模板专属颜色和原生链接；产品首页重写时应迁移到设计 token 和标准 Button。
- 当前为静态页面，无本地状态、loading、empty 或 error 状态。
- demo CTA 是进入组件演示页的唯一入口，重写时保留等价入口。
