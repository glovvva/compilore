// ⚠️ PANELS ARE INTENTIONALLY NON-COLLAPSIBLE
// Do not add collapsible, collapsedSize, or collapse/expand logic.
// This has been a recurring bug (fixed 4 times, keeps regressing).
// Panels are resizable via drag but CANNOT be collapsed.
// Layout is NOT persisted to localStorage — always starts at 25/50/25.

"use client";

import * as React from "react";
import { Group, Panel, Separator } from "react-resizable-panels";
import { WikiNavBridge } from "@/components/wiki-nav-bridge";
import { QueryPanel } from "@/components/query-panel";
import { InspectorPanel } from "@/components/inspector-panel";
import { StatusBar } from "@/components/status-bar";
import { ThemeToggle } from "@/components/theme-toggle";
import { CommandPalette } from "@/components/command-palette";
import { IngestModal } from "@/components/ingest-modal";

export function WorkspaceShell({ children }: { children?: React.ReactNode }) {
  return (
    <div className="flex h-dvh max-h-dvh flex-col overflow-hidden bg-background text-foreground">
      <header className="flex h-10 shrink-0 items-center justify-end border-b border-border bg-surface px-2">
        <ThemeToggle />
      </header>

      <Group
        orientation="horizontal"
        className="min-h-0 flex-1"
      >
        <Panel
          defaultSize={25}
          minSize={25}
          maxSize={45}
          className="overflow-hidden"
        >
          <WikiNavBridge />
        </Panel>

        <Separator className="w-2 shrink-0 bg-border" />

        <Panel defaultSize={50} minSize={25} className="overflow-hidden">
          <QueryPanel>{children}</QueryPanel>
        </Panel>

        <Separator className="w-2 shrink-0 bg-border" />

        <Panel
          defaultSize={25}
          minSize={25}
          maxSize={40}
          className="overflow-hidden"
        >
          <InspectorPanel panelRef={{ current: null }} />
        </Panel>
      </Group>

      <StatusBar />

      <CommandPalette />
      <IngestModal />
    </div>
  );
}
