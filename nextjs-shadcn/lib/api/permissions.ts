/**
 * API 中转层的权限码与「后端接口 → 所需权限」映射。
 *
 * - 权限码由登录会话携带（`session.user.permissions`，登录时从后端用户信息接口拉取）。
 * - 需要在 Next 侧做权限校验的后端接口，在此登记；未登记的接口仅要求登录。
 * - 后端自身仍会鉴权（Spring Security 403 兜底）。
 */

export const PERMISSIONS = {
  DATA_READ: "data:read",
} as const

/** 已知权限码 + 允许后端返回任意字符串码 */
export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS] | (string & {})

/** 后端接口路径 → 所需权限码（catch-all 代理使用） */
export const UPSTREAM_PERMISSIONS: Record<string, Permission> = {
  "/api/getData": PERMISSIONS.DATA_READ,
}

/**
 * 会话权限码是否满足要求。
 *
 * - `required` 为空表示仅需登录。
 * - 会话权限含 `"*"` 时视为拥有全部权限。
 */
export function hasPermission(
  granted: readonly string[],
  required?: Permission,
): boolean {
  if (!required) {
    return true
  }
  return granted.includes("*") || granted.includes(required)
}
