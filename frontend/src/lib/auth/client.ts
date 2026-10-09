"use client";

/**
 * Browser-side authentication actions. Everything goes through the same-origin proxy:
 *   - login/logout call django-allauth headless at /_allauth/browser/v1/* (session cookies)
 *   - identity/tenant calls hit /api/v1/*
 *
 * No tokens are ever stored in JavaScript. The session cookie is HttpOnly; only the CSRF cookie
 * is readable (by design) so we can echo it in the X-CSRFToken header on unsafe requests.
 */

import type { Me } from "./types";

const CSRF_COOKIE = "kayaka_csrftoken";
const ALLAUTH = "/_allauth/browser/v1";

export class AuthError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "AuthError";
  }
}

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]!) : null;
}

async function csrfToken(): Promise<string> {
  let token = readCookie(CSRF_COOKIE);
  if (!token) {
    await fetch("/api/v1/auth/csrf", { credentials: "same-origin", cache: "no-store" });
    token = readCookie(CSRF_COOKIE);
  }
  return token ?? "";
}

async function unsafe(path: string, method: string, body?: unknown): Promise<Response> {
  const token = await csrfToken();
  return fetch(path, {
    method,
    credentials: "same-origin",
    headers: {
      "content-type": "application/json",
      "X-CSRFToken": token,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

interface AllauthError {
  message?: string;
  param?: string;
}

function firstAllauthMessage(payload: unknown, fallback: string): string {
  if (payload && typeof payload === "object" && "errors" in payload) {
    const errors = (payload as { errors?: AllauthError[] }).errors;
    if (Array.isArray(errors) && errors.length > 0 && errors[0]?.message) {
      return errors[0].message;
    }
  }
  return fallback;
}

/** Log in with email + password via allauth headless. Throws AuthError on failure. */
export async function login(email: string, password: string): Promise<void> {
  const response = await unsafe(`${ALLAUTH}/auth/login`, "POST", { email, password });
  if (response.ok) return;

  let message = "We couldn't sign you in. Check your email and password.";
  try {
    message = firstAllauthMessage(await response.json(), message);
  } catch {
    // non-JSON response; keep the generic message
  }
  if (response.status === 401 || response.status === 400) {
    throw new AuthError("Invalid email or password.", response.status);
  }
  throw new AuthError(message, response.status);
}

/** Log out the current session. */
export async function logout(): Promise<void> {
  await unsafe(`${ALLAUTH}/auth/session`, "DELETE");
}

/** Switch the active tenant (membership is validated on the backend). */
export async function switchTenant(tenantId: string): Promise<void> {
  const response = await unsafe("/api/v1/tenants/switch", "POST", { tenantId });
  if (!response.ok) {
    throw new AuthError("Could not switch tenant.", response.status);
  }
}

/** Fetch the current identity (null when unauthenticated). */
export async function fetchMe(): Promise<Me | null> {
  const response = await fetch("/api/v1/me", {
    credentials: "same-origin",
    cache: "no-store",
  });
  if (response.status !== 200) return null;
  const body = (await response.json()) as { data: Me };
  return body.data;
}
