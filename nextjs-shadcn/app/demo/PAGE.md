# 页面: 组件演示 (/demo)

路由: `/demo` ｜ 文件: `app/demo/page.tsx` ｜ 类型: Client Component（`"use client"`）
功能域: [features/components-demo/SPEC.md](../../features/components-demo/SPEC.md)

## 布局

- 顶部 header: h1 "shadcn/ui Components" + 副标题（All 61 components in one page）+ 返回首页按钮（Link 包 Button）。
- 主体: 10 个 `<section>` 纵向堆叠；section 内用 Card 网格，每组件一个 Card：CardTitle（组件名）+ CardDescription（分类说明）+ CardContent（示例）。
- 页内渲染 `<Toaster />`（sonner）。

## Section 顺序与内容（10 节）

1. Buttons & Actions — Button（各 variant/size）、ButtonGroup、Toggle、ToggleGroup
2. Dropdown & Menu — DropdownMenu、ContextMenu、Menubar
3. Forms — Input、Textarea、Checkbox、RadioGroup、Switch、Slider、Select、NativeSelect、Combobox、InputGroup、Field、Label、InputOTP
4. Data Display — Avatar、Badge、Table、Tabs、Accordion、Collapsible、Kbd、Breadcrumb、Pagination、NavigationMenu、Empty、Marker、Item、Calendar
5. Feedback — Alert、AlertDialog、Progress、Skeleton、Spinner、Sonner（按钮触发 toast）、Tooltip、HoverCard
6. Overlays — Dialog、Sheet、Drawer、Popover
7. Layout — Card、Separator、AspectRatio、ScrollArea、Resizable、Sidebar
8. Media & Charts — Carousel、Chart（recharts 折线图）、Command
9. Chat UI — Bubble、Message、MessageScroller、Attachment
10. Other — Questionnaire、DirectionProvider

## 交互模式

- 浮层类（Dialog/Sheet/Drawer/AlertDialog/Popover/HoverCard/ContextMenu/DropdownMenu）: `useState` 控制 open。
- Tabs/Accordion/Collapsible: 给 `defaultValue`。
- Chart: 静态数据数组（LineChart + CartesianGrid）。
- Sonner: 按钮调用 `toast.success(...)`。
- 复杂组件（Sidebar/Questionnaire/MessageScroller）: 最小可运行示例。

## 状态

- 无 loading / empty / error（全静态数据）。

## 响应式

- 单列长页；Card 网格自动换行，移动端纵向堆叠。无额外断点行为；未来新增时记录在本节。

## 本页例外与注意

- 单文件约 1210 行；拆分为 section 组件的方案在功能域 SPEC 开放问题 2 中，决定前不拆。
- 原变体页 `/demo1` 已于 2026-10 转为登录页 `/login`（见 features/login/SPEC.md）；本页为组件演示唯一真相源。
