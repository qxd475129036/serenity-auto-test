# 登录

- 路由: `/login`
- 状态: 骨架（表单 UI，无后端）
- 版本: 0.1

## 目标

- 提供登录页 `/login` 的标准 UI 骨架：邮箱 + 密码 + 记住我 + 忘记密码入口。
- 作为后续接入真实认证（API/session）时的落点。

## 非目标

- 不接后端、不做 session/cookie 管理、不做注册/找回流程。
- 不是组件演示：`/demo` 才是组件手册。

## 用户与场景

- 用户打开 `/login` → 输入邮箱密码 → 提交 → 收到 toast 反馈（骨架阶段仅本地校验）。

## 页面与路由

| 路由 | 说明 |
|---|---|
| `/login` | 登录页，细则见 [app/login/PAGE.md](../../app/login/PAGE.md) |

## 功能需求

### 正常流程

- 邮箱、密码输入（带前缀图标，Label 关联，autoComplete 语义正确）。
- 记住我 Checkbox（本地 state）。
- 信息填写完整后提交，显示成功 toast（demo 文案）。
- 忘记密码: 占位按钮（type="button"），后续接流程。
- 返回按钮回首页 `/`。

### 异常与边界

- 邮箱或密码为空时提交，显示错误 toast。
- 无后端、无 loading 态、无路由跳转（骨架阶段）。

## 验收标准

- `/login` 200 渲染，无 console 错误；默认亮色显示正常。
- 空表单提交出 error toast；填写后提交出 success toast。
- 验证三件套通过（docs/verification.md）。

## 数据与接口

- 无接口；后续接入时在 docs/api.md 登记。

## 风险与依赖

- 认证方案确定前，页面只提供本地表单交互，不承担真实登录能力。

## 决策记录

- 2026-10: 原 `/demo1` 变体页改为登录页 `/login`，变体页不再保留。

## 开放问题

1. 认证方案未定（NextAuth？自研 API？），接入后补充本 SPEC 与 app/login/PAGE.md。
