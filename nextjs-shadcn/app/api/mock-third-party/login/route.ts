import { NextResponse } from "next/server"

/**
 * Mock 第三方认证 API。
 *
 * 真实接入时替换 THIRD_PARTY_API_URL 即可，lib/auth.ts 无需改动。
 *
 * POST /api/mock-third-party/login
 * 入参: { username: string, password: string }
 * 规则: password === "password" 视为成功，其它均为 401。
 * 成功响应: { data: { token, user: { username, name } } }
 * 失败响应: { error: { code, message } }
 */
export async function POST(request: Request) {
  let body: unknown
  try {
    body = await request.json()
  } catch {
    return NextResponse.json(
      { error: { code: "E_VALIDATION", message: "Invalid JSON body" } },
      { status: 400 },
    )
  }

  const username =
    typeof body === "object" && body !== null && "username" in body
      ? String((body as { username: unknown }).username)
      : ""
  const password =
    typeof body === "object" && body !== null && "password" in body
      ? String((body as { password: unknown }).password)
      : ""

  if (!username || !password) {
    return NextResponse.json(
      { error: { code: "E_VALIDATION", message: "username and password are required" } },
      { status: 400 },
    )
  }

  if (password !== "password") {
    return NextResponse.json(
      { error: { code: "E_UNAUTHORIZED", message: "Invalid username or password" } },
      { status: 401 },
    )
  }

  return NextResponse.json({
    data: {
      token: `mock-token-${username}`,
      user: {
        username,
        name: username,
      },
    },
  })
}
