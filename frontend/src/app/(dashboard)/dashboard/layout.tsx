import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: { default: "Dashboard", template: "%s · Dashboard · Kayaka" },
  robots: { index: false, follow: false },
};

// Plain, entrepreneur-friendly vocabulary (blueprint §J.7). Only Home exists in Phase 1.
const NAV = [
  { label: "Home", href: "/dashboard" },
  { label: "Products", href: null },
  { label: "Inquiries", href: null },
  { label: "My Store", href: null },
  { label: "Insights", href: null },
] as const;

function NavItems({ variant }: { variant: "sidebar" | "bottom" }) {
  const base =
    variant === "sidebar"
      ? "block rounded-md px-3 py-2 text-sm"
      : "flex min-h-14 flex-1 flex-col items-center justify-center px-1 text-xs";
  return (
    <ul className={variant === "sidebar" ? "space-y-1" : "flex"}>
      {NAV.map((item) => (
        <li key={item.label} className={variant === "bottom" ? "flex flex-1" : undefined}>
          {item.href ? (
            <Link href={item.href} aria-current="page" className={`${base} bg-accent font-medium`}>
              {item.label}
            </Link>
          ) : (
            <span
              aria-disabled="true"
              title="Coming soon"
              className={`${base} text-muted-foreground`}
            >
              {item.label}
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}

/**
 * Tenant dashboard shell: sidebar on desktop, bottom tab bar on mobile (most entrepreneurs
 * manage their store from a phone). Authentication and tenant switching arrive in Phase 2.
 */
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-dvh">
      <aside
        data-testid="dashboard-sidebar"
        className="hidden w-60 shrink-0 border-r p-4 md:block"
        aria-label="Dashboard navigation"
      >
        <p className="mb-6 px-3 text-lg font-semibold">Kayaka</p>
        <nav>
          <NavItems variant="sidebar" />
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center border-b px-4 md:hidden">
          <p className="text-lg font-semibold">Kayaka</p>
        </header>
        {/* pb-20 keeps content clear of the mobile bottom bar */}
        <main className="flex-1 p-4 pb-20 md:p-8 md:pb-8">{children}</main>
      </div>

      <nav
        data-testid="dashboard-bottom-nav"
        aria-label="Dashboard navigation"
        className="fixed inset-x-0 bottom-0 border-t bg-background md:hidden"
      >
        <NavItems variant="bottom" />
      </nav>
    </div>
  );
}
