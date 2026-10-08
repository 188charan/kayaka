import type { Metadata } from "next";

import { BrandMark } from "@/components/shared/brand-mark";
import {
  DashboardIcon,
  GaugeIcon,
  ListIcon,
  PulseIcon,
  ShieldIcon,
  UsersIcon,
} from "@/components/shared/icons";

export const metadata: Metadata = {
  title: { default: "Admin", template: "%s · Admin · Kayaka" },
  robots: { index: false, follow: false },
};

const NAV = [
  { label: "Overview", icon: DashboardIcon, active: true },
  { label: "Tenants", icon: UsersIcon, active: false },
  { label: "Health", icon: PulseIcon, active: false },
  { label: "Audit log", icon: ListIcon, active: false },
  { label: "Usage", icon: GaugeIcon, active: false },
] as const;

/** Platform admin shell: information-dense, desktop-first. Access control arrives in Phase 2. */
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh bg-muted/40">
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="flex h-14 items-center gap-3 px-4">
          <BrandMark label="Kayaka" />
          <span className="flex items-center gap-1.5 rounded-full border border-brand/30 bg-brand/10 px-2.5 py-0.5 text-xs font-medium text-accent-foreground">
            <ShieldIcon className="size-3.5" />
            Platform console
          </span>
          <span className="ml-auto text-xs text-muted-foreground">
            Signed in as Charan · PLATFORM_ADMIN (demo)
          </span>
        </div>
      </header>

      <div className="flex">
        <aside
          className="hidden w-56 shrink-0 border-r bg-background md:block"
          aria-label="Admin navigation"
        >
          <nav className="sticky top-14 space-y-1 p-3">
            {NAV.map((item) => {
              const Icon = item.icon;
              return item.active ? (
                <span
                  key={item.label}
                  aria-current="page"
                  className="flex items-center gap-3 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-accent-foreground"
                >
                  <Icon className="size-4.5" />
                  {item.label}
                </span>
              ) : (
                <span
                  key={item.label}
                  aria-disabled="true"
                  title="Coming soon"
                  className="flex items-center justify-between gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted/60"
                >
                  <span className="flex items-center gap-3">
                    <Icon className="size-4.5" />
                    {item.label}
                  </span>
                  <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-medium">
                    Soon
                  </span>
                </span>
              );
            })}
          </nav>
        </aside>

        <main className="min-w-0 flex-1 p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
