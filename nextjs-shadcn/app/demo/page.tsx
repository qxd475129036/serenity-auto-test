"use client"

import Link from "next/link"
import { useState } from "react"
import { toast } from "sonner"
import {
  CartesianGrid,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from "recharts"
import {
  ArrowLeftIcon,
  ChevronDownIcon,
  HomeIcon,
  MailIcon,
  SettingsIcon,
  SparklesIcon,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { ButtonGroup, ButtonGroupSeparator } from "@/components/ui/button-group"
import { Toggle } from "@/components/ui/toggle"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarShortcut,
  MenubarTrigger,
} from "@/components/ui/menubar"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { NativeSelect, NativeSelectOption } from "@/components/ui/native-select"
import {
  Combobox,
  ComboboxContent,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
  ComboboxTrigger,
} from "@/components/ui/combobox"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
  InputGroupText,
} from "@/components/ui/input-group"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Label } from "@/components/ui/label"
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "@/components/ui/input-otp"
import {
  Avatar,
  AvatarFallback,
  AvatarGroup,
  AvatarGroupCount,
  AvatarImage,
} from "@/components/ui/avatar"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { Kbd } from "@/components/ui/kbd"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { Marker, MarkerContent, MarkerIcon } from "@/components/ui/marker"
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemHeader,
  ItemMedia,
  ItemSeparator,
  ItemTitle,
} from "@/components/ui/item"
import { Calendar } from "@/components/ui/calendar"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { Spinner } from "@/components/ui/spinner"
import { Toaster } from "@/components/ui/sonner"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { AspectRatio } from "@/components/ui/aspect-ratio"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Bubble,
  BubbleContent,
  BubbleGroup,
  BubbleReactions,
} from "@/components/ui/bubble"
import {
  Message,
  MessageAvatar,
  MessageContent,
  MessageGroup,
} from "@/components/ui/message"
import {
  MessageScroller,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from "@/components/ui/message-scroller"
import {
  Attachment,
  AttachmentContent,
  AttachmentDescription,
  AttachmentMedia,
  AttachmentTitle,
} from "@/components/ui/attachment"
import {
  Questionnaire,
  QuestionnaireActions,
  QuestionnaireChoice,
  QuestionnaireChoices,
  QuestionnaireDescription,
  QuestionnaireItem,
  QuestionnaireNext,
  QuestionnaireProgress,
  QuestionnaireTitle,
} from "@/components/ui/questionnaire"
import { DirectionProvider } from "@/components/ui/direction"

const section =
  "flex flex-col gap-3 rounded-xl border bg-card p-4 text-card-foreground"
const sectionTitle = "text-sm font-semibold text-foreground"
const sectionDesc = "text-xs text-muted-foreground"

const chartData = [
  { month: "Jan", desktop: 186, mobile: 80 },
  { month: "Feb", desktop: 305, mobile: 200 },
  { month: "Mar", desktop: 237, mobile: 120 },
  { month: "Apr", desktop: 73, mobile: 190 },
  { month: "May", desktop: 209, mobile: 130 },
  { month: "Jun", desktop: 214, mobile: 140 },
]

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "var(--chart-1)",
  },
  mobile: {
    label: "Mobile",
    color: "var(--chart-2)",
  },
} as const

const frameworkOptions = [
  { value: "next", label: "Next.js" },
  { value: "vite", label: "Vite" },
  { value: "astro", label: "Astro" },
]

export default function DemoPage() {
  const [collapsibleOpen, setCollapsibleOpen] = useState(false)

  return (
    <DirectionProvider dir="ltr">
      <Toaster />
      <div className="min-h-screen bg-background text-foreground">
        {/* Header */}
        <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <Link href="/">
                <Button variant="ghost" size="icon-sm" aria-label="Go home">
                  <ArrowLeftIcon />
                </Button>
              </Link>
              <div>
                <h1 className="text-base font-semibold leading-none">
                  shadcn/ui Components
                </h1>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  All 61 components in one page
                </p>
              </div>
            </div>
            <Link href="/">
              <Button size="sm">
                <HomeIcon />
                Home
              </Button>
            </Link>
          </div>
        </header>

        <main className="mx-auto max-w-5xl space-y-10 px-4 py-8">
          {/* Buttons */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Buttons &amp; Actions</h2>
              <p className={sectionDesc}>
                Button, ButtonGroup, Toggle, ToggleGroup
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button>Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="link">Link</Button>
              <Button size="sm">Small</Button>
              <Button size="lg">Large</Button>
              <Button size="icon" aria-label="Icon button">
                <SparklesIcon />
              </Button>
              <Button disabled>Disabled</Button>
            </div>
            <Separator />
            <div className="flex flex-wrap items-center gap-4">
              <ButtonGroup>
                <Button variant="outline">Left</Button>
                <ButtonGroupSeparator />
                <Button variant="outline">Middle</Button>
                <ButtonGroupSeparator />
                <Button variant="outline">Right</Button>
              </ButtonGroup>
              <Toggle aria-label="Toggle bold">B</Toggle>
              <Toggle variant="outline" aria-label="Toggle italic">
                I
              </Toggle>
              <ToggleGroup type="single">
                <ToggleGroupItem value="a" aria-label="A">
                  A
                </ToggleGroupItem>
                <ToggleGroupItem value="b" aria-label="B">
                  B
                </ToggleGroupItem>
                <ToggleGroupItem value="c" aria-label="C">
                  C
                </ToggleGroupItem>
              </ToggleGroup>
            </div>
          </section>

          {/* Dropdown & Menu */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Dropdown &amp; Menu</h2>
              <p className={sectionDesc}>
                DropdownMenu, ContextMenu, Menubar
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">
                    Dropdown
                    <ChevronDownIcon />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>Profile</DropdownMenuItem>
                  <DropdownMenuItem>Settings</DropdownMenuItem>
                  <DropdownMenuItem>Logout</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <ContextMenu>
                <ContextMenuTrigger asChild>
                  <div className="flex h-20 w-full cursor-context-menu items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
                    Right-click here
                  </div>
                </ContextMenuTrigger>
                <ContextMenuContent>
                  <ContextMenuItem>Copy</ContextMenuItem>
                  <ContextMenuItem>Paste</ContextMenuItem>
                  <ContextMenuSeparator />
                  <ContextMenuItem>Delete</ContextMenuItem>
                </ContextMenuContent>
              </ContextMenu>

              <Menubar>
                <MenubarMenu>
                  <MenubarTrigger>File</MenubarTrigger>
                  <MenubarContent>
                    <MenubarItem>
                      New <MenubarShortcut>⌘N</MenubarShortcut>
                    </MenubarItem>
                    <MenubarItem>Open</MenubarItem>
                    <MenubarSeparator />
                    <MenubarItem>
                      Save <MenubarShortcut>⌘S</MenubarShortcut>
                    </MenubarItem>
                  </MenubarContent>
                </MenubarMenu>
                <MenubarMenu>
                  <MenubarTrigger>Edit</MenubarTrigger>
                  <MenubarContent>
                    <MenubarItem>Undo</MenubarItem>
                    <MenubarItem>Redo</MenubarItem>
                  </MenubarContent>
                </MenubarMenu>
              </Menubar>
            </div>
          </section>

          {/* Forms */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Forms</h2>
              <p className={sectionDesc}>
                Input, Textarea, Checkbox, Radio, Switch, Slider, Select,
                Combobox, InputGroup, Field, InputOTP
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field>
                <FieldLabel>Username</FieldLabel>
                <FieldGroup>
                  <Input placeholder="Enter username" />
                </FieldGroup>
                <FieldDescription>This is your public display name.</FieldDescription>
              </Field>
              <Field>
                <FieldLabel>Bio</FieldLabel>
                <FieldGroup>
                  <Textarea placeholder="Tell us about yourself" rows={2} />
                </FieldGroup>
              </Field>
              <div className="flex items-center gap-2">
                <Checkbox id="terms" />
                <Label htmlFor="terms" className="text-sm">
                  Accept terms and conditions
                </Label>
              </div>
              <RadioGroup defaultValue="option-one">
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="option-one" id="r1" />
                  <Label htmlFor="r1" className="text-sm">
                    Option One
                  </Label>
                </div>
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="option-two" id="r2" />
                  <Label htmlFor="r2" className="text-sm">
                    Option Two
                  </Label>
                </div>
              </RadioGroup>
              <div className="flex items-center gap-2">
                <Switch id="notifs" />
                <Label htmlFor="notifs" className="text-sm">
                  Enable notifications
                </Label>
              </div>
              <div className="space-y-2">
                <Label className="text-sm">Volume</Label>
                <Slider defaultValue={[50]} max={100} step={1} />
              </div>
              <Select defaultValue="apple">
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a fruit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="apple">Apple</SelectItem>
                  <SelectItem value="banana">Banana</SelectItem>
                  <SelectItem value="orange">Orange</SelectItem>
                </SelectContent>
              </Select>
              <NativeSelect defaultValue="apple">
                <NativeSelectOption value="apple">Apple</NativeSelectOption>
                <NativeSelectOption value="banana">Banana</NativeSelectOption>
                <NativeSelectOption value="orange">Orange</NativeSelectOption>
              </NativeSelect>
              <Combobox>
                <ComboboxInput placeholder="Select framework" />
                <ComboboxContent>
                  <ComboboxList>
                    {frameworkOptions.map((o) => (
                      <ComboboxItem key={o.value} value={o.value}>
                        {o.label}
                      </ComboboxItem>
                    ))}
                  </ComboboxList>
                </ComboboxContent>
              </Combobox>
              <div className="space-y-2">
                <Label className="text-sm">Email</Label>
                <InputGroup className="w-full">
                  <InputGroupAddon>
                    <MailIcon className="size-4 opacity-50" />
                  </InputGroupAddon>
                  <InputGroupInput placeholder="you@example.com" />
                  <InputGroupText>.com</InputGroupText>
                </InputGroup>
              </div>
              <div className="space-y-2">
                <Label className="text-sm">OTP Code</Label>
                <InputOTP maxLength={6}>
                  <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                  </InputOTPGroup>
                </InputOTP>
              </div>
            </div>
          </section>

          {/* Data Display */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Data Display</h2>
              <p className={sectionDesc}>
                Avatar, Badge, Table, Tabs, Accordion, Collapsible, Kbd,
                Breadcrumb, Pagination, NavigationMenu, Empty, Marker, Item,
                Calendar
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" alt="shadcn" />
                <AvatarFallback>CN</AvatarFallback>
              </Avatar>
              <AvatarGroup>
                <Avatar>
                  <AvatarFallback>AB</AvatarFallback>
                </Avatar>
                <Avatar>
                  <AvatarFallback>CD</AvatarFallback>
                </Avatar>
                <AvatarGroupCount>3</AvatarGroupCount>
              </AvatarGroup>
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
              <Kbd>⌘</Kbd>
              <Kbd>K</Kbd>
            </div>
            <Separator />
            <Tabs defaultValue="account" className="w-full">
              <TabsList>
                <TabsTrigger value="account">Account</TabsTrigger>
                <TabsTrigger value="password">Password</TabsTrigger>
              </TabsList>
              <TabsContent value="account" className="p-2">
                Make changes to your account here.
              </TabsContent>
              <TabsContent value="password" className="p-2">
                Change your password here.
              </TabsContent>
            </Tabs>
            <Separator />
            <Accordion
              type="single"
              collapsible
              className="w-full"
              defaultValue="item-1"
            >
              <AccordionItem value="item-1">
                <AccordionTrigger>Is it accessible?</AccordionTrigger>
                <AccordionContent>
                  Yes. It adheres to the WAI-ARIA design pattern.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Is it styled?</AccordionTrigger>
                <AccordionContent>
                  Yes. It comes with default styles that match the other
                  components.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
            <Collapsible
              open={collapsibleOpen}
              onOpenChange={setCollapsibleOpen}
              className="w-full"
            >
              <CollapsibleTrigger asChild>
                <Button variant="outline" size="sm">
                  {collapsibleOpen ? "Hide" : "Show"} content
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-2 rounded-md border p-3 text-sm">
                This is collapsible content.
              </CollapsibleContent>
            </Collapsible>
            <Separator />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="#">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbLink href="#">Components</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbPage>Demo</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious href="#" />
                </PaginationItem>
                <PaginationItem>
                  <PaginationLink href="#">1</PaginationLink>
                </PaginationItem>
                <PaginationItem>
                  <PaginationLink href="#">2</PaginationLink>
                </PaginationItem>
                <PaginationItem>
                  <PaginationEllipsis />
                </PaginationItem>
                <PaginationItem>
                  <PaginationNext href="#" />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
            <NavigationMenu>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuTrigger>Getting started</NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <div className="grid w-80 gap-3 p-4">
                      <NavigationMenuLink href="#">Introduction</NavigationMenuLink>
                      <NavigationMenuLink href="#">Installation</NavigationMenuLink>
                    </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>
            <Separator />
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <MailIcon />
                </EmptyMedia>
                <EmptyTitle>No messages</EmptyTitle>
                <EmptyDescription>
                  When you have messages, they will appear here.
                </EmptyDescription>
              </EmptyHeader>
              <EmptyContent>
                <Button size="sm">Compose</Button>
              </EmptyContent>
            </Empty>
            <Marker variant="separator">
              <MarkerContent>Section Title</MarkerContent>
            </Marker>
            <ItemGroup>
              <Item>
                <ItemMedia>
                  <Avatar>
                    <AvatarFallback>AB</AvatarFallback>
                  </Avatar>
                </ItemMedia>
                <ItemContent>
                  <ItemTitle>Alice Brown</ItemTitle>
                  <ItemDescription>Product Designer</ItemDescription>
                </ItemContent>
              </Item>
              <ItemSeparator />
              <Item>
                <ItemMedia>
                  <Avatar>
                    <AvatarFallback>CD</AvatarFallback>
                  </Avatar>
                </ItemMedia>
                <ItemContent>
                  <ItemTitle>Charlie Davis</ItemTitle>
                  <ItemDescription>Engineer</ItemDescription>
                </ItemContent>
              </Item>
            </ItemGroup>
            <div className="flex justify-center">
              <Calendar mode="single" />
            </div>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Name</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead className="text-right">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Alice</TableCell>
                  <TableCell>Designer</TableCell>
                  <TableCell className="text-right">
                    <Badge>Active</Badge>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Bob</TableCell>
                  <TableCell>Engineer</TableCell>
                  <TableCell className="text-right">
                    <Badge variant="secondary">Away</Badge>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </section>

          {/* Feedback */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Feedback</h2>
              <p className={sectionDesc}>
                Alert, AlertDialog, Progress, Skeleton, Spinner, Sonner,
                Tooltip, HoverCard
              </p>
            </div>
            <Alert>
              <AlertTitle>Heads up!</AlertTitle>
              <AlertDescription>
                You can add components to your app using the CLI.
              </AlertDescription>
            </Alert>
            <Alert variant="destructive">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                Your session has expired. Please log in again.
              </AlertDescription>
            </Alert>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline">Open Alert Dialog</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction>Continue</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Loading</span>
                <span>60%</span>
              </div>
              <Progress value={60} />
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
              <Spinner />
              <Spinner className="size-6" />
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <Button onClick={() => toast.success("Success!")}>Toast</Button>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline">Hover me</Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>This is a tooltip</p>
                </TooltipContent>
              </Tooltip>
              <HoverCard>
                <HoverCardTrigger asChild>
                  <Button variant="outline">Hover for card</Button>
                </HoverCardTrigger>
                <HoverCardContent>
                  <p className="text-sm">This is a hover card with extra details.</p>
                </HoverCardContent>
              </HoverCard>
            </div>
          </section>

          {/* Overlays */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Overlays</h2>
              <p className={sectionDesc}>
                Dialog, Sheet, Drawer, Popover
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline">Open Dialog</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Dialog Title</DialogTitle>
                    <DialogDescription>
                      This is a dialog description.
                    </DialogDescription>
                  </DialogHeader>
                  <DialogFooter>
                    <Button>Confirm</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline">Open Sheet</Button>
                </SheetTrigger>
                <SheetContent>
                  <SheetHeader>
                    <SheetTitle>Sheet Title</SheetTitle>
                    <SheetDescription>
                      This is a sheet description.
                    </SheetDescription>
                  </SheetHeader>
                </SheetContent>
              </Sheet>
              <Drawer>
                <DrawerTrigger asChild>
                  <Button variant="outline">Open Drawer</Button>
                </DrawerTrigger>
                <DrawerContent>
                  <DrawerHeader>
                    <DrawerTitle>Drawer Title</DrawerTitle>
                    <DrawerDescription>
                      This is a drawer description.
                    </DrawerDescription>
                  </DrawerHeader>
                  <DrawerFooter>
                    <Button>Submit</Button>
                  </DrawerFooter>
                </DrawerContent>
              </Drawer>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline">Open Popover</Button>
                </PopoverTrigger>
                <PopoverContent className="w-72">
                  <p className="text-sm">
                    This is a popover. Click outside to close.
                  </p>
                </PopoverContent>
              </Popover>
            </div>
          </section>

          {/* Layout */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Layout</h2>
              <p className={sectionDesc}>
                Card, Separator, AspectRatio, ScrollArea, Resizable, Sidebar
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Card Title</CardTitle>
                  <CardDescription>Card description</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Card content goes here.
                  </p>
                </CardContent>
                <CardFooter>
                  <Button size="sm">Action</Button>
                </CardFooter>
              </Card>
              <div className="space-y-2">
                <p className="text-sm">Above</p>
                <Separator />
                <p className="text-sm">Below</p>
              </div>
              <AspectRatio ratio={16 / 9} className="overflow-hidden rounded-lg bg-muted">
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  16:9 Aspect Ratio
                </div>
              </AspectRatio>
              <ScrollArea className="h-24 rounded-md border p-2">
                {Array.from({ length: 20 }).map((_, i) => (
                  <p key={i} className="py-1 text-sm">
                    Scroll item {i + 1}
                  </p>
                ))}
              </ScrollArea>
            </div>
            <ResizablePanelGroup
              orientation="horizontal"
              className="h-32 rounded-lg border"
            >
              <ResizablePanel defaultSize={50}>
                <div className="flex h-full items-center justify-center text-sm">
                  Panel 1
                </div>
              </ResizablePanel>
              <ResizableHandle />
              <ResizablePanel defaultSize={50}>
                <div className="flex h-full items-center justify-center text-sm">
                  Panel 2
                </div>
              </ResizablePanel>
            </ResizablePanelGroup>
            <SidebarProvider className="rounded-lg border">
              <Sidebar>
                <SidebarHeader>
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                    Workspace
                  </div>
                </SidebarHeader>
                <SidebarContent>
                  <SidebarGroup>
                    <SidebarGroupLabel>Menu</SidebarGroupLabel>
                    <SidebarGroupContent>
                      <SidebarMenu>
                        <SidebarMenuItem>
                          <SidebarMenuButton>
                            <HomeIcon />
                            Home
                          </SidebarMenuButton>
                        </SidebarMenuItem>
                        <SidebarMenuItem>
                          <SidebarMenuButton>
                            <SettingsIcon />
                            Settings
                          </SidebarMenuButton>
                        </SidebarMenuItem>
                      </SidebarMenu>
                    </SidebarGroupContent>
                  </SidebarGroup>
                </SidebarContent>
                <SidebarFooter>
                  <div className="px-2 py-1.5">
                    <SidebarTrigger />
                  </div>
                </SidebarFooter>
              </Sidebar>
              <SidebarInset className="p-4">
                <p className="text-sm text-muted-foreground">
                  Sidebar inset content
                </p>
              </SidebarInset>
            </SidebarProvider>
          </section>

          {/* Media & Charts */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Media &amp; Charts</h2>
              <p className={sectionDesc}>Carousel, Chart, Command</p>
            </div>
            <Carousel className="w-full max-w-xs">
              <CarouselContent>
                {Array.from({ length: 5 }).map((_, i) => (
                  <CarouselItem key={i}>
                    <div className="flex h-32 items-center justify-center rounded-lg bg-muted text-sm">
                      Slide {i + 1}
                    </div>
                  </CarouselItem>
                ))}
              </CarouselContent>
              <CarouselPrevious />
              <CarouselNext />
            </Carousel>
            <ChartContainer
              config={chartConfig}
              className="aspect-auto h-56 w-full"
            >
              <LineChart data={chartData} accessibilityLayer>
                <CartesianGrid vertical={false} />
                <XAxis
                  dataKey="month"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                />
                <YAxis tickLine={false} axisLine={false} />
                <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                <Line
                  dataKey="desktop"
                  type="monotone"
                  stroke="var(--color-desktop)"
                  strokeWidth={2}
                />
                <Line
                  dataKey="mobile"
                  type="monotone"
                  stroke="var(--color-mobile)"
                  strokeWidth={2}
                />
              </LineChart>
            </ChartContainer>
            <Command className="rounded-lg border">
              <CommandInput placeholder="Type a command or search..." />
              <CommandList>
                <CommandEmpty>No results found.</CommandEmpty>
                <CommandGroup heading="Suggestions">
                  <CommandItem>Calendar</CommandItem>
                  <CommandItem>Search Emoji</CommandItem>
                  <CommandItem>Calculator</CommandItem>
                </CommandGroup>
              </CommandList>
            </Command>
          </section>

          {/* Chat UI */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Chat UI</h2>
              <p className={sectionDesc}>
                Bubble, Message, MessageScroller, Attachment
              </p>
            </div>
            <BubbleGroup>
              <Bubble>
                <BubbleContent>Hello! How can I help you today?</BubbleContent>
                <BubbleReactions>
                  <Button size="icon-xs" variant="ghost">
                    👍
                  </Button>
                </BubbleReactions>
              </Bubble>
              <Bubble variant="muted" align="end">
                <BubbleContent>
                  I need help with the shadcn components.
                </BubbleContent>
              </Bubble>
            </BubbleGroup>
            <MessageScrollerProvider>
              <MessageScroller className="h-40 rounded-lg border">
                <MessageScrollerViewport>
                  <MessageScrollerContent className="p-3">
                    <MessageScrollerItem>
                      <MessageGroup>
                        <Message>
                          <MessageAvatar>
                            <Avatar>
                              <AvatarFallback>AI</AvatarFallback>
                            </Avatar>
                          </MessageAvatar>
                          <MessageContent>
                            Welcome to the chat!
                          </MessageContent>
                        </Message>
                        <Message align="end">
                          <MessageAvatar>
                            <Avatar>
                              <AvatarFallback>U</AvatarFallback>
                            </Avatar>
                          </MessageAvatar>
                          <MessageContent>
                            Thanks! This looks great.
                          </MessageContent>
                        </Message>
                      </MessageGroup>
                    </MessageScrollerItem>
                  </MessageScrollerContent>
                </MessageScrollerViewport>
              </MessageScroller>
            </MessageScrollerProvider>
            <Attachment>
              <AttachmentMedia variant="icon">
                <MailIcon />
              </AttachmentMedia>
              <AttachmentContent>
                <AttachmentTitle>document.pdf</AttachmentTitle>
                <AttachmentDescription>2.4 MB</AttachmentDescription>
              </AttachmentContent>
            </Attachment>
          </section>

          {/* Other */}
          <section className={section}>
            <div>
              <h2 className={sectionTitle}>Other</h2>
              <p className={sectionDesc}>Questionnaire, Direction</p>
            </div>
            <Questionnaire
              onSubmit={(e) => {
                e.preventDefault()
                toast.success("Questionnaire submitted!")
              }}
            >
              <QuestionnaireProgress>1 of 3</QuestionnaireProgress>
              <QuestionnaireItem name="framework">
                <QuestionnaireTitle>
                  What is your favorite framework?
                </QuestionnaireTitle>
                <QuestionnaireDescription>
                  Select one option below.
                </QuestionnaireDescription>
                <QuestionnaireChoices>
                  <QuestionnaireChoice value="next">
                    Next.js
                  </QuestionnaireChoice>
                  <QuestionnaireChoice value="vite">
                    Vite
                  </QuestionnaireChoice>
                  <QuestionnaireChoice value="astro">
                    Astro
                  </QuestionnaireChoice>
                </QuestionnaireChoices>
                <QuestionnaireActions>
                  <QuestionnaireNext>Next</QuestionnaireNext>
                </QuestionnaireActions>
              </QuestionnaireItem>
            </Questionnaire>
          </section>

          <footer className="pt-4 text-center text-xs text-muted-foreground">
            Built with Next.js 16 + shadcn/ui
          </footer>
        </main>
      </div>
    </DirectionProvider>
  )
}
