import { describe, expect, it } from "vitest";

import { parseServerEnv } from "@/lib/env-schema";

const valid = {
  API_ORIGIN: "http://localhost:8000/",
  PROXY_SHARED_SECRET: "x".repeat(32),
  APP_ENV: "development",
};

describe("parseServerEnv", () => {
  it("accepts a valid environment and strips trailing slashes from API_ORIGIN", () => {
    expect(parseServerEnv(valid)).toEqual({
      API_ORIGIN: "http://localhost:8000",
      PROXY_SHARED_SECRET: "x".repeat(32),
      APP_ENV: "development",
    });
  });

  it("defaults APP_ENV to development", () => {
    const { APP_ENV, ...rest } = valid;
    void APP_ENV;
    expect(parseServerEnv(rest).APP_ENV).toBe("development");
  });

  it("lists every problem in one readable error", () => {
    expect(() => parseServerEnv({})).toThrowError(/API_ORIGIN[\s\S]*PROXY_SHARED_SECRET/);
  });

  it("rejects short proxy secrets", () => {
    expect(() => parseServerEnv({ ...valid, PROXY_SHARED_SECRET: "short" })).toThrowError(
      /at least 32 characters/,
    );
  });

  it("rejects non-http API origins", () => {
    expect(() => parseServerEnv({ ...valid, API_ORIGIN: "ftp://example.com" })).toThrowError(
      /API_ORIGIN/,
    );
  });
});
