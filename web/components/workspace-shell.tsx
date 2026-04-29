"use client";

import * as React from "react";
import { ChevronRight } from "lucide-react";
import { WikiNavBridge } from "@/components/wiki-nav-bridge";
import { QueryPanel } from "@/components/query-panel";
import { InspectorPanel } from "@/components/inspector-panel";
import { StatusBar } from "@/components/status-bar";
import { ThemeToggle } from "@/components/theme-toggle";
import { CommandPalette } from "@/components/command-palette";
import { IngestModal } from "@/components/ingest-modal";
import { cn } from "@/lib/utils";

export function WorkspaceShell({ children }: { children?: React.ReactNode }) {
  const [leftOpen, setLeftOpen] = React.useState(true);
  const [rightOpen, setRightOpen] = React.useState(true);

  return (
    <div className="flex h-dvh max-h-dvh flex-col overflow-hidden bg-background text-foreground">
      <header className="flex h-10 shrink-0 items-center justify-between border-b border-border bg-surface px-2">
        <div className="flex items-center">
          {!leftOpen && (
            <button
              type="button"
              onClick={() => setLeftOpen(true)}
              className="flex size-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-background hover:text-foreground"
              aria-label="Open wiki sidebar"
            >
              <ChevronRight className="size-4" />
            </button>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!rightOpen && (
            <button
              type="button"
              onClick={() => setRightOpen(true)}
              className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground transition-colors hover:text-foreground"
              aria-label="Open inspector"
            >
              Inspector
            </button>
          )}
          <ThemeToggle />
        </div>
      </header>

      <div className="relative min-h-0 flex-1">
        {leftOpen && <WikiNavBridge onClose={() => setLeftOpen(false)} />}

        <main
          className={cn(
            "h-full overflow-hidden",
            leftOpen ? "pl-72" : "pl-0",
            rightOpen ? "pr-80" : "pr-0",
          )}
        >
          <QueryPanel>{children}</QueryPanel>
        </main>

        {rightOpen && <InspectorPanel onClose={() => setRightOpen(false)} />}
      </div>

      <StatusBar />
      <CommandPalette />
      <IngestModal />
    </div>
  );
}
