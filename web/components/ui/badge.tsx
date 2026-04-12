import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded border px-2 py-0.5 font-mono text-[11px] font-normal uppercase tracking-wide transition-opacity duration-200 ease-out",
  {
    variants: {
      variant: {
        default: "border-border bg-surface text-muted-foreground",
        accent: "border-accent/50 bg-accent/10 text-foreground",
        green: "border-[var(--accent-green)]/40 bg-[var(--accent-green)]/10 text-[var(--accent-green)]",
        red: "border-[var(--accent-red)]/40 bg-[var(--accent-red)]/10 text-[var(--accent-red)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
