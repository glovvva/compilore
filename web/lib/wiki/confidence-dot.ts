import { cn } from "@/lib/utils";

export function confidenceDotClass(confidence: number): string {
  if (confidence > 0.7) return "bg-[var(--accent-green)]";
  if (confidence >= 0.4) return "bg-[oklch(0.78_0.14_85)]";
  return "bg-[var(--accent-red)]";
}

export function confidenceBarClass(confidence: number): string {
  return cn(
    "h-full rounded-full transition-[width] duration-200 ease-out",
    confidence > 0.7 && "bg-[var(--accent-green)]",
    confidence >= 0.4 && confidence <= 0.7 && "bg-[oklch(0.78_0.14_85)]",
    confidence < 0.4 && "bg-[var(--accent-red)]",
  );
}
