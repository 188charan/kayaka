import { describe, expect, it } from "vitest";

import { ApiError, toApiError, unwrap } from "@/lib/api/errors";

const envelope = {
  error: {
    code: "VALIDATION_ERROR",
    message: "Some fields need attention.",
    details: [{ field: "email", code: "invalid", message: "Enter a valid email address." }],
    requestId: "req_abc12345",
  },
};

describe("toApiError", () => {
  it("reads the backend error envelope", () => {
    const error = toApiError(400, envelope);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(400);
    expect(error.code).toBe("VALIDATION_ERROR");
    expect(error.requestId).toBe("req_abc12345");
    expect(error.details).toHaveLength(1);
  });

  it("tolerates bodies that are not an envelope", () => {
    expect(toApiError(502, "<html>Bad gateway</html>", "req_x").code).toBe("INTERNAL_ERROR");
    expect(toApiError(418, null).code).toBe("UNEXPECTED_RESPONSE");
  });
});

describe("unwrap", () => {
  it("returns data on success", async () => {
    const response = new Response("{}", { status: 200 });
    await expect(unwrap(Promise.resolve({ data: { ok: true }, response }))).resolves.toEqual({
      ok: true,
    });
  });

  it("throws ApiError on error responses", async () => {
    const response = new Response("{}", { status: 400 });
    await expect(unwrap(Promise.resolve({ error: envelope, response }))).rejects.toMatchObject({
      code: "VALIDATION_ERROR",
      status: 400,
    });
  });

  it("maps network failures to NETWORK_ERROR", async () => {
    await expect(unwrap(Promise.reject(new TypeError("fetch failed")))).rejects.toMatchObject({
      code: "NETWORK_ERROR",
      status: 0,
    });
  });
});
