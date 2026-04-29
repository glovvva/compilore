"use client";

import { WikiNav } from "@/components/wiki-nav";
import { useWorkspace } from "@/components/workspace-context";

export function WikiNavBridge({ onClose }: { onClose: () => void }) {
  const { selectWikiPage, selectedWikiPage } = useWorkspace();
  return (
    <WikiNav
      onPageSelect={selectWikiPage}
      selectedSlug={selectedWikiPage?.slug}
      onClose={onClose}
    />
  );
}
