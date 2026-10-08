import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

// The three surfaces share src/components and src/lib, but never import each other (ADR 0001).
const surfaceBoundary = (others) => ({
  "no-restricted-imports": [
    "error",
    {
      patterns: others.map((surface) => ({
        group: [`@/app/(${surface})/**`, `@/features/${surface}/**`],
        message: `Do not import ${surface} code here. Move shared code to src/components or src/lib.`,
      })),
    },
  ],
});

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores([
    ".next/**",
    "out/**",
    "next-env.d.ts",
    "src/lib/api/schema.d.ts",
    "playwright-report/**",
    "test-results/**",
  ]),
  { files: ["src/app/(storefront)/**"], rules: surfaceBoundary(["dashboard", "admin"]) },
  { files: ["src/app/(dashboard)/**"], rules: surfaceBoundary(["storefront", "admin"]) },
  { files: ["src/app/(admin)/**"], rules: surfaceBoundary(["storefront", "dashboard"]) },
]);
