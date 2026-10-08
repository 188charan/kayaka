import { cn } from "@/lib/utils";

/**
 * Kayaka wordmark. The glyph is decorative (aria-hidden); the literal text "Kayaka" carries
 * the accessible name. Pass `label` to override the wordmark text (e.g. a tenant store name)
 * while keeping the brand glyph.
 */
export function BrandMark({
  label = "Kayaka",
  className,
  glyphClassName,
}: {
  label?: string;
  className?: string;
  glyphClassName?: string;
}) {
  return (
    <span className={cn("inline-flex items-center gap-2 font-semibold tracking-tight", className)}>
      <span
        aria-hidden="true"
        className={cn(
          "grid size-7 place-items-center rounded-lg bg-primary text-primary-foreground",
          glyphClassName,
        )}
      >
        <svg viewBox="0 0 24 24" className="size-4" fill="none" aria-hidden="true">
          <path
            d="M7 4v16M7 12l8-8M7 12l8 8"
            stroke="currentColor"
            strokeWidth={2.25}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
      {label}
    </span>
  );
}
