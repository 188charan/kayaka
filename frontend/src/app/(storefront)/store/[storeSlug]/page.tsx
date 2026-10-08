import type { Metadata } from "next";

import { Skeleton } from "@/components/ui/skeleton";
import { storeNameFromSlug } from "@/lib/store-slug";

// The layout has already rejected invalid slugs with a 404.
type Props = { params: Promise<{ storeSlug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { storeSlug } = await params;
  return {
    title: storeNameFromSlug(storeSlug),
    // Placeholder stores must not be indexed. Real stores get SEO metadata in Phase 5.
    robots: { index: false, follow: false },
  };
}

export default async function StoreHomePage({ params }: Props) {
  const { storeSlug } = await params;

  return (
    <section aria-labelledby="store-heading" className="space-y-6">
      <div className="space-y-1">
        <h1 id="store-heading" className="text-2xl font-semibold">
          {storeNameFromSlug(storeSlug)}
        </h1>
        <p className="text-muted-foreground">
          This storefront is a placeholder. Products and customization arrive in later phases.
        </p>
      </div>

      {/* Mobile-first grid: 2 columns on phones, up to 4 on desktop. */}
      <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4" aria-label="Products">
        {Array.from({ length: 8 }, (_, index) => (
          <li key={index} className="space-y-2">
            <Skeleton className="aspect-[4/5] w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/3" />
          </li>
        ))}
      </ul>
    </section>
  );
}
