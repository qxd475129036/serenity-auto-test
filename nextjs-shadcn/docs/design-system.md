# 设计系统

## 设计 Token（真相源: app/globals.css）

- 色彩: oklch 表色，shadcn `neutral` 中性灰基调（无品牌色，品牌色待定）。
- 双主题变量集: `:root`（亮色）与 `.dark`（暗色）。
- Tailwind v4 通过 `@theme inline` 把 CSS 变量映射为工具类（`--color-background` → `bg-background` 等）。

### 核心 Token 速查

| Token | 亮色 | 暗色 | 用途 |
|---|---|---|---|
| `--background` | oklch(1 0 0) | oklch(0.145 0 0) | 页面背景 |
| `--foreground` | oklch(0.145 0 0) | oklch(0.985 0 0) | 正文 |
| `--primary` / `--primary-foreground` | oklch(0.205 0 0) / oklch(0.985 0 0) | 反转 | 主按钮 |
| `--secondary` `--muted` `--accent` | oklch(0.97 0 0) | oklch(0.269 0 0) | 次级表面 |
| `--destructive` | oklch(0.577 0.245 27.325) | oklch(0.704 0.191 22.216) | 错误/删除（唯一彩色） |
| `--border` / `--input` | oklch(0.922 0 0) | oklch(1 0 0 / 10–15%) | 边框/输入框 |
| `--ring` | oklch(0.708 0 0) | oklch(0.556 0 0) | 焦点环 |
| `--card` `--popover` | oklch(1 0 0) / oklch(1 0 0) | oklch(0.205 0 0) | 卡片/浮层 |
| `--chart-1..5` | 灰阶 5 档 | 同左 | 图表配色 |
| `--sidebar*` | 见 globals.css | 见 globals.css | Sidebar 系列 |

完整数值以 `app/globals.css` 的 `:root` / `.dark` 段落为准，本文档不复述全量（单一真相源）。

### 圆角

基准 `--radius: 0.625rem`（10px）。Tailwind 圆角刻度由倍数派生: sm 0.6x、md 0.8x、lg 1x、xl 1.4x、2xl 1.8x、3xl 2.2x、4xl 2.6x。常规卡片/面板用 `rounded-lg` 及以下，勿用超大圆角。

### 字体

- 无衬线: Geist（next/font/google，CSS 变量 `--font-geist-sans`）
- 等宽: Geist Mono（`--font-geist-mono`）
- `html` 默认 `font-sans`；不引入其他 web font。

### 基础样式（@layer base）

- `*`: `border-border outline-ring/50`
- `body`: `bg-background text-foreground`

## 组件使用规则

- 一律从 `@/components/ui/*` 导入，不用相对路径。
- 动态 class 用 `cn()`（`@/lib/utils`）合并，不字符串拼接。
- 图标只用 lucide-react。
- 内容分组用 Card；一个演示块 = 一个 Card（CardTitle + CardDescription + CardContent）。
- 操作反馈用 sonner toast；触发 toast 的页面必须自行渲染 `<Toaster />`（当前 demo 页各带一个）。
- 按钮用 `Button` 的 variant/size（default/secondary/ghost/outline/destructive/link；sm/default/lg/icon），不用裸 `<button>` 复刻样式。

## 可访问性基线

- 交互元素可键盘到达，且焦点环可见（依赖 `--ring`，勿覆盖掉 outline）。
- 表单控件必须有 `<Label>` 关联（htmlFor / id）。
- Dialog、Sheet、Drawer 等浮层的 aria 交给 shadcn 组件内置实现，不手写 aria。
- 纯图标按钮必须有 `aria-label` 或 Tooltip。
- 图片必须有 `alt`。

## 禁令

- 主视觉不用任意色值（裸 hex/rgb），一律走 token 类（如 `bg-primary`、`text-muted-foreground`）。
- 通用规则不复制进页面级 PAGE.md；页面只写"本页例外"。
