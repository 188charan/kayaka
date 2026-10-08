import { expect, test } from "@playwright/test";

test.describe("walking skeleton", () => {
  test("home page renders and reaches the API from the server", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1, name: "Kayaka" })).toBeVisible();
    await expect(page.getByTestId("api-status-server")).toHaveAttribute("data-state", "ok");
  });

  test("dashboard reaches the API from the browser through the proxy", async ({ page }) => {
    const ping = page.waitForResponse("**/api/v1/public/ping");
    await page.goto("/dashboard");
    const response = await ping;
    expect(response.status()).toBe(200);
    expect(response.headers()["x-request-id"]).toBeTruthy();
    await expect(page.getByTestId("api-status-proxy")).toHaveAttribute("data-state", "ok");
  });

  test("dashboard navigation adapts to the viewport", async ({ page, isMobile }) => {
    await page.goto("/dashboard");
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

  test("admin overview renders", async ({ page }) => {
    await page.goto("/admin");
    await expect(page.getByRole("heading", { name: "Platform overview" })).toBeVisible();
    await expect(page.getByTestId("api-status-server")).toHaveAttribute("data-state", "ok");
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
});
