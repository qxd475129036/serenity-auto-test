"use client"

import {
  ArrowDownIcon,
  ArrowUpIcon,
  ArrowUpDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
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
import {
  Pagination,
  PaginationContent,
  PaginationItem,
} from "@/components/ui/pagination"
import type { ReactTable, RowData } from "@tanstack/react-table"
import type { features } from "@/components/app/use-table"

export type DataTableProps<TData extends RowData> = {
  table: ReactTable<typeof features, TData>
  /** 可选每页行数选项，默认 [10, 20, 50] */
  pageSizeOptions?: number[]
  className?: string
}

const DEFAULT_PAGE_SIZE_OPTIONS = [10, 20, 50]

/**
 * 基于 TanStack Table v9 + shadcn 的通用数据表格组件。
 * 支持：列排序、分页、多行 header（通过 column group 嵌套自动实现）。
 */
export function DataTable<TData extends RowData>({
  table,
  pageSizeOptions = DEFAULT_PAGE_SIZE_OPTIONS,
  className,
}: DataTableProps<TData>) {
  const { pagination } = table.state

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <div className="rounded-md border">
        <Table>
          {/* 多行 header：TanStack 的 getHeaderGroups 会把嵌套 column groups 展开成多行 */}
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    colSpan={header.colSpan}
                    className={cn(
                      header.column.getCanSort() && "cursor-pointer select-none",
                    )}
                    onClick={
                      header.column.getCanSort()
                        ? header.column.getToggleSortingHandler()
                        : undefined
                    }
                  >
                    {header.isPlaceholder ? null : (
                      <SortableHeader header={header} />
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>

          <TableBody>
            {table.getRowModel().rows.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={table.getAllColumns().length}
                  className="h-24 text-center text-muted-foreground"
                >
                  データがありません
                </TableCell>
              </TableRow>
            ) : (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getAllCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {cell.renderValue() as React.ReactNode}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* 分页控制条 */}
      <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>
            {pagination.pageIndex * pagination.pageSize + 1}
            –
            {Math.min(
              (pagination.pageIndex + 1) * pagination.pageSize,
              table.getRowCount(),
            )}{" "}
            / {table.getRowCount()} 件
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

        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                <ChevronLeftIcon />
                前へ
              </Button>
            </PaginationItem>
            <PaginationItem>
              <span className="text-sm tabular-nums">
                {pagination.pageIndex + 1} / {table.getPageCount()}
              </span>
            </PaginationItem>
            <PaginationItem>
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                次へ
                <ChevronRightIcon />
              </Button>
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      </div>
    </div>
  )
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

  const icon = sorted === "asc" ? (
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
