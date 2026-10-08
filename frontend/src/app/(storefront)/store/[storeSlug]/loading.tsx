import { Skeleton } from "@/components/ui/skeleton";

export default function StoreLoading() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading store">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {Array.from({ length: 8 }, (_, index) => (
          <Skeleton key={index} className="aspect-[4/5] w-full" />
        ))}
      </div>
    </div>
  );
}
