import { BagIcon, StarIcon } from "@/components/shared/icons";
import { PlaceholderImage } from "@/components/shared/placeholder-image";
import { Badge } from "@/components/ui/badge";
import { type DemoProduct, formatPrice } from "@/lib/demo-data";

const badgeVariant = {
  New: "brand",
  Bestseller: "success",
  "Low stock": "muted",
} as const;

/**
 * Storefront product card. Static/demo only — the "Add" affordance is non-functional in Phase 1
 * (cart + inquiry wiring arrives in a later phase).
 */
export function ProductCard({ product }: { product: DemoProduct }) {
  const onSale = product.compareAtPrice && product.compareAtPrice > product.price;

  return (
    <article className="group flex flex-col overflow-hidden rounded-xl border bg-card transition-all hover:border-brand/40 hover:shadow-md">
      <div className="relative">
        <PlaceholderImage
          seed={product.id}
          label={product.name}
          className="aspect-[4/5] w-full transition-transform duration-300 group-hover:scale-[1.03]"
        />
        {product.badge ? (
          <Badge variant={badgeVariant[product.badge]} className="absolute left-2.5 top-2.5">
            {product.badge}
          </Badge>
        ) : null}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-medium leading-snug">{product.name}</h3>
          <span className="inline-flex shrink-0 items-center gap-0.5 text-xs text-muted-foreground">
            <StarIcon className="size-3 text-amber-500" />
            {product.rating}
          </span>
        </div>

        <div className="mt-auto flex items-center justify-between gap-2 pt-1">
          <div className="flex items-baseline gap-1.5">
            <span className="text-sm font-semibold">{formatPrice(product.price)}</span>
            {onSale ? (
              <span className="text-xs text-muted-foreground line-through">
                {formatPrice(product.compareAtPrice!)}
              </span>
            ) : null}
          </div>
          <span
            aria-hidden="true"
            title="Add to cart (coming soon)"
            className="grid size-8 place-items-center rounded-full border text-muted-foreground transition-colors group-hover:border-brand/40 group-hover:text-foreground"
          >
            <BagIcon className="size-4" />
          </span>
        </div>
      </div>
    </article>
  );
}
