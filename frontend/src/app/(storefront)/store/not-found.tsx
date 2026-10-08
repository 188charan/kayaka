import { NotFoundState } from "@/components/shared/not-found-state";

export default function StoreNotFound() {
  return (
    <NotFoundState
      title="Store not found"
      message="This store doesn't exist or isn't available right now. Check the link and try again."
    />
  );
}
