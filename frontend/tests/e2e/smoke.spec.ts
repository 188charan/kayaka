import { expect, type Page, test } from "@playwright/test";

// Must match the password used to seed demo data in CI (see .github/workflows/ci.yml) and locally.
const DEMO_PASSWORD = process.env.KAYAKA_DEMO_PASSWORD ?? "e2e-demo-password-123456";
const OWNER_EMAIL = "owner@demo.kayaka.local";
const ADMIN_EMAIL = "admin@kayaka.local";

async function login(page: Page, email: string): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(DEMO_PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("**/dashboard");
}

test.describe("public surfaces", () => {
  test("home page renders and reaches the API from the server", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1, name: "Kayaka" })).toBeVisible();
    await expect(page.getByTestId("api-status-server")).toHaveAttribute("data-state", "ok");
  });

  test("storefront shell renders for a valid store slug", async ({ page }) => {
    await page.goto("/store/demo-store");
    await expect(page.getByTestId("store-name")).toHaveText("Demo Store");
    await expect(page.getByRole("heading", { level: 1, name: "Demo Store" })).toBeVisible();
  });

  test("invalid store slug shows the store not-found page with 404", async ({ page }) => {
    const response = await page.goto("/store/Not--Valid");
    expect(response?.status()).toBe(404);
    await expect(page.getByRole("heading", { name: "Store not found" })).toBeVisible();
  });

  test("unknown page shows the not-found page with 404", async ({ page }) => {
    const response = await page.goto("/this-page-does-not-exist");
    expect(response?.status()).toBe(404);
    await expect(page.getByRole("heading", { name: "Page not found" })).toBeVisible();
  });
});

test.describe("authentication", () => {
  test("unauthenticated dashboard redirects to login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("unauthenticated admin redirects to login", async ({ page }) => {
    await page.goto("/admin");
    await expect(page).toHaveURL(/\/login/);
  });

  test("owner can sign in and reach the dashboard, which pings the API via the proxy", async ({
    page,
  }) => {
    const ping = page.waitForResponse("**/api/v1/public/ping");
    await login(page, OWNER_EMAIL);
    await expect(page.getByRole("heading", { level: 1, name: /good morning/i })).toBeVisible();
    const response = await ping;
    expect(response.status()).toBe(200);
    await expect(page.getByTestId("api-status-proxy")).toHaveAttribute("data-state", "ok");
  });

  test("dashboard navigation adapts to the viewport (authenticated)", async ({
    page,
    isMobile,
  }) => {
    await login(page, OWNER_EMAIL);
    const sidebar = page.getByTestId("dashboard-sidebar");
    const bottomNav = page.getByTestId("dashboard-bottom-nav");
    if (isMobile) {
      await expect(bottomNav).toBeVisible();
      await expect(sidebar).toBeHidden();
    } else {
      await expect(sidebar).toBeVisible();
      await expect(bottomNav).toBeHidden();
    }
  });

  test("platform admin can reach the admin overview", async ({ page }) => {
    await login(page, ADMIN_EMAIL);
    await page.goto("/admin");
    await expect(page.getByRole("heading", { name: "Platform overview" })).toBeVisible();
    await expect(page.getByTestId("api-status-server")).toHaveAttribute("data-state", "ok");
  });

  test("tenant user is redirected away from the admin console", async ({ page }) => {
    await login(page, OWNER_EMAIL);
    await page.goto("/admin");
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("signing out returns to the login page", async ({ page }) => {
    await login(page, OWNER_EMAIL);
    await page.getByRole("button", { name: "Account menu" }).first().click();
    await page.getByRole("menuitem", { name: "Sign out" }).click();
    await page.waitForURL("**/login");
  });
});

test.describe("API proxy", () => {
  test("forwards to Django and returns the data envelope", async ({ request }) => {
    const response = await request.get("/api/v1/public/ping", {
      headers: { "X-Request-ID": "e2e-trace-12345" },
    });
    expect(response.status()).toBe(200);
    expect(response.headers()["x-request-id"]).toBe("e2e-trace-12345");
    const body = await response.json();
    expect(body.data.service).toBe("kayaka-api");
  });

  test("unknown API routes return the JSON error envelope", async ({ request }) => {
    const response = await request.get("/api/v1/does-not-exist");
    expect(response.status()).toBe(404);
    const body = await response.json();
    expect(body.error.code).toBe("NOT_FOUND");
    expect(body.error.requestId).toBe(response.headers()["x-request-id"]);
  });

  test("identity endpoint requires authentication", async ({ request }) => {
    const response = await request.get("/api/v1/me");
    expect(response.status()).toBe(401);
    const body = await response.json();
    expect(body.error.code).toBe("NOT_AUTHENTICATED");
  });
});
