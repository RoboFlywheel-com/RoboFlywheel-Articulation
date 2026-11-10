// SPDX-License-Identifier: Apache-2.0

import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): React.JSX.Element {
  return <div className={cn("animate-pulse rounded-sm bg-[#eaeaea]", className)} {...props} />;
}
