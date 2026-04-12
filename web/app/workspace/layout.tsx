import type { ReactNode } from "react";
import { WorkspaceProvider } from "@/components/workspace-context";
import { WorkspaceShell } from "@/components/workspace-shell";

/**
 * Persistent three-panel workspace for Compilore (ingest, query, inspect, lint).
 */
export default function WorkspaceLayout({ children }: { children: ReactNode }) {
  return (
    <WorkspaceProvider>
      <WorkspaceShell>{children}</WorkspaceShell>
    </WorkspaceProvider>
  );
}
