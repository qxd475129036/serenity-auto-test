"use client"

import type { ColumnDef, RowData } from "@tanstack/react-table"
import { Checkbox } from "@/components/ui/checkbox"
import { features } from "@/components/app/use-table"

export const SELECTION_COLUMN_ID = "__selection"

/**
 * 生成行选择列：表头复选框负责全选 / 解除全选，行内复选框切换单行选中。
 * 放在 columns 数组第一位；需要同时开启 enableRowSelection 与稳定 getRowId。
 */
export function createSelectionColumn<
  TData extends RowData,
>(): ColumnDef<typeof features, TData, unknown> {
  return {
    id: SELECTION_COLUMN_ID,
    enableSorting: false,
    header: ({ table }) => {
      const hasSelection = table.getIsSomeRowsSelected()

      return (
        <Checkbox
          aria-label={hasSelection ? "選択を解除" : "全行を選択"}
          checked={table.getIsAllRowsSelected()}
          indeterminate={hasSelection && !table.getIsAllRowsSelected()}
          onCheckedChange={() => {
            if (hasSelection) {
              table.resetRowSelection()
            } else {
              table.toggleAllRowsSelected(true)
            }
          }}
        />
      )
    },
    cell: ({ row }) => (
      <Checkbox
        aria-label="この行を選択"
        checked={row.getIsSelected()}
        disabled={!row.getCanSelect()}
        onCheckedChange={(checked) => row.toggleSelected(checked)}
      />
    ),
  }
}
