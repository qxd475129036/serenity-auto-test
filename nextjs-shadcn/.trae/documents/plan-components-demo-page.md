# 计划:创建 shadcn 组件 Demo 子页面

## 概述

创建一个 `/demo` 子页面,将全部 61 个 shadcn 组件按分类呈现为可交互的演示;在主页 `/` 添加一个按钮跳转至该页面。

## 当前状态

- Next.js 16 + App Router + Tailwind v4 + shadcn(radix-nova 风格)已就绪。
- [app/layout.tsx](file:///Users/quxd/git/nextjs-shadcn/app/layout.tsx) 已包裹 `TooltipProvider`。
- `components/ui/` 下有 61 个组件文件,导出符号已确认(见附录)。
- 主页 [app/page.tsx](file:///Users/quxd/git/nextjs-shadcn/app/page.tsx) 为 create-next-app 默认模板。

## 变更内容

### 1. 新建 `app/demo/page.tsx`(客户端组件)

**文件**: `app/demo/page.tsx`

- 顶部 `"use client"`。
- 顶部统一导入所有需要的组件(来自 `@/components/ui/*`)、`useState`、`toast`(sonner)、recharts 数据等。
- 页面结构:
  - 顶部 header:标题 "shadcn/ui Components" + 返回首页按钮(Link + Button)。
  - 页面内渲染 `<Toaster />` 使 sonner toast 可用。
  - 按分类用 `Card` 包裹,每个组件一个独立的小区块,含组件名标题与示例。

**分类与示例设计**:

1. **Buttons**: Button(各 variant/size)、ButtonGroup、Toggle、ToggleGroup
2. **Dropdown & Menu**: DropdownMenu、ContextMenu、Menubar
3. **Forms**: Input、Textarea、Checkbox、RadioGroup、Switch、Slider、Select、NativeSelect、Combobox、InputGroup、Field、Label、InputOTP
4. **Data Display**: Avatar、Badge、Table、Tabs、Accordion、Collapsible、Kbd、Breadcrumb、Pagination、NavigationMenu、Empty、Marker、Item、Calendar
5. **Feedback**: Alert、AlertDialog、Progress、Skeleton、Spinner、Sonner(toast 按钮触发)、Tooltip、HoverCard
6. **Overlays**: Dialog、Sheet、Drawer、Popover
7. **Layout**: Card、Separator、AspectRatio、ScrollArea、Resizable、Sidebar
8. **Media & Charts**: Carousel、Chart(recharts 折线图示例)、Command
9. **Chat UI**: Bubble、Message、MessageScroller、Attachment
10. **Other**: Questionnaire、DirectionProvider

**关键交互实现**:
- Dialog/Sheet/Drawer/AlertDialog/ContextMenu/DropdownMenu/Popover/HoverCard 等用 `useState` 控制 `open`。
- Tabs/Accordion/Collapsible 给默认值。
- Chart 提供静态数据数组。
- Calendar 渲染 `<Calendar />`。
- Sonner 用按钮 `toast.success(...)` 触发。
- Questionnaire 用其默认问题结构。

### 2. 修改 `app/page.tsx`

- 保留原有内容,在按钮区(Docs/Deploy 附近)新增一个 `<Button>`(variant default),用 `next/link` 的 `<Link href="/demo">` 包裹,文案如 "View Components Demo"。

## 假设与决策

- Demo 页面为单个大文件,不拆分,方便集中查看。
- 所有示例尽量用默认 props,复杂组件(Sidebar/Questionnaire/MessageScroller)使用最小可运行示例。
- 不修改 `layout.tsx`(TooltipProvider 已在;Toaster 放在 demo 页内避免影响首页)。
- 不引入新依赖(全部用已有组件与已装库)。

## 验证

- `npm run build` 通过(TS 类型检查 + 生产构建)。
- 首页按钮可点击跳转 `/demo`。
- `/demo` 页面所有组件渲染无报错。

## 附录:组件导出清单

| 组件文件 | 导出 |
|---|---|
| accordion | Accordion, AccordionItem, AccordionTrigger, AccordionContent |
| alert | Alert, AlertTitle, AlertDescription, AlertAction |
| alert-dialog | AlertDialog... |
| aspect-ratio | AspectRatio |
| attachment | Attachment... |
| avatar | Avatar, AvatarImage, AvatarFallback |
| badge | Badge, badgeVariants |
| breadcrumb | Breadcrumb... |
| bubble | BubbleGroup, Bubble, BubbleContent, BubbleReactions |
| button | Button, buttonVariants |
| button-group | ButtonGroup... |
| calendar | Calendar, CalendarDayButton |
| card | Card, CardHeader, CardTitle, CardDescription, CardAction, CardContent, CardFooter |
| carousel | Carousel... |
| chart | ChartContainer, ChartTooltip, ChartLegendContent, ChartStyle |
| checkbox | Checkbox |
| collapsible | Collapsible, CollapsibleTrigger, CollapsibleContent |
| combobox | Combobox... |
| command | Command... |
| context-menu | ContextMenu... |
| dialog | Dialog, DialogTrigger, DialogPortal, DialogClose, DialogOverlay, DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription |
| direction | DirectionProvider, useDirection |
| drawer | Drawer... |
| dropdown-menu | DropdownMenu... |
| empty | Empty... |
| field | Field... |
| hover-card | HoverCard, HoverCardTrigger, HoverCardContent |
| input | Input |
| input-group | InputGroup... |
| input-otp | InputOTP, InputOTPGroup, InputOTPSlot, InputOTPSeparator |
| item | Item... |
| kbd | Kbd, KbdGroup |
| label | Label |
| marker | Marker, MarkerIcon, MarkerContent, markerVariants |
| menubar | Menubar... |
| message | Message... |
| message-scroller | MessageScroller... |
| native-select | NativeSelect, NativeSelectOptGroup, NativeSelectOption |
| navigation-menu | NavigationMenu... |
| pagination | Pagination... |
| popover | Popover, PopoverTrigger, PopoverContent |
| progress | Progress |
| questionnaire | Questionnaire... |
| radio-group | RadioGroup, RadioGroupItem |
| resizable | ResizableHandle, ResizablePanel, ResizablePanelGroup |
| scroll-area | ScrollArea, ScrollBar |
| select | Select... |
| separator | Separator |
| sheet | Sheet... |
| sidebar | Sidebar... |
| skeleton | Skeleton |
| slider | Slider |
| sonner | Toaster |
| spinner | Spinner |
| switch | Switch |
| table | Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption |
| tabs | Tabs, TabsList, TabsTrigger, TabsContent |
| textarea | Textarea |
| toggle | Toggle, toggleVariants |
| toggle-group | ToggleGroup, ToggleGroupItem |
| tooltip | Tooltip, TooltipTrigger, TooltipContent |
