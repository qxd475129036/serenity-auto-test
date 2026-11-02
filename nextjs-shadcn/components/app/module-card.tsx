import Link from "next/link"
import { ChevronRightIcon } from "lucide-react"
import {
  Card,
  CardAction,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { NavItem } from "@/components/app/nav-config"

type ModuleCardProps = {
  item: NavItem
}

/**
 * 工作台功能卡片：整卡可点击，进入对应模块页面。
 */
export function ModuleCard({ item }: ModuleCardProps) {
  const Icon = item.icon

  return (
    <Link href={item.href} className="group block rounded-xl">
      <Card
        size="sm"
        className="h-full transition group-hover:ring-foreground/25"
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2.5">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-muted">
              <Icon className="size-4" aria-hidden="true" />
            </span>
            <span>{item.title}</span>
          </CardTitle>
          <CardAction className="self-center">
            <ChevronRightIcon
              className="size-4 text-muted-foreground transition group-hover:translate-x-0.5 group-hover:text-foreground"
              aria-hidden="true"
            />
          </CardAction>
          <CardDescription>{item.description}</CardDescription>
        </CardHeader>
      </Card>
    </Link>
  )
}
