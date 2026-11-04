"use client"

import {
  ArrowDownIcon,
  ArrowUpIcon,
  ArrowUpDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  InboxIcon,
} from "lucide-react"
import { cn } from "cn"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { ReactTable, RowData } from "@tanstack/react-table"
import type { features } from "@/components/app/use-table"

/** 表格密度：仅控制单元格内边距 */
export type Density = "compact" | "default" | "comfortable"

const DENSITY_MAP: Record<Density, string> = {
  compact: "px-3 py-1",
  default: "px-4 py-2",
  comfortable: "px-5 py-3",
}

/** 表头固定高度 */
const HEAD_HEIGHT = "h-10"

/** 滚动区域随视口高度自适应，预留导航/页面标题/分页的空间 */
const MAX_BODY_HEIGHT =
  "[&_[data-slot=table-container]]:max-h-[calc(100dvh-16rem)]"

/** 各密度下至少保留 10 行的可视高度（含表头） */
const MIN_BODY_HEIGHT: Record<Density, string> = {
  compact: "[&_[data-slot=table-container]]:min-h-[21rem]",
  default: "[&_[data-slot=table-container]]:min-h-[26rem]",
  comfortable: "[&_[data-slot=table-container]]:min-h-[31rem]",
}

/** 列数达到该阈值时自动切换为紧凑内边距 */
const MANY_COLUMNS_THRESHOLD = 8

export type DataTableProps<TData extends RowData> = {
  table: ReactTable<typeof features, TData>
  /** 可选每页行数选项，默认 [10, 20, 50] */
  pageSizeOptions?: number[]
  /** 表格密度；未指定时按列数自动选择（≥8 列用 compact） */
  density?: Density
  /** 是否启用斑马纹（隔行变色），默认 false */
  striped?: boolean
  className?: string
}

const DEFAULT_PAGE_SIZE_OPTIONS = [10, 20, 50]

/**
 * 基于 TanStack Table v9 + shadcn 的通用数据表格组件。
 * 支持：列排序、分页、密度切换、斑马纹。
 */
export function DataTable<TData extends RowData>({
  table,
  pageSizeOptions = DEFAULT_PAGE_SIZE_OPTIONS,
  density,
  striped = false,
  className,
}: DataTableProps<TData>) {
  const { pagination } = table.state
  const leafHeaders = table.getLeafHeaders()
  const resolvedDensity: Density =
    density ??
    (leafHeaders.length >= MANY_COLUMNS_THRESHOLD ? "compact" : "default")
  const cellPadding = DENSITY_MAP[resolvedDensity]

  const rowCount = table.getRowCount()
  const pageCount = table.getPageCount()
  const rangeStart =
    rowCount === 0 ? 0 : pagination.pageIndex * pagination.pageSize + 1
  const rangeEnd = Math.min(
    (pagination.pageIndex + 1) * pagination.pageSize,
    rowCount,
  )

  return (
    <div
      className={cn(
        "overflow-hidden rounded-xl border border-border/70 bg-card shadow-sm",
        "[&_[data-slot=table-container]]:overflow-y-auto",
        MAX_BODY_HEIGHT,
        MIN_BODY_HEIGHT[resolvedDensity],
        className,
      )}
    >
      <Table>
        {/* 单行 header：只用叶子列的表头，不做多行 column group 展开 */}
        <TableHeader className="bg-muted/40">
          <TableRow className="border-border/60 hover:bg-transparent">
            {leafHeaders.map((header) => {
              const isSorted = header.column.getIsSorted() !== false
              const canSort = header.column.getCanSort()

              return (
                <TableHead
                  key={header.id}
                  aria-sort={
                    isSorted
                      ? header.column.getIsSorted() === "asc"
                        ? "ascending"
                        : "descending"
                      : undefined
                  }
                  className={cn(
                    HEAD_HEIGHT,
                    cellPadding,
                    "sticky top-0 z-10 bg-muted/95 backdrop-blur-sm text-sm font-semibold text-muted-foreground transition-colors",
                    isSorted && "text-foreground",
                    canSort &&
                      "cursor-pointer select-none hover:text-foreground",
                  )}
                  onClick={
                    canSort
                      ? header.column.getToggleSortingHandler()
                      : undefined
                  }
                >
                  <SortableHeader header={header} />
                </TableHead>
              )
            })}
          </TableRow>
        </TableHeader>

        <TableBody>
          {table.getRowModel().rows.length === 0 ? (
            <TableRow className="border-0 hover:bg-transparent">
              <TableCell colSpan={table.getAllColumns().length}>
                <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
                  <span className="flex size-12 items-center justify-center rounded-full bg-muted">
                    <InboxIcon
                      className="size-5 text-muted-foreground"
                      aria-hidden="true"
                    />
                  </span>
                  <div className="space-y-1">
                    <p className="text-sm font-medium">データがありません</p>
                    <p className="text-xs text-muted-foreground">
                      条件を変更するか、新しいデータを登録してください。
                    </p>
                  </div>
                </div>
              </TableCell>
            </TableRow>
          ) : (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                className={cn(
                  "border-border/50 transition-colors",
                  striped && "even:bg-muted/25",
                )}
              >
                {row.getAllCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    className={cn("text-sm text-foreground/90", cellPadding)}
                  >
                    {cell.renderValue() as React.ReactNode}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {/* 分页控制条：内嵌卡片底部，与表格融为一体 */}
      <div className="flex flex-col gap-3 border-t border-border/60 bg-muted/20 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="tabular-nums">
            {rangeStart}–{rangeEnd} / {rowCount} 件
          </span>
          <Select
            value={String(pagination.pageSize)}
            onValueChange={(v) => table.setPageSize(Number(v))}
          >
            <SelectTrigger size="sm" className="w-auto gap-1">
              <SelectValue />
              <span className="text-muted-foreground">件/ページ</span>
            </SelectTrigger>
            <SelectContent alignItemWithTrigger={false}>
              {pageSizeOptions.map((size) => (
                <SelectItem key={size} value={String(size)}>
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="前のページ"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeftIcon />
          </Button>

          {pageItems(pagination.pageIndex, pageCount).map((item, index) =>
            item === "ellipsis" ? (
              <span
                key={`ellipsis-${index}`}
                className="px-1 text-xs text-muted-foreground"
              >
                …
              </span>
            ) : (
              <Button
                key={item}
                variant={item === pagination.pageIndex ? "default" : "ghost"}
                size="icon-sm"
                className="tabular-nums"
                aria-label={`${item + 1} ページ目`}
                aria-current={
                  item === pagination.pageIndex ? "page" : undefined
                }
                onClick={() => table.setPageIndex(item)}
              >
                {item + 1}
              </Button>
            ),
          )}

          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="次のページ"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRightIcon />
          </Button>
        </div>
      </div>
    </div>
  )
}

/** 生成页码序列：总数 ≤ 7 时全部显示，否则用省略号窗口收纳 */
function pageItems(
  current: number,
  total: number,
): Array<number | "ellipsis"> {
  if (total <= 0) return []
  if (total <= 7) return Array.from({ length: total }, (_, i) => i)

  const items: Array<number | "ellipsis"> = [0]
  const start = Math.max(1, current - 1)
  const end = Math.min(total - 2, current + 1)

  if (start > 1) items.push("ellipsis")
  for (let i = start; i <= end; i += 1) items.push(i)
  if (end < total - 2) items.push("ellipsis")
  items.push(total - 1)
  return items
}

/** 可排序列的 header 渲染：显示文字 + 排序状态图标 */
function SortableHeader<TData extends RowData>({
  header,
}: {
  header: ReturnType<
    ReactTable<typeof features, TData>["getHeaderGroups"]
  >[number]["headers"][number]
}) {
  const sorted = header.column.getIsSorted()

  const icon =
    sorted === "asc" ? (
      <ArrowUpIcon className="ml-1 size-3" />
    ) : sorted === "desc" ? (
      <ArrowDownIcon className="ml-1 size-3" />
    ) : header.column.getCanSort() ? (
      <ArrowUpDownIcon className="ml-1 size-3 opacity-40" />
    ) : null

  return (
    <span className="inline-flex items-center">
      {header.column.columnDef.header as React.ReactNode}
      {icon}
    </span>
  )
}
