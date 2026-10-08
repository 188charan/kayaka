import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ErrorState } from "@/components/shared/error-state";
import { StatusBadge } from "@/components/shared/status-badge";
import { isValidStoreSlug, storeNameFromSlug } from "@/lib/store-slug";

afterEach(cleanup);

describe("StatusBadge (frontend smoke test)", () => {
  it("renders an accessible status with its state", () => {
    render(<StatusBadge status="ok" label="API connected" />);
    const status = screen.getByRole("status");
    expect(status.textContent).toContain("API connected");
    expect(status.dataset.state).toBe("ok");
  });
});

describe("ErrorState", () => {
  it("shows a retry action and the error reference", () => {
    const onRetry = vi.fn();
    render(<ErrorState digest="abc123" onRetry={onRetry} />);
    expect(screen.getByRole("alert").textContent).toContain("Reference: abc123");
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });
});

describe("store slugs", () => {
  it.each(["demo-store", "abc", "anjali-decor-2"])("accepts %s", (slug) => {
    expect(isValidStoreSlug(slug)).toBe(true);
  });

  it.each(["ab", "-start", "end-", "double--hyphen", "UPPER", "with space", "x".repeat(41)])(
    "rejects %s",
    (slug) => {
      expect(isValidStoreSlug(slug)).toBe(false);
    },
  );

  it("derives a placeholder display name", () => {
    expect(storeNameFromSlug("anjali-decor")).toBe("Anjali Decor");
  });
});
