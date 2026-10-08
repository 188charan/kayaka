/**
 * Store slugs: 3–40 chars, lowercase letters, digits and single hyphens, no leading/trailing
 * hyphen. The backend is authoritative (Phase 2); this check only avoids pointless requests.
 */
const STORE_SLUG = /^(?=.{3,40}$)[a-z0-9]+(?:-[a-z0-9]+)*$/;

export function isValidStoreSlug(slug: string): boolean {
  return STORE_SLUG.test(slug);
}

/** Placeholder display name until the store profile comes from the API. */
export function storeNameFromSlug(slug: string): string {
  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
