"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useWorkspace } from "@/components/workspace-context";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

/**
 * Footer chrome for the workspace: tenant identity, aggregate wiki health, and
 * model routing hints across the **compile** and **query** loops (brief four-loop architecture).
 */
export function StatusBar() {
  const { stats } = useWorkspace();
  const router = useRouter();
  const [signingOut, setSigningOut] = React.useState(false);

  async function handleSignOut() {
    setSigningOut(true);
    try {
      const supabase = createSupabaseBrowserClient();
      await supabase.auth.signOut();
      router.push("/login");
      router.refresh();
    } finally {
      setSigningOut(false);
    }
  }

  return (
    <footer className="flex h-6 w-full shrink-0 items-center border-t border-border bg-surface px-3 font-mono text-[11px] text-muted-foreground transition-colors duration-200 ease-out">
      <div className="flex min-w-0 flex-1 items-center gap-1.5 truncate">
        <span className="text-[var(--accent-green)]" aria-hidden>
          ●
        </span>
        <span className="truncate">bartek-playground</span>
      </div>
      <div className="hidden flex-1 justify-center truncate text-center sm:flex">
        {stats.totalPages} pages · ${stats.costThisMonthUsd.toFixed(2)} this month
      </div>
      <div className="flex min-w-0 flex-1 items-center justify-end gap-3 truncate text-right">
        <span className="hidden truncate sm:inline">
          compile: claude-sonnet · query: gemma-4-31b
        </span>
        <button
          type="button"
          onClick={handleSignOut}
          disabled={signingOut}
          className="shrink-0 cursor-pointer border-0 bg-transparent p-0 font-mono text-[11px] text-muted-foreground underline-offset-2 hover:text-foreground hover:underline disabled:opacity-50"
        >
          {signingOut ? "…" : "Sign out"}
        </button>
      </div>
    </footer>
  );
}
