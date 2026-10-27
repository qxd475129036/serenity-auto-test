# 验证要求

## 验证命令

| 命令 | 作用 |
|---|---|
| `npm run typecheck` | TypeScript 类型检查（`tsc --noEmit`） |
| `npm run lint` | ESLint（next core-web-vitals + typescript） |
| `npm run build` | 生产构建（含全部静态页面编译） |
| `npm run dev` | 本地开发（浏览器人工验证） |

当前未引入测试框架（无 vitest/jest）。引入前，**验证三件套 = typecheck + lint + build**；引入后在此补充测试命令并升级三件套为四件套。

## 提交前检查清单

- [ ] `npm run typecheck && npm run lint && npm run build` 全部通过
- [ ] 改动未超出任务范围（对照 SPEC 目标/非目标）
- [ ] 页面级改动已在浏览器人工验证（亮色/暗色 + 移动端视口）
- [ ] 规则若有变化，同步更新对应 SPEC / PAGE / docs 文档

## 证据格式

任务完成汇报时必须给出:

1. 验证三件套的输出（可只贴关键行: 通过/失败 + 错误摘要）。
2. UI 变更: 截图（亮色/暗色，涉及响应式时加移动端）。
3. 改动文件清单（一行一个路径，标注新增/修改）。
