"use client";

import * as React from "react";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useWorkspace } from "@/components/workspace-context";
import { useWikiPages } from "@/hooks/use-wiki-pages";

function fuzzyScore(query: string, title: string, slug: string): number {
  const q = query.toLowerCase().trim();
  if (!q) return 1;
  const t = title.toLowerCase();
  const s = slug.toLowerCase();
  if (t === q || s === q) return 100;
  if (t.includes(q) || s.includes(q)) return 50;
  const parts = q.split(/\s+/).filter(Boolean);
  let sc = 0;
  for (const p of parts) {
    if (t.includes(p)) sc += 10;
    if (s.includes(p)) sc += 8;
  }
  return sc;
}

/**
 * Global **command** surface (⌘K): ingest shortcuts, query focus, lint gate, stats,
 * wiki fuzzy open, and paste — wiring the four loops without leaving the keyboard.
 */
export function CommandPalette() {
  const {
    commandOpen,
    setCommandOpen,
    focusQueryInput,
    setLintConfirmOpen,
    setStatsModalOpen,
    setPasteModalOpen,
    selectWikiPage,
    startMockIngest,
  } = useWorkspace();
  const { pages: cmdWikiPages } = useWikiPages();

  const [mode, setMode] = React.useState<"root" | "ingest-url" | "wiki">("root");
  const [rootQ, setRootQ] = React.useState("");
  const [urlDraft, setUrlDraft] = React.useState("");
  const [wikiQ, setWikiQ] = React.useState("");

  React.useEffect(() => {
    if (!commandOpen) {
      window.setTimeout(() => {
        setMode("root");
        setRootQ("");
        setUrlDraft("");
        setWikiQ("");
      }, 0);
    }
  }, [commandOpen]);

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommandOpen(true);
      }
    };
    window.addEventListener("keydown", down);
    return () => window.removeEventListener("keydown", down);
  }, [setCommandOpen]);

  const rankedWiki = React.useMemo(() => {
    const q = wikiQ.trim();
    if (!q) return cmdWikiPages.slice(0, 12);
    return [...cmdWikiPages]
      .map((p) => ({ p, sc: fuzzyScore(q, p.title, p.slug) }))
      .filter((x) => x.sc > 0)
      .sort((a, b) => b.sc - a.sc)
      .slice(0, 12)
      .map((x) => x.p);
  }, [wikiQ, cmdWikiPages]);

  const inputValue = mode === "root" ? rootQ : mode === "ingest-url" ? urlDraft : wikiQ;
  const setInputValue = (v: string) => {
    if (mode === "root") setRootQ(v);
    else if (mode === "ingest-url") setUrlDraft(v);
    else setWikiQ(v);
  };

  const placeholder =
    mode === "root"
      ? "Type a command or search…"
      : mode === "ingest-url"
        ? "https://…"
        : "Fuzzy search wiki…";

  return (
    <>
      <CommandDialog
        open={commandOpen}
        onOpenChange={setCommandOpen}
        shouldFilter={mode === "root"}
      >
        <VisuallyHidden>
          <DialogTitle>Command Palette</DialogTitle>
        </VisuallyHidden>
        <CommandInput
          placeholder={placeholder}
          value={inputValue}
          onValueChange={setInputValue}
          onKeyDown={(e) => {
            if (mode === "ingest-url" && e.key === "Enter" && urlDraft.trim()) {
              e.preventDefault();
              setCommandOpen(false);
              startMockIngest();
            }
          }}
        />
        {mode === "root" && (
          <CommandList>
            <CommandEmpty>No results.</CommandEmpty>
            <CommandGroup heading="Actions">
              <CommandItem
                onSelect={() => {
                  setMode("ingest-url");
                  setUrlDraft("");
                }}
              >
                Ingest URL…
              </CommandItem>
              <CommandItem
                onSelect={() => {
                  setCommandOpen(false);
                  focusQueryInput();
                }}
              >
                Ask (focus query)
              </CommandItem>
              <CommandItem
                onSelect={() => {
                  setCommandOpen(false);
                  setLintConfirmOpen(true);
                }}
              >
                Lint wiki…
              </CommandItem>
              <CommandItem
                onSelect={() => {
                  setCommandOpen(false);
                  setStatsModalOpen(true);
                }}
              >
                Stats dashboard
              </CommandItem>
              <CommandItem
                onSelect={() => {
                  setMode("wiki");
                  setWikiQ("");
                }}
              >
                Open wiki page…
              </CommandItem>
              <CommandItem
                onSelect={() => {
                  setCommandOpen(false);
                  setPasteModalOpen(true);
                }}
              >
                New paste…
              </CommandItem>
            </CommandGroup>
          </CommandList>
        )}
        {mode === "ingest-url" && (
          <div className="border-t border-border px-3 py-2 font-mono text-[10px] text-muted-foreground">
            Enter to start mock ingest · Esc to close
          </div>
        )}
        {mode === "wiki" && (
          <CommandList>
            {rankedWiki.map((p) => (
              <CommandItem
                key={p.id}
                value={`${p.title} ${p.slug}`}
                onSelect={() => {
                  selectWikiPage(p);
                  setCommandOpen(false);
                }}
              >
                <span className="truncate">{p.title}</span>
                <span className="ml-auto font-mono text-[10px] text-muted-foreground">{p.slug}</span>
              </CommandItem>
            ))}
          </CommandList>
        )}
      </CommandDialog>

      <LintDialogs />
      <StatsModal />
      <PasteModal />
    </>
  );
}

function LintDialogs() {
  const { lintConfirmOpen, setLintConfirmOpen, runMockLint } = useWorkspace();
  return (
    <Dialog open={lintConfirmOpen} onOpenChange={setLintConfirmOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Run lint?</DialogTitle>
          <DialogDescription className="font-mono text-xs">
            Mock lint will flag structural issues before the next compile loop (no API).
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button type="button" variant="ghost" onClick={() => setLintConfirmOpen(false)}>
            Cancel
          </Button>
          <Button type="button" variant="destructive" onClick={runMockLint}>
            Run lint
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function StatsModal() {
  const { statsModalOpen, setStatsModalOpen, stats } = useWorkspace();
  return (
    <Dialog open={statsModalOpen} onOpenChange={setStatsModalOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Health dashboard</DialogTitle>
          <DialogDescription className="font-mono text-xs">Mock aggregate stats for the workspace.</DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 gap-2 font-mono text-sm">
          <div className="rounded-md border border-border p-2">Pages: {stats.totalPages}</div>
          <div className="rounded-md border border-border p-2">Concepts: {stats.concepts}</div>
          <div className="rounded-md border border-border p-2">Entities: {stats.entities}</div>
          <div className="rounded-md border border-border p-2">Sources: {stats.sources}</div>
          <div className="rounded-md border border-border p-2">Outputs: {stats.outputs}</div>
          <div className="rounded-md border border-border p-2 text-[var(--cost)]">
            ${stats.costThisMonthUsd.toFixed(2)} / mo
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function PasteModal() {
  const { pasteModalOpen, setPasteModalOpen } = useWorkspace();
  return (
    <Dialog open={pasteModalOpen} onOpenChange={setPasteModalOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New paste</DialogTitle>
          <DialogDescription className="font-mono text-xs">
            Paste markdown (mock — will wire to ingest later).
          </DialogDescription>
        </DialogHeader>
        <textarea
          rows={8}
          className="w-full resize-y rounded-md border border-border bg-background p-2 font-mono text-xs text-foreground outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
          placeholder="# Title…"
        />
        <DialogFooter>
          <Button type="button" variant="ghost" onClick={() => setPasteModalOpen(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
