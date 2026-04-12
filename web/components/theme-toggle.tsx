"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const STORAGE_KEY = "compilore-appearance";

/**
 * Toggles forced light/dark on `<html>`. When storage is empty, `:root` follows
 * `prefers-color-scheme` via CSS (no `data-theme`), matching the Precision Dark default.
 */
export function ThemeToggle({ className }: { className?: string }) {
  const [forced, setForced] = React.useState<"light" | "dark" | null>(null);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      if (v === "light" || v === "dark") {
        setForced(v);
        document.documentElement.setAttribute("data-theme", v);
      } else {
        document.documentElement.removeAttribute("data-theme");
      }
    } catch {
      document.documentElement.removeAttribute("data-theme");
    }
  }, []);

  const resolvedDark = React.useMemo(() => {
    if (!mounted) return true;
    if (forced === "dark") return true;
    if (forced === "light") return false;
    return !window.matchMedia("(prefers-color-scheme: light)").matches;
  }, [forced, mounted]);

  const toggle = React.useCallback(() => {
    const next = resolvedDark ? "light" : "dark";
    setForced(next);
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* ignore */
    }
  }, [resolvedDark]);

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className={cn("shrink-0 border-border", className)}
      aria-label={resolvedDark ? "Switch to light theme" : "Switch to dark theme"}
      onClick={toggle}
    >
      {resolvedDark ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  );
}
