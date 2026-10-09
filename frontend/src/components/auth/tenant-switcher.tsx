"use client";

import { useRouter } from "next/navigation";
import { useId, useState } from "react";

import { StoreIcon } from "@/components/shared/icons";
import { switchTenant } from "@/lib/auth/client";
import type { Membership } from "@/lib/auth/types";

/**
 * Active-tenant selector. With a single tenant it just shows the name; with several it switches
 * the active tenant on the backend (membership is always re-validated server-side) and refreshes.
 */
export function TenantSwitcher({
  memberships,
  activeTenantId,
}: {
  memberships: Membership[];
  activeTenantId: string | null;
}) {
  const router = useRouter();
  const selectId = useId();
  const [busy, setBusy] = useState(false);

  if (memberships.length === 0) return null;

  const current = activeTenantId ?? memberships[0]!.tenant.id;

  if (memberships.length === 1) {
    return (
      <span className="flex items-center gap-2 text-sm font-medium">
        <StoreIcon className="size-4 text-brand" />
        {memberships[0]!.tenant.name}
      </span>
    );
  }

  async function onChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const tenantId = event.target.value;
    setBusy(true);
    try {
      await switchTenant(tenantId);
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <label htmlFor={selectId} className="flex items-center gap-2">
      <StoreIcon className="size-4 text-brand" aria-hidden="true" />
      <span className="sr-only">Active tenant</span>
      <select
        id={selectId}
        value={current}
        onChange={onChange}
        disabled={busy}
        className="h-9 rounded-md border bg-background px-2 text-sm outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:opacity-50"
      >
        {memberships.map((m) => (
          <option key={m.tenant.id} value={m.tenant.id}>
            {m.tenant.name}
          </option>
        ))}
      </select>
    </label>
  );
}
