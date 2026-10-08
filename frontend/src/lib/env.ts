import "server-only";

import { parseServerEnv } from "@/lib/env-schema";

/** Validated server environment. Importing this from client code fails the build. */
export const serverEnv = parseServerEnv(process.env);
