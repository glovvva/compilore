"use client";

import * as React from "react";
import {
  Group,
  Panel,
  Separator,
  useDefaultLayout,
} from "react-resizable-panels";
import type { PanelImperativeHandle } from "react-resizable-panels";
import { WikiNavBridge } from "@/components/wiki-nav-bridge";
import { QueryPanel } from "@/components/query-panel";
import { InspectorPanel } from "@/components/inspector-panel";
import { StatusBar } from "@/components/status-bar";
import { ThemeToggle } from "@/components/theme-toggle";
import { CommandPalette } from "@/components/command-palette";
import { IngestModal } from "@/components/ingest-modal";
import { createCompilorePanelStorage } from "@/lib/panel-storage";

const DEFAULT_LAYOUT = { "wiki-nav": 20, main: 58, inspector: 22 } as const;

/**
 * Application chrome: resizable **wiki / query / inspect** columns, status bar,
 * theme toggle, command palette, and ingest modal — the four-loop surface in one shell.
 *
 * Side panels are fixed visible (not collapsible); separators remain drag handles.
 */
export function WorkspaceShell({ children }: { children?: React.ReactNode }) {
  const { defaultLayout, onLayoutChanged } = useDefaultLayout({
    id: "compilore-workspace",
    panelIds: ["wiki-nav", "main", "inspector"],
    storage: createCompilorePanelStorage(),
  });

  /** Unattached stubs: nav/inspector still pass `panelRef` for optional collapse buttons (no-op). */
  const stubLeftPanelRef = React.useRef<PanelImperativeHandle | null>(null);
  const stubRightPanelRef = React.useRef<PanelImperativeHandle | null>(null);

  return (
    <div className="flex h-dvh max-h-dvh flex-col overflow-hidden bg-background text-foreground">
      <header className="flex h-10 shrink-0 items-center justify-end border-b border-border bg-surface px-2">
        <ThemeToggle />
      </header>

      <Group
        orientation="horizontal"
        className="min-h-0 flex-1"
        defaultLayout={defaultLayout ?? DEFAULT_LAYOUT}
        onLayoutChanged={onLayoutChanged}
      >
        <Panel
          id="wiki-nav"
          defaultSize={20}
          minSize={15}
          maxSize={35}
          className="min-w-0"
        >
          <WikiNavBridge panelRef={stubLeftPanelRef} />
        </Panel>

        <Separator className="w-2 shrink-0 bg-border" />

        <Panel id="main" minSize={30} className="min-w-0">
          <QueryPanel>{children}</QueryPanel>
        </Panel>

        <Separator className="w-2 shrink-0 bg-border" />

        <Panel
          id="inspector"
          defaultSize={22}
          minSize={18}
          maxSize={40}
          className="min-w-0"
        >
          <InspectorPanel panelRef={stubRightPanelRef} />
        </Panel>
      </Group>

      <StatusBar />

      <CommandPalette />
      <IngestModal />
    </div>
  );
}
