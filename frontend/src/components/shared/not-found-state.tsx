import Link from "next/link";

import { Button } from "@/components/ui/button";

export function NotFoundState({
  title = "Page not found",
  message = "The page you're looking for doesn't exist or has moved.",
  homeHref = "/",
  homeLabel = "Go to home",
}: {
  title?: string;
  message?: string;
  homeHref?: string;
  homeLabel?: string;
}) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-4 py-16 text-center">
      <p className="text-sm font-medium text-muted-foreground">404</p>
      <h1 className="text-2xl font-semibold">{title}</h1>
      <p className="text-muted-foreground">{message}</p>
      <Button asChild size="lg" variant="outline">
        <Link href={homeHref}>{homeLabel}</Link>
      </Button>
    </div>
  );
}
