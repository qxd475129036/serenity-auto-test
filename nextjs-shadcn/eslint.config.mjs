import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    files: ["**/*.{ts,tsx}"],
    rules: {
      // 本项目统一使用 Base UI，禁止再引入 Radix UI。
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["radix-ui", "@radix-ui/*"],
              message: "项目统一使用 Base UI（@base-ui/react），禁止引入 Radix UI。",
            },
          ],
        },
      ],
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
