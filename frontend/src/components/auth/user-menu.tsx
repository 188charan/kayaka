"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { logout } from "@/lib/auth/client";
import { cn } from "@/lib/utils";

function initialsOf(name: string, email: string): string {
  const source = name.trim() || email;
  const parts = source
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2);
  return parts.map((p) => p.charAt(0).toUpperCase()).join("") || "U";
}

export function UserMenu({
  name,
  email,
  subtitle,
}: {
  name: string;
  email: string;
  subtitle?: string;
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  async function onLogout() {
    setBusy(true);
    try {
      await logout();
      router.replace("/login");
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label="Account menu"
        className={cn(
          "grid size-8 place-items-center rounded-full bg-accent text-xs font-semibold text-accent-foreground",
          "outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50",
        )}
      >
        {initialsOf(name, email)}
      </button>

      {open ? (
        <>
          <button
            type="button"
            aria-hidden="true"
            tabIndex={-1}
            className="fixed inset-0 z-30 cursor-default"
            onClick={() => setOpen(false)}
          />
          <div
            role="menu"
            className="absolute right-0 z-40 mt-2 w-56 overflow-hidden rounded-lg border bg-popover text-popover-foreground shadow-lg"
          >
            <div className="border-b px-3 py-2.5">
              <p className="truncate text-sm font-medium">{name || email}</p>
              <p className="truncate text-xs text-muted-foreground">{email}</p>
              {subtitle ? (
                <p className="mt-0.5 truncate text-xs text-muted-foreground">{subtitle}</p>
              ) : null}
            </div>
            <button
              type="button"
              role="menuitem"
              onClick={onLogout}
              disabled={busy}
              className="block w-full px-3 py-2.5 text-left text-sm hover:bg-accent disabled:opacity-50"
            >
              {busy ? "Signing out…" : "Sign out"}
            </button>
          </div>
        </>
      ) : null}
    </div>
  );
}
