import * as React from "react";
import { cn } from "@/lib/utils";

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "compilore-skeleton rounded-md border border-border bg-transparent",
        className,
      )}
      {...props}
    />
  );
}

export { Skeleton };
