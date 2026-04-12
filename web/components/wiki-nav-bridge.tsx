"use client";

import * as React from "react";
import type { PanelImperativeHandle } from "react-resizable-panels";
import { WikiNav } from "@/components/wiki-nav";
import { useWorkspace } from "@/components/workspace-context";

export function WikiNavBridge({ panelRef }: { panelRef: React.RefObject<PanelImperativeHandle | null> }) {
  const { selectWikiPage, selectedWikiPage } = useWorkspace();
  return (
    <WikiNav
      panelRef={panelRef}
      onPageSelect={selectWikiPage}
      selectedSlug={selectedWikiPage?.slug}
    />
  );
}
