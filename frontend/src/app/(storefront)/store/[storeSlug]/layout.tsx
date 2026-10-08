import Link from "next/link";
import { notFound } from "next/navigation";

import { BagIcon, SearchIcon, WhatsAppIcon } from "@/components/shared/icons";
import { Button } from "@/components/ui/button";
import { DEMO_CATEGORIES, DEMO_STORE } from "@/lib/demo-data";
import { isValidStoreSlug, storeNameFromSlug } from "@/lib/store-slug";

/**
 * Customer storefront shell: mobile-first, sticky header, category nav, footer with a WhatsApp
 * CTA. Phase 5 replaces the placeholder name/catalog with the tenant profile and theme tokens.
 *
 * Unknown stores are rejected here, before anything streams, so the response is a real 404
 * (rendered by ../not-found.tsx). Phase 5 will look the store up via the API at this point.
 *
 * All affordances here (search, cart, WhatsApp) are visual only in Phase 1.
 */
export default async function StoreLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ storeSlug: string }>;
}) {
  const { storeSlug } = await params;
  if (!isValidStoreSlug(storeSlug)) notFound();
  const storeName = storeNameFromSlug(storeSlug);

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-20 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-4 px-4">
          <Link
            href={`/store/${storeSlug}`}
            className="flex items-center gap-2 text-lg font-semibold tracking-tight"
            aria-label={storeName}
          >
            <span
              aria-hidden="true"
              className="grid size-8 place-items-center rounded-lg bg-primary text-sm font-bold text-primary-foreground"
            >
              {storeName.charAt(0)}
            </span>
            <span data-testid="store-name">{storeName}</span>
          </Link>

          <div className="relative ml-auto hidden flex-1 items-center sm:flex sm:max-w-xs">
            <SearchIcon className="pointer-events-none absolute left-3 size-4 text-muted-foreground" />
            <input
              type="search"
              aria-label="Search products"
              placeholder="Search products…"
              className="h-9 w-full rounded-full border bg-muted/40 pl-9 pr-3 text-sm outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
            />
          </div>

          <div className="ml-auto flex items-center gap-1 sm:ml-0">
            <Button variant="ghost" size="icon" aria-label="Search products" className="sm:hidden">
              <SearchIcon className="size-5" />
            </Button>
            <Button variant="ghost" size="icon" aria-label="Cart" className="relative">
              <BagIcon className="size-5" />
              <span className="absolute -right-0.5 -top-0.5 grid size-4 place-items-center rounded-full bg-brand text-[10px] font-semibold text-brand-foreground">
                2
              </span>
            </Button>
            <Button
              size="sm"
              className="hidden gap-1.5 bg-success text-success-foreground hover:bg-success/90 sm:inline-flex"
            >
              <WhatsAppIcon className="size-4" />
              WhatsApp
            </Button>
          </div>
        </div>

        <nav aria-label="Categories" className="border-t bg-background/80">
          <ul className="mx-auto flex max-w-6xl items-center gap-1 overflow-x-auto px-3 py-2 text-sm">
            {DEMO_CATEGORIES.map((category, index) => (
              <li key={category}>
                <span
                  aria-current={index === 0 ? "true" : undefined}
                  className={
                    index === 0
                      ? "inline-block whitespace-nowrap rounded-full bg-accent px-3 py-1 font-medium text-accent-foreground"
                      : "inline-block whitespace-nowrap rounded-full px-3 py-1 text-muted-foreground"
                  }
                >
                  {category}
                </span>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">{children}</main>

      {/* Mobile sticky WhatsApp CTA */}
      <div className="sticky bottom-0 z-20 border-t bg-background/95 p-3 backdrop-blur sm:hidden">
        <Button className="w-full gap-2 bg-success text-success-foreground hover:bg-success/90">
          <WhatsAppIcon className="size-5" />
          Inquire on WhatsApp
        </Button>
      </div>

      <footer className="border-t">
        <div className="mx-auto grid max-w-6xl gap-6 px-4 py-10 sm:grid-cols-3">
          <div className="space-y-2">
            <p className="font-semibold">{storeName}</p>
            <p className="text-sm text-muted-foreground">{DEMO_STORE.tagline}</p>
            <p className="text-sm text-muted-foreground">{DEMO_STORE.location}</p>
          </div>
          <div className="space-y-2 text-sm">
            <p className="font-medium">Shop</p>
            {DEMO_CATEGORIES.slice(1, 5).map((category) => (
              <p key={category} className="text-muted-foreground">
                {category}
              </p>
            ))}
          </div>
          <div className="space-y-2 text-sm">
            <p className="font-medium">Get in touch</p>
            <p className="flex items-center gap-1.5 text-muted-foreground">
              <WhatsAppIcon className="size-4 text-success" />
              {DEMO_STORE.whatsapp}
            </p>
          </div>
        </div>
        <div className="border-t">
          <p className="mx-auto max-w-6xl px-4 py-4 text-sm text-muted-foreground">
            Powered by Kayaka · demo store with sample data
          </p>
        </div>
      </footer>
    </div>
  );
}
