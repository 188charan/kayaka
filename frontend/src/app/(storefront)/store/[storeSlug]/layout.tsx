import Link from "next/link";
import { notFound } from "next/navigation";

import { isValidStoreSlug, storeNameFromSlug } from "@/lib/store-slug";

/**
 * Customer storefront shell: mobile-first, compact sticky header, footer.
 * Phase 5 replaces the placeholder name with the tenant profile and theme tokens.
 *
 * Unknown stores are rejected here, before anything streams, so the response is a real 404
 * (rendered by ../not-found.tsx). Phase 5 will look the store up via the API at this point.
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
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <Link
            href={`/store/${storeSlug}`}
            className="text-lg font-semibold"
            data-testid="store-name"
          >
            {storeName}
          </Link>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">{children}</main>

      <footer className="border-t">
        <div className="mx-auto max-w-6xl px-4 py-6 text-sm text-muted-foreground">
          Powered by Kayaka
        </div>
      </footer>
    </div>
  );
}
