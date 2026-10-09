import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { TenantSwitcher } from "@/components/auth/tenant-switcher";
import { UserMenu } from "@/components/auth/user-menu";
import { BrandMark } from "@/components/shared/brand-mark";
import {
  BellIcon,
  BoxIcon,
  ChartIcon,
  HomeIcon,
  ListIcon,
  StoreIcon,
  TagIcon,
  UsersIcon,
} from "@/components/shared/icons";
import { Button } from "@/components/ui/button";
import { getServerMe } from "@/lib/auth/server";
import { activeMembership } from "@/lib/auth/types";

export const metadata: Metadata = {
  title: { default: "Dashboard", template: "%s · Dashboard · Kayaka" },
  robots: { index: false, follow: false },
};

type NavItem = {
  label: string;
  href: string | null;
  icon: typeof HomeIcon;
  phase?: string;
};

// Plain, entrepreneur-friendly vocabulary (blueprint §J.7). Only Home exists in Phase 2.
const NAV: NavItem[] = [
  { label: "Home", href: "/dashboard", icon: HomeIcon },
  { label: "Products", href: null, icon: BoxIcon, phase: "Phase 3" },
  { label: "Categories", href: null, icon: TagIcon, phase: "Phase 3" },
  { label: "Inquiries", href: null, icon: ListIcon, phase: "Phase 6" },
  { label: "Customers", href: null, icon: UsersIcon, phase: "Phase 6" },
  { label: "My Store", href: null, icon: StoreIcon, phase: "Phase 5" },
  { label: "Insights", href: null, icon: ChartIcon, phase: "Phase 8" },
];

const MOBILE_NAV = NAV.filter((item) =>
  ["Home", "Products", "Inquiries", "Insights", "My Store"].includes(item.label),
);

function SidebarItem({ item }: { item: NavItem }) {
  const Icon = item.icon;
  if (item.href) {
    return (
      <Link
        href={item.href}
        aria-current="page"
        className="flex items-center gap-3 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-accent-foreground"
      >
        <Icon className="size-4.5" />
        {item.label}
      </Link>
    );
  }
  return (
    <span
      aria-disabled="true"
      title={`Coming in ${item.phase}`}
      className="flex items-center justify-between gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted/60"
    >
      <span className="flex items-center gap-3">
        <Icon className="size-4.5" />
        {item.label}
      </span>
      <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-medium">Soon</span>
    </span>
  );
}

/**
 * Tenant dashboard shell. Authentication is enforced on the server here (unauthenticated users
 * are redirected to /login) AND independently by every backend API — this guard is UX, not the
 * security boundary. Sidebar on desktop, bottom tab bar on mobile.
 */
export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const me = await getServerMe();
  if (!me) redirect("/login?next=/dashboard");

  const member = activeMembership(me);
  const tenantName = member?.tenant.name ?? "No tenant yet";
  const tenantSlug = member ? `${member.tenant.slug}.kayaka.store` : "—";
  const roleLabel = member ? member.role.charAt(0) + member.role.slice(1).toLowerCase() : "Member";

  return (
    <div className="flex min-h-dvh bg-muted/30">
      <aside
        data-testid="dashboard-sidebar"
        className="hidden w-64 shrink-0 flex-col border-r bg-background md:flex"
        aria-label="Dashboard navigation"
      >
        <div className="flex h-16 items-center border-b px-5">
          <BrandMark label="Kayaka" />
        </div>

        <div className="flex items-center gap-3 border-b px-5 py-4">
          <span
            aria-hidden="true"
            className="grid size-9 place-items-center rounded-lg bg-primary text-sm font-bold text-primary-foreground"
          >
            {tenantName.charAt(0)}
          </span>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{tenantName}</p>
            <p className="truncate text-xs text-muted-foreground">{tenantSlug}</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          {NAV.map((item) => (
            <SidebarItem key={item.label} item={item} />
          ))}
        </nav>

        <div className="flex items-center gap-3 border-t px-5 py-4">
          <UserMenu name={me.fullName} email={me.email} subtitle={`${roleLabel} · ${tenantName}`} />
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{me.fullName || me.email}</p>
            <p className="truncate text-xs text-muted-foreground">{roleLabel}</p>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between gap-3 border-b bg-background/95 px-4 backdrop-blur md:px-8">
          <div className="flex items-center gap-2 md:hidden">
            <BrandMark label="Kayaka" />
          </div>
          <div className="hidden md:block">
            <TenantSwitcher memberships={me.memberships} activeTenantId={me.activeTenantId} />
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" aria-label="Notifications" className="relative">
              <BellIcon className="size-5" />
              <span className="absolute right-1.5 top-1.5 size-2 rounded-full bg-brand" />
            </Button>
            <UserMenu
              name={me.fullName}
              email={me.email}
              subtitle={`${roleLabel} · ${tenantName}`}
            />
          </div>
        </header>

        {/* pb-24 keeps content clear of the mobile bottom bar */}
        <main className="flex-1 p-4 pb-24 md:p-8 md:pb-8">{children}</main>
      </div>

      <nav
        data-testid="dashboard-bottom-nav"
        aria-label="Dashboard navigation"
        className="fixed inset-x-0 bottom-0 z-20 border-t bg-background/95 backdrop-blur md:hidden"
      >
        <ul className="flex">
          {MOBILE_NAV.map((item) => {
            const Icon = item.icon;
            const content = (
              <>
                <Icon className="size-5" />
                <span>{item.label}</span>
              </>
            );
            return (
              <li key={item.label} className="flex flex-1">
                {item.href ? (
                  <Link
                    href={item.href}
                    aria-current="page"
                    className="flex min-h-16 flex-1 flex-col items-center justify-center gap-1 px-1 text-[11px] font-medium text-brand"
                  >
                    {content}
                  </Link>
                ) : (
                  <span
                    aria-disabled="true"
                    title={`Coming in ${item.phase}`}
                    className="flex min-h-16 flex-1 flex-col items-center justify-center gap-1 px-1 text-[11px] text-muted-foreground"
                  >
                    {content}
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
