import type { components } from "@/lib/api/schema";

type ErrorResponse = components["schemas"]["ErrorResponse"];
type ErrorDetail = components["schemas"]["ErrorDetail"];

/** Every failed API call surfaces as an ApiError with the backend's stable error code. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId: string | null;
  readonly details: ErrorDetail[];

  constructor(init: {
    status: number;
    code: string;
    message: string;
    requestId?: string | null;
    details?: ErrorDetail[];
  }) {
    super(init.message);
    this.name = "ApiError";
    this.status = init.status;
    this.code = init.code;
    this.requestId = init.requestId ?? null;
    this.details = init.details ?? [];
  }
}

function isErrorResponse(body: unknown): body is ErrorResponse {
  if (typeof body !== "object" || body === null || !("error" in body)) return false;
  const error = (body as { error: unknown }).error;
  return (
    typeof error === "object" &&
    error !== null &&
    typeof (error as { code?: unknown }).code === "string" &&
    typeof (error as { message?: unknown }).message === "string"
  );
}

/** Convert a non-2xx response body into an ApiError, tolerating non-envelope bodies. */
export function toApiError(status: number, body: unknown, requestId?: string | null): ApiError {
  if (isErrorResponse(body)) {
    return new ApiError({
      status,
      code: body.error.code,
      message: body.error.message,
      requestId: body.error.requestId ?? requestId ?? null,
      details: body.error.details,
    });
  }
  return new ApiError({
    status,
    code: status >= 500 ? "INTERNAL_ERROR" : "UNEXPECTED_RESPONSE",
    message: "Unexpected response from the server.",
    requestId,
  });
}

type FetchResult<T> = { data?: T; error?: unknown; response: Response };

/**
 * Await an openapi-fetch call and return its data, or throw ApiError.
 * Network failures become ApiError with status 0 and code NETWORK_ERROR.
 */
export async function unwrap<T>(call: Promise<FetchResult<T>>): Promise<T> {
  let result: FetchResult<T>;
  try {
    result = await call;
  } catch {
    throw new ApiError({
      status: 0,
      code: "NETWORK_ERROR",
      message: "Could not reach the server. Check your connection and try again.",
    });
  }
  const { data, error, response } = result;
  if (!response.ok || data === undefined) {
    throw toApiError(response.status, error, response.headers.get("x-request-id"));
  }
  return data;
}
