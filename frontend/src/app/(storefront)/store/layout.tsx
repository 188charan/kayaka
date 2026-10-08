/**
 * Pass-through layout. It exists so ./not-found.tsx can catch notFound() thrown by
 * [storeSlug]/layout.tsx and show a store-specific 404 instead of the generic one.
 */
export default function StoresLayout({ children }: { children: React.ReactNode }) {
  return children;
}
