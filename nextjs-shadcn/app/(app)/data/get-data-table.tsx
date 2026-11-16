"use client"

import { useMemo, useState } from "react"
import type { ColumnDef } from "@tanstack/react-table"
import {
  AlertCircleIcon,
  InboxIcon,
  RotateCwIcon,
  SearchIcon,
} from "lucide-react"
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { Skeleton } from "@/components/ui/skeleton"
import { Spinner } from "@/components/ui/spinner"
import { DataTable } from "@/components/app/data-table"
import {
  features,
  getPaginationInitialState,
  useAppTable,
} from "@/components/app/use-table"

/** 请求参数：固定 lobCd = 10 */
const REQUEST_BODY = { lobCd: 10 }

/** 数据行：结构未知，统一按键值对象处理 */
type DataRow = Record<string, unknown>

type LoadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "success"; rows: DataRow[] }

/** 常见的数据集合包装键，按顺序查找 */
const COLLECTION_KEYS = [
  "data",
  "list",
  "items",
  "records",
  "rows",
  "result",
  "content",
] as const

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

function toRow(value: unknown): DataRow {
  return isPlainObject(value) ? value : { value }
}

/**
 * 防御性解析返回数据：
 * 兼容顶层数组、`{ data: [...] }` 以及 list / items / records / rows / result / content
 * 等常见包装（最多向下查找 3 层）。无法识别时返回 null。
 */
function extractRows(payload: unknown, depth = 0): DataRow[] | null {
  if (Array.isArray(payload)) {
    return payload.map(toRow)
  }
  if (!isPlainObject(payload) || depth > 3) {
    return null
  }

  for (const key of COLLECTION_KEYS) {
    const candidate = payload[key]
    if (Array.isArray(candidate)) {
      return candidate.map(toRow)
    }
  }

  for (const key of COLLECTION_KEYS) {
    if (key in payload) {
      const found = extractRows(payload[key], depth + 1)
      if (found !== null) {
        return found
      }
    }
  }

  return null
}

/** 从统一错误包 `{ error: { message } }` 中取出可读信息 */
function readErrorMessage(payload: unknown, fallback: string): string {
  if (isPlainObject(payload)) {
    const error = payload.error
    if (isPlainObject(error) && typeof error.message === "string") {
      return error.message
    }
  }
  return fallback
}

/** 单元格展示：空值占位，对象类型转 JSON 字符串 */
function formatCellValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "—"
  }
  if (typeof value === "object") {
    return JSON.stringify(value)
  }
  return String(value)
}

/** 列键取所有行的并集，保持首次出现顺序 */
function getColumnKeys(rows: DataRow[]): string[] {
  const keys: string[] = []
  const seen = new Set<string>()

  for (const row of rows) {
    for (const key of Object.keys(row)) {
      if (!seen.has(key)) {
        seen.add(key)
        keys.push(key)
      }
    }
  }

  return keys
}

export function GetDataTable() {
  const [state, setState] = useState<LoadState>({ status: "idle" })
  const isLoading = state.status === "loading"

  async function fetchData() {
    if (isLoading) {
      return
    }

    setState({ status: "loading" })

    try {
      const response = await fetch("/api/get-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(REQUEST_BODY),
      })
      const payload: unknown = await response.json().catch(() => null)

      if (!response.ok) {
        setState({
          status: "error",
          message: readErrorMessage(
            payload,
            `データの取得に失敗しました（HTTP ${response.status}）。`,
          ),
        })
        return
      }

      const rows = extractRows(payload)
      if (rows === null) {
        setState({
          status: "error",
          message: "レスポンスのデータ形式を判別できませんでした。",
        })
        return
      }

      setState({ status: "success", rows })
    } catch {
      setState({
        status: "error",
        message: "データ取得サーバーに接続できませんでした。",
      })
    }
  }

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Button onClick={fetchData} disabled={isLoading}>
          {isLoading ? <Spinner /> : <SearchIcon />}
          {isLoading ? "検索中…" : "検索"}
        </Button>
      </div>

      {state.status === "idle" && <IdleState />}
      {state.status === "loading" && <LoadingState />}
      {state.status === "error" && (
        <ErrorState message={state.message} onRetry={fetchData} />
      )}
      {state.status === "success" &&
        (state.rows.length === 0 ? (
          <EmptyState />
        ) : (
          <DynamicDataTable rows={state.rows} />
        ))}
    </>
  )
}

function DynamicDataTable({ rows }: { rows: DataRow[] }) {
  // 列由数据键动态生成；数据不变时列定义保持稳定
  const columns = useMemo<ColumnDef<typeof features, DataRow, unknown>[]>(
    () =>
      getColumnKeys(rows).map((key) => ({
        id: key,
        accessorFn: (row) => row[key],
        header: key,
        // 结构未知，无法保证排序语义，统一关闭排序
        enableSorting: false,
        cell: ({ getValue }) => (
          <span className="whitespace-nowrap">
            {formatCellValue(getValue())}
          </span>
        ),
      })),
    [rows],
  )

  const table = useAppTable({
    key: "get-data",
    columns,
    data: rows,
    initialState: { pagination: getPaginationInitialState() },
  })

  return <DataTable table={table} />
}

function IdleState() {
  return (
    <Empty className="rounded-xl border border-dashed border-border/70 bg-card">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <SearchIcon aria-hidden="true" />
        </EmptyMedia>
        <EmptyTitle>データ未取得</EmptyTitle>
        <EmptyDescription>
          「検索」ボタンを押すと、lobCd = 10 のデータを取得します。
        </EmptyDescription>
      </EmptyHeader>
    </Empty>
  )
}

function LoadingState() {
  return (
    <div
      role="status"
      aria-label="読み込み中"
      className="space-y-3 rounded-xl border border-border/70 bg-card p-4 shadow-sm"
    >
      <Skeleton className="h-10 w-full" />
      {Array.from({ length: 8 }, (_, index) => (
        <Skeleton key={index} className="h-12 w-full" />
      ))}
      <span className="sr-only">読み込み中…</span>
    </div>
  )
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry: () => void
}) {
  return (
    <Alert variant="destructive">
      <AlertCircleIcon />
      <AlertTitle>データの取得に失敗しました</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
      <AlertAction>
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RotateCwIcon />
          再試行
        </Button>
      </AlertAction>
    </Alert>
  )
}

function EmptyState() {
  return (
    <Empty className="rounded-xl border border-dashed border-border/70 bg-card">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <InboxIcon aria-hidden="true" />
        </EmptyMedia>
        <EmptyTitle>データがありません</EmptyTitle>
        <EmptyDescription>
          lobCd = 10 のデータは 0 件でした。
        </EmptyDescription>
      </EmptyHeader>
    </Empty>
  )
}
