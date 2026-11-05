"use client"

import {
  createPaginatedRowModel,
  createSortedRowModel,
  createTableHook,
  rowPaginationFeature,
  rowSelectionFeature,
  rowSortingFeature,
  sortFns,
  tableFeatures,
} from "@tanstack/react-table"
import type { PaginationState } from "@tanstack/react-table"

/**
 * 共享 features 定义 —— 排序 + 分页 + 行选择。
 *
 * 导出 features 实例供子模块的 ColumnDef 显式类型参数使用。
 */
export const features = tableFeatures({
  rowSortingFeature,
  rowPaginationFeature,
  rowSelectionFeature,
  sortedRowModel: createSortedRowModel(),
  paginatedRowModel: createPaginatedRowModel(),
  sortFns,
})

/** 分页配置：由页面级传入，表格组件只消费不写死 */
export type TablePaginationConfig = {
  /** false = 不分页（单页展示全部数据） */
  enabled?: boolean
  /** 初始每页行数，默认 10 */
  pageSize?: number
  /** 每页行数选项，默认 [10, 20, 50] */
  pageSizeOptions?: number[]
}

export const DEFAULT_PAGE_SIZE = 10
export const DEFAULT_PAGE_SIZE_OPTIONS = [10, 20, 50]

/**
 * 把页面级分页配置转换成 useAppTable 的 initialState.pagination。
 * 关闭分页时使用 MAX_SAFE_INTEGER，保证所有行落在同一页。
 */
export function getPaginationInitialState(
  config?: TablePaginationConfig,
): PaginationState {
  return {
    pageIndex: 0,
    pageSize:
      config?.enabled === false
        ? Number.MAX_SAFE_INTEGER
        : (config?.pageSize ?? DEFAULT_PAGE_SIZE),
  }
}

/**
 * createTableHook 工厂 —— 预绑定 features 与默认选项，
 * 整个应用的 table 都复用这份配置。
 *
 * createTableHook options 只接受 app-level 共享选项；
 * 表格级选项（如 initialState）在 useAppTable 调用时传入。
 *
 * @example
 * // 子模块里：
 * import { useAppTable, features } from "@/components/app/use-table"
 * import type { ColumnDef } from "@tanstack/react-table"
 *
 * const columns: ColumnDef<typeof features, Shop, unknown>[] = [...]
 * const table = useAppTable({ key: "shops", columns, data })
 */
export const { useAppTable } = createTableHook({
  features,
})
