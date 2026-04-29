// ⚠️ PANELS ARE INTENTIONALLY NON-COLLAPSIBLE
// Do not add collapsible, collapsedSize, or collapse/expand logic.
// This has been a recurring bug (fixed 4 times, keeps regressing).
// Panels are resizable via drag but CANNOT be collapsed.
// If you need to change panel behavior, consult the decision log first.

"use client";

import * as React from "react";
import {
  Group,
  Panel,
  Separator,
  useDefaultLayout,
} from "react-resizable-panels";
import { WikiNavBridge } from "@/components/wiki-nav-bridge";
import { QueryPanel } from "@/components/query-panel";
import { InspectorPanel } from "@/components/inspector-panel";
import { StatusBar } from "@/components/status-bar";
import { ThemeToggle } from "@/components/theme-toggle";
import { CommandPalette } from "@/components/command-palette";
import { IngestModal } from "@/components/ingest-modal";
import { createCompilorePanelStorage } from "@/lib/panel-storage";

const DEFAULT_LAYOUT = { "wiki-nav": 25, main: 50, inspector: 25 } as const;

/**
 * Application chrome: resizable **wiki / query / inspect** columns, status bar,
 * theme toggle, command palette, and ingest modal — the four-loop surface in one shell.
 *
 * Side panels are fixed visible (not collapsible); separators remain drag handles.
 */
export function WorkspaceShell({ children }: { children?: React.ReactNode }) {
  const [layoutReady, setLayoutReady] = React.useState(false);

  React.useEffect(() => {
    const keys = ["compilore-panel-layout", "compilore-panel-state"];

    for (const key of keys) {
      const saved = localStorage.getItem(key);
      if (!saved) continue;

      try {
        const layout = JSON.parse(saved);
        const sizes =
          Array.isArray(layout)
            ? layout
            : Array.isArray(layout?.layout)
              ? layout.layout
              : [];
        const hasCollapsed = sizes.some((size: number) => size < 25);
        if (hasCollapsed) {
          localStorage.removeItem(key);
        }
      } catch {
        localStorage.removeItem(key);
      }
    }

    setLayoutReady(true);
  }, []);

  const { defaultLayout, onLayoutChanged } = useDefaultLayout({
    id: "compilore-workspace",
    panelIds: ["wiki-nav", "main", "inspector"],
    storage: createCompilorePanelStorage(),
  });

  if (!layoutReady) {
    return (
      <div className="flex h-dvh max-h-dvh items-center justify-center bg-background text-sm text-muted-foreground">
        Ładowanie układu...
      </div>
    );
  }

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
          defaultSize={25}
          minSize={25}
          maxSize={45}
          className="min-w-0"
        >
          <WikiNavBridge panelRef={{ current: null }} />
        </Panel>

        <Separator className="w-2 shrink-0 bg-border" />

        <Panel id="main" minSize={25} className="min-w-0">
          <QueryPanel>{children}</QueryPanel>
        </Panel>

        <Separator className="w-2 shrink-0 bg-border" />

        <Panel
          id="inspector"
          defaultSize={25}
          minSize={25}
          maxSize={40}
          className="min-w-0"
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
