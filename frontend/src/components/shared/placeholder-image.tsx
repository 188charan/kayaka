import { cn } from "@/lib/utils";

/**
 * Deterministic decorative product/image placeholder. Phase 1 has no media pipeline (R2 arrives
 * later), so we render an inline SVG gradient keyed off a seed plus the item's initials. No
 * network requests, no remote image config. Purely decorative, so it is aria-hidden.
 */
const PALETTES = [
  ["oklch(0.9 0.05 262)", "oklch(0.8 0.1 262)"],
  ["oklch(0.92 0.05 330)", "oklch(0.82 0.09 330)"],
  ["oklch(0.92 0.06 162)", "oklch(0.82 0.09 162)"],
  ["oklch(0.93 0.06 70)", "oklch(0.85 0.1 70)"],
  ["oklch(0.9 0.05 300)", "oklch(0.8 0.09 300)"],
  ["oklch(0.92 0.05 230)", "oklch(0.82 0.09 230)"],
] as const;

function seedFrom(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
  return hash;
}

function initials(label: string): string {
  const words = label.trim().split(/\s+/).slice(0, 2);
  return words.map((w) => w.charAt(0).toUpperCase()).join("");
}

export function PlaceholderImage({
  seed,
  label,
  className,
}: {
  seed: string;
  label: string;
  className?: string;
}) {
  const palette = PALETTES[seedFrom(seed) % PALETTES.length] ?? PALETTES[0];
  const gradientId = `ph-${seedFrom(seed).toString(36)}`;

  return (
    <div aria-hidden="true" className={cn("relative overflow-hidden bg-muted", className)}>
      <svg
        className="size-full"
        viewBox="0 0 100 125"
        preserveAspectRatio="xMidYMid slice"
        role="presentation"
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={palette[0]} />
            <stop offset="100%" stopColor={palette[1]} />
          </linearGradient>
        </defs>
        <rect width="100" height="125" fill={`url(#${gradientId})`} />
        <circle cx="78" cy="26" r="30" fill="oklch(1 0 0 / 0.18)" />
        <circle cx="20" cy="104" r="22" fill="oklch(1 0 0 / 0.12)" />
        <text
          x="50"
          y="62"
          textAnchor="middle"
          dominantBaseline="central"
          fontSize="22"
          fontWeight="600"
          fill="oklch(0.3 0.03 262 / 0.65)"
          fontFamily="ui-sans-serif, system-ui, sans-serif"
        >
          {initials(label)}
        </text>
      </svg>
    </div>
  );
}
