import Link from "next/link"
import { ArrowLeftIcon, ConstructionIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"

type PlaceholderPageProps = {
  title: string
  description: string
}

/**
 * 各业务模块的统一占位页内容。
 */
export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-6 space-y-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          {title}
        </h1>
        <p className="text-sm text-muted-foreground">{description}</p>
      </header>
      <Card>
        <CardContent>
          <Empty className="border border-dashed">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <ConstructionIcon aria-hidden="true" />
              </EmptyMedia>
              <EmptyTitle>準備中</EmptyTitle>
              <EmptyDescription>
                この機能は現在準備中です。今後のリリースで提供予定です。
              </EmptyDescription>
            </EmptyHeader>
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeftIcon />
                ダッシュボードに戻る
              </Button>
            </Link>
          </Empty>
        </CardContent>
      </Card>
    </div>
  )
}
