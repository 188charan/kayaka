/**
 * Identity/tenancy shapes returned by the backend (/api/v1/me, /api/v1/tenants). These mirror the
 * DRF serializers in kayaka.tenancy.api.serializers and the OpenAPI schema; the backend remains
 * the source of truth for authorization — anything here is for rendering only.
 */

export interface TenantRef {
  id: string;
  name: string;
  slug: string;
  status: string;
}

export interface Membership {
  tenant: TenantRef;
  role: string;
  status: string;
  permissions: string[];
}

export interface Me {
  id: string;
  email: string;
  fullName: string;
  isAuthenticated: boolean;
  platformRoles: string[];
  platformPermissions: string[];
  activeTenantId: string | null;
  memberships: Membership[];
}

export interface TenantSummary {
  id: string;
  name: string;
  slug: string;
  status: string;
  role: string | null;
  permissions: string[];
}

/** The user's active membership (or the first one) — used to label the dashboard. */
export function activeMembership(me: Me): Membership | null {
  if (me.activeTenantId) {
    const match = me.memberships.find((m) => m.tenant.id === me.activeTenantId);
    if (match) return match;
  }
  return me.memberships[0] ?? null;
}

export function hasPlatformAccess(me: Me): boolean {
  return me.platformRoles.length > 0;
}
