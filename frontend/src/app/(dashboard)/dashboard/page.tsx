import type { Metadata } from "next";

import { ApiStatusClient } from "@/components/shared/api-status-client";

export const metadata: Metadata = { title: "Home" };

export default function DashboardHomePage() {
  return (
    <div className="max-w-2xl space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Welcome to your store</h1>
        <p className="text-muted-foreground">
          Sign-in and your store setup checklist arrive in the next phase.
        </p>
      </div>
      <ApiStatusClient />
    </div>
  );
}
