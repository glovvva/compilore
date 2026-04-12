"use client";

import * as React from "react";
import type { PanelImperativeHandle } from "react-resizable-panels";
import { BookMarked, Brain, ChevronLeft, FileText, Plus, Sparkles, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { WikiPage, WikiPageType } from "@/lib/types/wiki";
import { confidenceDotClass } from "@/lib/wiki/confidence-dot";
import { useWikiPages } from "@/hooks/use-wiki-pages";
import { useWorkspace } from "@/components/workspace-context";

function escapeRegExp(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function HighlightTitle({ title, query }: { title: string; query: string }) {
  const needle = query.trim();
  if (!needle) return <>{title}</>;
  const parts = title.split(new RegExp(`(${escapeRegExp(needle)})`, "gi"));
  return (
    <>
      {parts.map((part, i) => {
        const isHit = part.toLowerCase() === needle.toLowerCase();
        if (isHit) {
          return (
            <mark key={i} className="bg-accent/25 text-foreground">
              {part}
            </mark>
          );
        }
        return <React.Fragment key={i}>{part}</React.Fragment>;
      })}
    </>
  );
}

const SECTIONS: { type: WikiPageType; label: string; emptyLabel: string }[] = [
  { type: "concept", label: "CONCEPTS", emptyLabel: "concept" },
  { type: "entity", label: "ENTITIES", emptyLabel: "entity" },
  { type: "source_summary", label: "SOURCES", emptyLabel: "source" },
  { type: "output", label: "OUTPUTS", emptyLabel: "output" },
  { type: "index", label: "INDEX", emptyLabel: "index" },
];

function pageTypeIcon(t: WikiPageType) {
  switch (t) {
    case "concept":
      return Brain;
    case "entity":
      return User;
    case "source_summary":
      return FileText;
    case "output":
      return Sparkles;
    case "index":
      return BookMarked;
    default:
      return Brain;
  }
}

export interface WikiNavProps {
  onPageSelect: (page: WikiPage) => void;
  selectedSlug?: string;
  panelRef: React.RefObject<PanelImperativeHandle | null>;
}

/**
 * Live wiki graph from `/api/wiki/pages` for the **ingest/compile** loop; drives inspector selection.
 */
export function WikiNav({ onPageSelect, selectedSlug, panelRef }: WikiNavProps) {
  const { pages, isLoading, error } = useWikiPages();
  const { setIngestOpen } = useWorkspace();
  const [q, setQ] = React.useState("");

  const filtered = React.useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return pages;
    return pages.filter(
      (p) =>
        p.title.toLowerCase().includes(s) ||
        p.slug.toLowerCase().includes(s) ||
        p.page_type.toLowerCase().includes(s),
    );
  }, [pages, q]);

  const byType = React.useMemo(() => {
    const m = new Map<WikiPageType, WikiPage[]>();
    for (const s of SECTIONS) m.set(s.type, []);
    for (const p of filtered) {
      const list = m.get(p.page_type);
      if (list) list.push(p);
    }
    return m;
  }, [filtered]);

  const counts = React.useMemo(() => {
    const m = new Map<WikiPageType, number>();
    for (const s of SECTIONS) m.set(s.type, 0);
    for (const p of pages) {
      const n = m.get(p.page_type);
      if (n != null) m.set(p.page_type, n + 1);
    }
    return m;
  }, [pages]);

  return (
    <div className="flex h-full min-h-0 flex-col border-r border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-2 py-2">
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Wiki</span>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="size-7"
          aria-label="Collapse wiki panel"
          onClick={() => panelRef.current?.collapse()}
        >
          <ChevronLeft className="size-4" />
        </Button>
      </div>
      <div className="p-2">
        <Input
          placeholder="Search…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="font-mono text-xs"
        />
      </div>
      {error && (
        <div className="mx-2 mb-2 rounded-md border border-[var(--accent-red)] bg-[var(--accent-red)]/10 px-2 py-1.5 font-mono text-[10px] text-[var(--accent-red)]">
          {error}
        </div>
      )}
      <div className="min-h-0 flex-1 overflow-y-auto px-1 pb-2">
        {SECTIONS.map((section, idx) => {
          const Icon = pageTypeIcon(section.type);
          const list = byType.get(section.type) ?? [];
          const count = counts.get(section.type) ?? 0;
          return (
            <div
              key={section.type}
              className={cn(idx > 0 && "mt-3 border-t border-border pt-3")}
            >
              <div className="mb-1.5 flex items-center gap-2 px-2 font-mono text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
                <Icon className="size-3 shrink-0" />
                {section.label}
                <span className="rounded border border-border px-1 text-[10px] text-foreground">({count})</span>
              </div>
              {isLoading ? (
                <ul className="space-y-1 px-1">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <li key={i} className="compilore-skeleton h-9 rounded-md border border-border" />
                  ))}
                </ul>
              ) : list.length === 0 ? (
                <p className="px-2 py-2 font-sans text-sm italic text-muted-foreground">
                  No {section.emptyLabel} pages yet
                </p>
              ) : (
                <ul className="space-y-0.5">
                  {list.map((p) => {
                    const RowIcon = pageTypeIcon(p.page_type);
                    const active = selectedSlug === p.slug;
                    return (
                      <li key={p.id || p.slug}>
                        <button
                          type="button"
                          onClick={() => onPageSelect(p)}
                          className={cn(
                            "group flex w-full items-start gap-2 rounded-md border border-transparent px-2 py-1.5 text-left transition-[border-color,background-color] duration-150 ease-out",
                            "hover:bg-surface focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]",
                            active && "border-l-2 border-l-accent bg-surface pl-[6px]",
                            !active && "border-l-2 border-l-transparent",
                          )}
                        >
                          <span
                            className={cn(
                              "mt-1.5 size-1.5 shrink-0 rounded-full",
                              confidenceDotClass(p.confidence),
                            )}
                            title={`confidence ${p.confidence.toFixed(2)}`}
                          />
                          <RowIcon className="mt-1 size-3.5 shrink-0 text-muted-foreground" aria-hidden />
                          <span className="min-w-0 flex-1">
                            <span className="block truncate font-sans text-sm text-foreground">
                              <HighlightTitle title={p.title} query={q} />
                            </span>
                            <span className="mt-0.5 hidden font-mono text-[10px] text-muted-foreground group-hover:block">
                              {p.slug}
                            </span>
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })}
      </div>
      <div className="border-t border-border p-2">
        <Button
          type="button"
          variant="accent"
          className="w-full font-mono text-xs"
          onClick={() => setIngestOpen(true)}
        >
          <Plus className="size-3.5" />
          Ingest
        </Button>
      </div>
    </div>
  );
}
