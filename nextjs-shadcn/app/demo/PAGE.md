# shadcn 组件演示

- 路由: `/demo`
- 文件: `app/demo/page.tsx`
- 类型: Client Component（`"use client"`）
- 功能域: [shadcn 组件演示 SPEC](../../features/components-demo/SPEC.md)

## 页面元素

以下字段只记录当前页面实例。组件 API 和通用默认值以 `components/ui/*.tsx` 为准；组合子组件归入对应主组件，不单独计数。

### 顶部工具栏

- 展示: 返回按钮、页面标题、副标题和 Home 按钮
- 定义: 标识当前页面并提供返回首页入口
- 默认: 标题 `shadcn/ui Components`；副标题 `All 61 components in one page`；sticky、半透明背景和 blur
- 交互:
  - 点击返回按钮进入 `/`
  - 点击 Home 进入 `/`

### 页脚

- 展示: `Built with Next.js 16 + shadcn/ui`
- 定义: 标识页面技术栈
- 默认: 居中小字，`text-muted-foreground`
- 交互: 无

### 1. Buttons & Actions

#### Button

- 展示: 全部 variant、常用 size、图标按钮和禁用态
- 定义: 触发操作的通用按钮
- 默认: default、secondary、outline、ghost、destructive、link；sm/default/lg/icon
- 交互:
  - 点击无业务回调

#### ButtonGroup

- 展示: Left / Middle / Right 三个相连按钮
- 定义: 对相邻操作进行分组
- 默认: 三个按钮均使用 `variant="outline"`
- 交互:
  - 点击无业务回调

#### Toggle

- 展示: B、I 两个独立切换按钮
- 定义: 表示可独立开启或关闭的切换操作
- 默认: 初始未选中；I 使用 `variant="outline"`
- 交互:
  - 点击后切换对应按钮的选中状态

#### ToggleGroup

- 展示: A / B / C 三个选项
- 定义: 在多个切换项中进行单选
- 默认: `type="single"`，初始未选中
- 交互:
  - 点击选项后更新单选状态

### 2. Dropdown & Menu

#### DropdownMenu

- 展示: Dropdown 按钮和 Profile / Settings / Logout 菜单
- 定义: 由按钮触发的下拉操作菜单
- 默认: 初始关闭
- 交互:
  - 点击 Trigger 打开菜单
  - 点击菜单项后关闭，无业务回调

#### ContextMenu

- 展示: `Right-click here` 触发区域和 Copy / Paste / Delete 菜单
- 定义: 由右键触发的上下文菜单
- 默认: 初始关闭；触发区域为虚线边框
- 交互:
  - 右键点击触发区域打开菜单
  - 点击菜单项后关闭，无业务回调

#### Menubar

- 展示: File / Edit 菜单栏
- 定义: 桌面应用式多菜单导航
- 默认: 初始关闭；包含快捷键提示
- 交互:
  - 点击 File 或 Edit 打开对应菜单
  - 点击菜单项后关闭，无业务回调

### 3. Forms

#### Input

- 展示: Username 单行输入框
- 定义: 输入单行文本
- 默认: placeholder `Enter username`，初始值 `""`
- 交互:
  - 输入内容保存在控件自身，Demo 不读取或提交

#### Textarea

- 展示: Bio 多行输入框
- 定义: 输入多行文本
- 默认: placeholder `Tell us about yourself`，`rows={2}`
- 交互:
  - 输入内容保存在控件自身，Demo 不读取或提交

#### Checkbox

- 展示: `Accept terms and conditions`
- 定义: 选择布尔状态
- 默认: 初始未选中
- 交互:
  - 点击后切换选中状态

#### RadioGroup

- 展示: Option One / Option Two
- 定义: 从多个选项中选择一个
- 默认: 默认选中 `option-one`
- 交互:
  - 选择后更新当前单选项

#### Switch

- 展示: `Enable notifications` 开关
- 定义: 切换持续性的开启/关闭状态
- 默认: 初始关闭
- 交互:
  - 点击后切换开关状态
  - 不触发系统通知

#### Slider

- 展示: Volume 滑杆
- 定义: 选择连续数值
- 默认: `[50]`，`max=100`，`step=1`
- 交互:
  - 拖动或键盘调整后更新当前值

#### Select

- 展示: Apple / Banana / Orange 自定义下拉框
- 定义: 从预设选项中选择一个
- 默认: 默认选中 `apple`
- 交互:
  - 打开菜单并选择后更新当前值

#### NativeSelect

- 展示: Apple / Banana / Orange 原生下拉框
- 定义: 使用原生控件选择预设值
- 默认: 默认选中 `apple`
- 交互:
  - 选择后更新当前值

#### Combobox

- 展示: `Select framework` 可搜索选择器
- 定义: 通过输入过滤并选择选项
- 默认: 初始未选择；选项 Next.js / Vite / Astro
- 交互:
  - 输入后过滤选项
  - 选择后更新当前值，无后续业务

#### InputGroup

- 展示: Mail 图标、邮箱输入和后缀 `.com`
- 定义: 组合前缀、输入框和后缀内容
- 默认: placeholder `you@example.com`
- 交互:
  - 输入内容保存在控件自身，Demo 不读取或提交

#### Field

- 展示: Username、Bio 两个字段组合
- 定义: 组织 Label、控件和说明文字
- 默认: Username 含公开名称说明；Bio 使用 `Textarea`
- 交互: 无

#### Label

- 展示: Checkbox、Switch、Slider 等控件的文字标签
- 定义: 描述控件并提供关联点击区域
- 默认: 使用 `text-sm` 页面样式
- 交互:
  - 点击与控件正确关联的 Label 时聚焦或切换对应控件

#### InputOTP

- 展示: OTP Code 分段验证码输入
- 定义: 输入一次性验证码
- 默认: `maxLength={6}`；页面渲染 3 个 slot，初始为空
- 交互:
  - 输入后更新验证码字符
  - 不校验、不提交

### 4. Data Display

#### Avatar

- 展示: shadcn 远程头像、`CN` 回退、AvatarGroup 和数量 `3`
- 定义: 展示用户头像及回退内容
- 默认: 单个头像使用远程图片；头像组使用 AB / CD 回退
- 交互: 无

#### Badge

- 展示: Default、Secondary、Outline、Destructive
- 定义: 展示简短状态或分类
- 默认: 四种变体各展示一次
- 交互: 无

#### Table

- 展示: Name / Role / Status 表和两行成员数据
- 定义: 展示结构化数据
- 默认: Alice / Designer / Active；Bob / Engineer / Away
- 交互: 无

#### Tabs

- 展示: Account / Password 两个页签
- 定义: 在同一区域切换不同内容
- 默认: 默认显示 `account`
- 交互:
  - 点击页签后切换对应内容

#### Accordion

- 展示: 两个可折叠问答项
- 定义: 按需展开内容
- 默认: `type="single"`、`collapsible`、默认展开 `item-1`
- 交互:
  - 点击标题展开或收起对应项
  - 允许收起当前项

#### Collapsible

- 展示: Show / Hide content 按钮和说明内容
- 定义: 单独控制一块内容展开或收起
- 默认: 初始关闭
- 交互:
  - 点击按钮切换展开状态
  - 按钮文案随状态切换

#### Kbd

- 展示: `⌘` 和 `K`
- 定义: 展示键盘按键或快捷键
- 默认: 两个独立 Kbd
- 交互: 无

#### Breadcrumb

- 展示: Home / Components / Demo
- 定义: 展示当前页面在信息层级中的位置
- 默认: 前两级为 `href="#"` 链接，末级为当前页
- 交互:
  - 点击前两级链接跟随 `#` 占位地址

#### Pagination

- 展示: Previous / 1 / 2 / Ellipsis / Next
- 定义: 展示分页导航
- 默认: 链接均为 `href="#"`
- 交互:
  - 点击链接跟随 `#` 占位地址

#### NavigationMenu

- 展示: Getting started 菜单及 Introduction / Installation 链接
- 定义: 展示可展开的站点导航
- 默认: 初始关闭；链接为 `href="#"`
- 交互:
  - 点击 Trigger 打开菜单
  - 点击内容链接跟随 `#` 占位地址

#### Empty

- 展示: Mail 图标、`No messages` 说明和 Compose 按钮
- 定义: 展示空数据状态及建议操作
- 默认: `EmptyMedia variant="icon"`，Compose 使用小号按钮
- 交互:
  - 点击 Compose 无业务回调

#### Marker

- 展示: `Section Title`
- 定义: 使用分隔标记强调内容分组
- 默认: `variant="separator"`
- 交互: 无

#### Item

- 展示: Alice Brown / Product Designer；Charlie Davis / Engineer
- 定义: 展示成员或资源条目
- 默认: 使用 Avatar、ItemContent 和 ItemSeparator
- 交互: 无

#### Calendar

- 展示: 单月日历
- 定义: 选择日期
- 默认: `mode="single"`，初始未选择日期
- 交互:
  - 点击日期后更新当前选中日期

### 5. Feedback

#### Alert

- 展示: 默认提示和 destructive 错误提示
- 定义: 在页面内传达重要信息
- 默认: 一个默认变体；一个 `variant="destructive"`
- 交互: 无

#### AlertDialog

- 展示: Open Alert Dialog 按钮、确认标题、说明、Cancel 和 Continue
- 定义: 要求用户确认高风险操作
- 默认: 初始关闭
- 交互:
  - 点击按钮打开对话框
  - Cancel 关闭并放弃操作
  - Continue 关闭对话框，无业务回调

#### Progress

- 展示: Loading 文案、60% 和进度条
- 定义: 展示任务完成进度
- 默认: `value={60}`
- 交互: 无

#### Skeleton

- 展示: 圆形头像占位和两行文本占位
- 定义: 表示内容正在加载
- 默认: 静态占位，尺寸分别为圆形、32×4、24×3
- 交互: 无

#### Spinner

- 展示: 默认尺寸和 `size-6` 两个加载指示器
- 定义: 表示异步操作进行中
- 默认: 两个实例
- 交互: 无

#### Sonner

- 展示: Toast 按钮
- 定义: 触发 Sonner 通知
- 默认: 按钮使用默认变体
- 交互:
  - 点击后显示成功 toast `Success!`

#### Tooltip

- 展示: Hover me 按钮和短暂说明
- 定义: 在悬浮或聚焦时补充文字说明
- 默认: 初始关闭；内容 `This is a tooltip`
- 交互:
  - 悬浮或聚焦触发器时打开
  - 离开后关闭

#### HoverCard

- 展示: Hover for card 按钮和详情浮层
- 定义: 在悬浮时展示更丰富的补充内容
- 默认: 初始关闭；内容为额外说明文字
- 交互:
  - 悬浮或聚焦触发器时打开
  - 离开后关闭

### 6. Overlays

#### Dialog

- 展示: Open Dialog 按钮、标题、说明和 Confirm 按钮
- 定义: 在当前页面之上展示模态内容
- 默认: 初始关闭
- 交互:
  - 点击按钮打开对话框
  - 点击 Confirm 无业务回调
  - 使用内置关闭机制关闭

#### Sheet

- 展示: Open Sheet 按钮和侧边面板
- 定义: 从页面边缘展示补充内容
- 默认: 初始关闭；面板含标题和描述
- 交互:
  - 点击按钮打开 Sheet
  - 使用内置关闭机制关闭

#### Drawer

- 展示: Open Drawer 按钮和底部抽屉
- 定义: 从底部展示补充内容或操作
- 默认: 初始关闭；含标题、描述和 Submit 按钮
- 交互:
  - 点击按钮打开 Drawer
  - 点击 Submit 无业务回调
  - 使用内置关闭机制关闭

#### Popover

- 展示: Open Popover 按钮和锚定浮层
- 定义: 在触发器附近展示临时内容
- 默认: 初始关闭；宽度 `w-72`
- 交互:
  - 点击按钮打开
  - 点击外部关闭

### 7. Layout

#### Card

- 展示: 标题、描述、正文、Action 按钮和 CardFooter
- 定义: 将相关内容组织为独立卡片
- 默认: CardTitle `Card Title`；CardDescription `Card description`
- 交互:
  - 点击 Action 无业务回调

#### Separator

- 展示: Above 和 Below 两段文字之间的分隔线
- 定义: 分隔相关内容
- 默认: 使用默认水平分隔线
- 交互: 无

#### AspectRatio

- 展示: `16:9 Aspect Ratio` 内容盒
- 定义: 保持固定宽高比
- 默认: `ratio={16 / 9}`，背景 `bg-muted`
- 交互: 无

#### ScrollArea

- 展示: 20 条 Scroll item
- 定义: 在固定区域内提供自定义滚动
- 默认: 高度 `h-24`，带边框
- 交互:
  - 滚动浏览内容

#### Resizable

- 展示: Panel 1 / Panel 2 水平分栏
- 定义: 允许用户调整面板尺寸
- 默认: `orientation="horizontal"`，两个 Panel 各 50%
- 交互:
  - 拖动 ResizableHandle 调整两侧宽度

#### Sidebar

- 展示: Workspace、Home / Settings 菜单、SidebarTrigger 和内容区
- 定义: 展示应用侧边导航
- 默认: 包裹在 SidebarProvider 中，带边框
- 交互:
  - 点击 SidebarTrigger 展开或收起侧边栏
  - 点击 Home / Settings 无业务回调

### 8. Media & Charts

#### Carousel

- 展示: 5 张 Slide 和 Previous / Next 按钮
- 定义: 在有限宽度内轮播内容
- 默认: 最大宽度 `max-w-xs`
- 交互:
  - 点击 Previous / Next 切换 Slide

#### Chart

- 展示: 3 个月的 desktop / mobile 折线图
- 定义: 使用图表展示趋势数据
- 默认: 静态数组；`LineChart`、CartesianGrid、Tooltip 和两条折线
- 交互:
  - 悬浮图表显示 ChartTooltip

#### Command

- 展示: 搜索框、Empty 状态和 Suggestions 列表
- 定义: 搜索并选择命令
- 默认: placeholder `Type a command or search...`；3 个建议项
- 交互:
  - 输入时过滤命令
  - 点击建议项无业务回调

### 9. Chat UI

#### Bubble

- 展示: 两条聊天气泡和 👍 reaction
- 定义: 展示聊天消息及反应
- 默认: 第一条默认样式；第二条 `variant="muted"`、`align="end"`
- 交互:
  - 点击 👍 无业务回调

#### Message

- 展示: AI 和用户两条带头像的消息
- 定义: 展示标准聊天消息布局
- 默认: 两条静态消息
- 交互: 无

#### MessageScroller

- 展示: 高度 `h-40` 的消息滚动区域和一组对话
- 定义: 承载可滚动的聊天记录
- 默认: 带边框和 `p-3` 内容间距
- 交互:
  - 滚动浏览消息

#### Attachment

- 展示: Mail 图标、`document.pdf` 和 `2.4 MB`
- 定义: 展示聊天附件及文件信息
- 默认: `AttachmentMedia variant="icon"`
- 交互: 无

### 10. Other

#### Questionnaire

- 展示: 进度 `1 of 3`、框架单选题和 Next 按钮
- 定义: 展示分步问卷交互
- 默认: Next.js / Vite / Astro，初始未选择
- 交互:
  - 选择选项后更新当前答案
  - 提交问卷后显示成功 toast `Questionnaire submitted!`

#### DirectionProvider

- 展示: 无可见 UI
- 定义: 为页面提供文字方向上下文
- 默认: `dir="ltr"`
- 交互: 无

## 响应式

- 页面固定为单列长页，10 个 Section 纵向排列。
- 顶部工具栏保持单行；主内容和工具栏统一使用 `max-w-5xl` 与 `px-4`。
- Forms 和 Layout 的双列网格在 `sm:` 起生效，移动端回退为单列。
- 复杂示例保持在容器内滚动或换行，不产生页面级横向滚动。

## 本页例外与注意

- 本页按 UI 模块维护；AvatarGroup、InputOTPSlot、SidebarMenu 等组合子组件归入对应主组件。
- 61 个组件的完整性以 `components/ui/*.tsx` 实际导出和本页导入清单为准。
- 单文件约 1210 行；拆分方案见功能域 SPEC 的开放问题第 1 项，决定前不拆。
