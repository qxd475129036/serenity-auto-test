"use client"

import {
  createPaginatedRowModel,
  createSortedRowModel,
  createTableHook,
  rowPaginationFeature,
  rowSortingFeature,
  sortFns,
  tableFeatures,
} from "@tanstack/react-table"

/**
 * 共享 features 定义 —— 只注册排序 + 分页，按需打包。
 * 将来要加 filtering / column visibility 等，在 tableFeatures 里追加即可。
 *
 * 导出 features 实例供子模块的 ColumnDef 显式类型参数使用。
 */
export const features = tableFeatures({
  rowSortingFeature,
  rowPaginationFeature,
  sortedRowModel: createSortedRowModel(),
  paginatedRowModel: createPaginatedRowModel(),
  sortFns,
})

/**
 * createTableHook 工厂 —— 预绑定 features 与默认选项，
 * 整个应用的 table 都复用这份配置。
 *
 * createTableHook options 只接受 app-level 共享选项；
 * 表格级选项（如 defaultPageSize）在 useAppTable 调用时传入。
 *
 * @example
 * // 子模块里：
 * import { useAppTable, features } from "@/components/app/use-table"
 * import type { ColumnDef } from "@tanstack/react-table"
 *
 * const columns: ColumnDef<typeof features, Shop, unknown>[] = [...]
 * const table = useAppTable({ key: "shops", columns, data, defaultPageSize: 10 })
 */
export const { useAppTable } = createTableHook({
  features,
})
