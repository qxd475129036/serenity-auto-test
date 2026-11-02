"use client"

import { useState } from "react"
import Link from "next/link"
import { MenuIcon, RabbitIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { SignOutButton } from "@/components/login/sign-out-button"
import { NAV_GROUPS } from "@/components/app/nav-config"

const MENU_GROUPS = NAV_GROUPS

function Brand() {
  return (
    <Link
      href="/"
      className="flex shrink-0 items-center gap-2 rounded-lg px-2 py-1 focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none"
    >
      <RabbitIcon className="size-5" aria-hidden="true" />
      <span className="font-heading text-lg font-semibold tracking-tight">
        rabbit
      </span>
    </Link>
  )
}

/**
 * 登录后业务系统的顶部导航。
 * 桌面显示下拉菜单，窄屏折叠为 Sheet 抽屉。
 */
export function AppHeader() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center gap-3 px-4 sm:px-6 lg:px-8">
        <Brand />

        <nav aria-label="メインメニュー" className="hidden min-w-0 lg:block">
          <NavigationMenu viewport={false} className="max-w-none justify-start">
            <NavigationMenuList className="justify-start gap-1">
              {MENU_GROUPS.map((group) => (
                <NavigationMenuItem key={group.title}>
                  <NavigationMenuTrigger>{group.title}</NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="grid w-72 gap-1 p-2">
                      {group.items.map((item) => (
                        <li key={item.title}>
                          <NavigationMenuLink asChild>
                            <Link href={item.href}>
                              <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                                <item.icon
                                  className="size-4"
                                  aria-hidden="true"
                                />
                              </span>
                              <span className="flex flex-col">
                                <span className="font-medium">{item.title}</span>
                                <span className="text-xs text-muted-foreground">
                                  {item.description}
                                </span>
                              </span>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                      ))}
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                aria-label="メニューを開く"
                className="lg:hidden"
              >
                <MenuIcon />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80 gap-0">
              <SheetHeader className="border-b">
                <SheetTitle>メニュー</SheetTitle>
                <SheetDescription className="sr-only">
                  業務メニューの一覧
                </SheetDescription>
              </SheetHeader>
              <div className="flex-1 overflow-y-auto p-4">
                {NAV_GROUPS.map((group) => (
                  <section key={group.title} className="mb-6 space-y-2">
                    <h2 className="text-xs font-medium text-muted-foreground">
                      {group.title}
                    </h2>
                    <ul className="space-y-1">
                      {group.items.map((item) => (
                        <li key={item.title}>
                          <Link
                            href={item.href}
                            onClick={() => setMenuOpen(false)}
                            className="flex items-center gap-2.5 rounded-lg px-2 py-2 text-sm hover:bg-muted focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none"
                          >
                            <item.icon
                              className="size-4 text-muted-foreground"
                              aria-hidden="true"
                            />
                            {item.title}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </section>
                ))}
              </div>
            </SheetContent>
          </Sheet>

          <SignOutButton />
        </div>
      </div>
    </header>
  )
}
