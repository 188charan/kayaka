import { z } from "zod";

/**
 * Server-side environment contract. Kept separate from `env.ts` so it can be unit tested
 * without the `server-only` guard.
 */
export const serverEnvSchema = z.object({
  /** Origin of the Django API, e.g. http://localhost:8000 or https://api.example.com */
  API_ORIGIN: z.url({ protocol: /^https?$/ }).transform((value) => value.replace(/\/+$/, "")),
  /** Shared with Django; proves requests came through our proxy (ADR 0003). */
  PROXY_SHARED_SECRET: z.string().min(32, "must be at least 32 characters"),
  APP_ENV: z.enum(["development", "test", "staging", "production"]).default("development"),
});

export type ServerEnv = z.infer<typeof serverEnvSchema>;

export function parseServerEnv(source: Record<string, string | undefined>): ServerEnv {
  const result = serverEnvSchema.safeParse(source);
  if (!result.success) {
    const problems = result.error.issues
      .map((issue) => `  - ${issue.path.join(".")}: ${issue.message}`)
      .join("\n");
    throw new Error(
      `Invalid environment configuration:\n${problems}\n` +
        "Copy frontend/.env.example to frontend/.env.local and fill in the values.",
    );
  }
  return result.data;
}
