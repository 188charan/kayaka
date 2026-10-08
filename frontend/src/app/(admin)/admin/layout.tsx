import type { Metadata } from "next";

export const metadata: Metadata = {
  title: { default: "Admin", template: "%s · Admin · Kayaka" },
  robots: { index: false, follow: false },
};

/** Platform admin shell: information-dense, desktop-first. Access control arrives in Phase 2. */
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh bg-muted/40">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-12 max-w-7xl items-center gap-6 px-4 text-sm">
          <p className="font-semibold">Kayaka Admin</p>
          <nav aria-label="Admin navigation" className="flex gap-4 text-muted-foreground">
            <span aria-current="page" className="font-medium text-foreground">
              Overview
            </span>
            <span aria-disabled="true" title="Coming soon">
              Tenants
            </span>
            <span aria-disabled="true" title="Coming soon">
              Audit log
            </span>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl p-4">{children}</main>
    </div>
  );
}
