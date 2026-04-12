"use client";

import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useWorkspace } from "@/components/workspace-context";

/**
 * Modal entry for the **ingest** loop (URL / future file upload). Mock-only until API wiring.
 */
export function IngestModal() {
  const { ingestOpen, setIngestOpen, startMockIngest } = useWorkspace();
  const [url, setUrl] = React.useState("");

  return (
    <Dialog
      open={ingestOpen}
      onOpenChange={(o) => {
        setIngestOpen(o);
        if (!o) setUrl("");
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ingest</DialogTitle>
          <DialogDescription className="font-mono text-xs">
            Add knowledge from a URL (mock pipeline — no network).
          </DialogDescription>
        </DialogHeader>
        <Input
          placeholder="https://example.com/doc"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="font-mono text-sm"
        />
        <DialogFooter className="gap-2 sm:gap-0">
          <Button type="button" variant="ghost" onClick={() => setIngestOpen(false)}>
            Cancel
          </Button>
          <Button
            type="button"
            variant="accent"
            disabled={!url.trim()}
            onClick={() => {
              setIngestOpen(false);
              setUrl("");
              startMockIngest();
            }}
          >
            Start ingest
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
