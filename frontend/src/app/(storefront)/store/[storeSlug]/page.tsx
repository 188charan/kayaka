import type { Metadata } from "next";

import { ArrowRightIcon, SparkleIcon, WhatsAppIcon } from "@/components/shared/icons";
import { ProductCard } from "@/components/shared/product-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DEMO_PRODUCTS, DEMO_STORE } from "@/lib/demo-data";
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
  const storeName = storeNameFromSlug(storeSlug);
  const featured = DEMO_PRODUCTS.slice(0, 3);

  return (
    <div className="space-y-10">
      {/* Hero */}
      <section
        aria-labelledby="store-heading"
        className="relative overflow-hidden rounded-2xl border bg-gradient-to-br from-accent/60 via-background to-background p-6 md:p-10"
      >
        <div className="max-w-xl space-y-4">
          <Badge variant="brand">
            <SparkleIcon className="size-3" />
            New collection
          </Badge>
          <h1 id="store-heading" className="text-3xl font-semibold tracking-tight md:text-4xl">
            {storeName}
          </h1>
          <p className="text-muted-foreground">{DEMO_STORE.tagline}</p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button size="lg">Shop the collection</Button>
            <Button
              size="lg"
              variant="outline"
              className="gap-2 border-success/40 text-success hover:bg-success/10"
            >
              <WhatsAppIcon className="size-5" />
              Inquire on WhatsApp
            </Button>
          </div>
        </div>
      </section>

      {/* Featured */}
      <section aria-labelledby="featured-heading" className="space-y-4">
        <div className="flex items-end justify-between gap-2">
          <div>
            <h2 id="featured-heading" className="text-xl font-semibold tracking-tight">
              Featured
            </h2>
            <p className="text-sm text-muted-foreground">Handpicked pieces from the studio</p>
          </div>
          <span className="flex items-center gap-1 text-sm text-muted-foreground">
            View all
            <ArrowRightIcon className="size-4" />
          </span>
        </div>
        <ul className="grid grid-cols-2 gap-4 lg:grid-cols-3" aria-label="Featured products">
          {featured.map((product) => (
            <li key={product.id}>
              <ProductCard product={product} />
            </li>
          ))}
        </ul>
      </section>

      {/* All products */}
      <section aria-labelledby="all-heading" className="space-y-4">
        <h2 id="all-heading" className="text-xl font-semibold tracking-tight">
          All products
        </h2>
        <ul
          className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4"
          aria-label="All products"
        >
          {DEMO_PRODUCTS.map((product) => (
            <li key={product.id}>
              <ProductCard product={product} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
