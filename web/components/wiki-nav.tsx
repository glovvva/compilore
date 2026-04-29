"use client";

import * as React from "react";
import {
  BookMarked,
  Brain,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  FileText,
  Plus,
  Sparkles,
  User,
} from "lucide-react";
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

function getTopic(page: WikiPage): string {
  const fm = page.frontmatter;
  if (fm && typeof fm.topic === "string" && fm.topic) return fm.topic;
  return "General";
}

interface SectionConfig {
  type: WikiPageType;
  label: string;
  emptyLabel: string;
  groupByTopic: boolean;
}

const SECTIONS: SectionConfig[] = [
  { type: "concept", label: "Concepts", emptyLabel: "concept", groupByTopic: true },
  { type: "entity", label: "Entities", emptyLabel: "entity", groupByTopic: true },
  { type: "source_summary", label: "Sources", emptyLabel: "source", groupByTopic: false },
  { type: "output", label: "Outputs", emptyLabel: "output", groupByTopic: false },
];

export interface WikiNavProps {
  onPageSelect: (page: WikiPage) => void;
  selectedSlug?: string;
  onClose: () => void;
}

export function WikiNav({ onPageSelect, selectedSlug, onClose }: WikiNavProps) {
  const { pages, isLoading, error } = useWikiPages();
  const { setIngestOpen } = useWorkspace();
  const [q, setQ] = React.useState("");
  const [openSections, setOpenSections] = React.useState<Record<string, boolean>>(
    () => Object.fromEntries(SECTIONS.map((s) => [s.type, true])),
  );

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

  const toggleSection = (type: string) => {
    setOpenSections((prev) => ({ ...prev, [type]: !prev[type] }));
  };

  return (
    <aside className="fixed left-0 top-10 z-20 flex h-[calc(100dvh-2.5rem)] w-72 flex-col border-r border-border bg-surface">
      <div className="flex h-10 shrink-0 items-center justify-between border-b border-border px-3">
        <span className="font-mono text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
          Wiki
        </span>
        <button
          type="button"
          className="flex size-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-background hover:text-foreground"
          aria-label="Close wiki sidebar"
          onClick={onClose}
        >
          <ChevronLeft className="size-4" />
        </button>
      </div>

      <div className="shrink-0 p-2">
        <Input
          placeholder="Search…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="font-mono text-xs"
        />
      </div>

      {error && (
        <div className="mx-2 mb-2 shrink-0 rounded-md border border-[var(--accent-red)] bg-[var(--accent-red)]/10 px-2 py-1.5 font-mono text-[10px] text-[var(--accent-red)]">
          {error}
        </div>
      )}

      <nav className="min-h-0 flex-1 overflow-y-auto">
        {SECTIONS.map((section) => {
          const Icon = pageTypeIcon(section.type);
          const list = byType.get(section.type) ?? [];
          const isOpen = openSections[section.type] ?? true;

          return (
            <div key={section.type} className="border-b border-border last:border-b-0">
              <button
                type="button"
                onClick={() => toggleSection(section.type)}
                className="flex w-full items-center gap-2 px-3 py-2 font-mono text-[11px] font-medium uppercase tracking-wider text-muted-foreground hover:bg-background"
              >
                {isOpen ? (
                  <ChevronDown className="size-3 shrink-0" />
                ) : (
                  <ChevronRight className="size-3 shrink-0" />
                )}
                <Icon className="size-3 shrink-0" />
                <span className="shrink-0">{section.label}</span>
                <span className="ml-auto shrink-0 rounded border border-border px-1 text-[10px] text-foreground">
                  {list.length}
                </span>
              </button>

              {isOpen && (
                <div className="pb-1">
                  {isLoading ? (
                    <div className="space-y-1 px-3 pb-2">
                      {Array.from({ length: 3 }).map((_, i) => (
                        <div
                          key={i}
                          className="compilore-skeleton h-8 rounded-md border border-border"
                        />
                      ))}
                    </div>
                  ) : list.length === 0 ? (
                    <p className="px-3 pb-2 font-sans text-sm italic text-muted-foreground">
                      No {section.emptyLabel} pages yet
                    </p>
                  ) : section.groupByTopic ? (
                    <TopicGroupedList
                      pages={list}
                      selectedSlug={selectedSlug}
                      q={q}
                      onPageSelect={onPageSelect}
                    />
                  ) : (
                    <FlatPageList
                      pages={list}
                      selectedSlug={selectedSlug}
                      q={q}
                      onPageSelect={onPageSelect}
                    />
                  )}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      <div className="shrink-0 border-t border-border p-2">
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
    </aside>
  );
}

function TopicGroupedList({
  pages,
  selectedSlug,
  q,
  onPageSelect,
}: {
  pages: WikiPage[];
  selectedSlug?: string;
  q: string;
  onPageSelect: (page: WikiPage) => void;
}) {
  const groups = React.useMemo(() => {
    const m = new Map<string, WikiPage[]>();
    for (const p of pages) {
      const topic = getTopic(p);
      if (!m.has(topic)) m.set(topic, []);
      m.get(topic)!.push(p);
    }
    return [...m.entries()].sort(([a], [b]) => {
      if (a === "General") return 1;
      if (b === "General") return -1;
      return a.localeCompare(b);
    });
  }, [pages]);

  const [openTopics, setOpenTopics] = React.useState<Record<string, boolean>>({});
  const toggle = (topic: string) =>
    setOpenTopics((prev) => ({ ...prev, [topic]: !(prev[topic] ?? true) }));

  if (groups.length === 1) {
    return (
      <FlatPageList
        pages={groups[0]![1]}
        selectedSlug={selectedSlug}
        q={q}
        onPageSelect={onPageSelect}
      />
    );
  }

  return (
    <>
      {groups.map(([topic, topicPages]) => {
        const isOpen = openTopics[topic] ?? true;
        return (
          <div key={topic}>
            <button
              type="button"
              onClick={() => toggle(topic)}
              className="flex w-full items-center gap-1.5 px-4 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground/60 hover:text-muted-foreground"
            >
              {isOpen ? (
                <ChevronDown className="size-2.5 shrink-0" />
              ) : (
                <ChevronRight className="size-2.5 shrink-0" />
              )}
              <span className="shrink-0">{topic}</span>
            </button>
            {isOpen && (
              <FlatPageList
                pages={topicPages}
                selectedSlug={selectedSlug}
                q={q}
                onPageSelect={onPageSelect}
              />
            )}
          </div>
        );
      })}
    </>
  );
}

function FlatPageList({
  pages,
  selectedSlug,
  q,
  onPageSelect,
}: {
  pages: WikiPage[];
  selectedSlug?: string;
  q: string;
  onPageSelect: (page: WikiPage) => void;
}) {
  return (
    <ul className="space-y-0.5 px-2">
      {pages.map((p) => {
        const Icon = pageTypeIcon(p.page_type);
        const active = selectedSlug === p.slug;
        return (
          <li key={p.id || p.slug}>
            <button
              type="button"
              onClick={() => onPageSelect(p)}
              className={cn(
                "group flex w-full items-start gap-2 rounded-md border border-transparent px-2 py-1.5 text-left transition-[border-color,background-color] duration-150 ease-out",
                "hover:bg-background focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]",
                active && "border-l-2 border-l-accent bg-background pl-[6px]",
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
              <Icon className="mt-1 size-3.5 shrink-0 text-muted-foreground" aria-hidden />
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
  );
}
