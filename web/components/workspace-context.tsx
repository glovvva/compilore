"use client";

import * as React from "react";
import type { MockQueryResponse } from "@/lib/mock-data";
import { MOCK_WIKI_STATS } from "@/lib/mock-data";
import type { WikiPage } from "@/lib/types/wiki";
import { useWikiPages } from "@/hooks/use-wiki-pages";
import { unwrapApiData } from "@/lib/api-envelope";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export interface CompileLogLine {
  id: string;
  label: string;
  status: "pending" | "done";
  durationMs?: number;
  costFragment?: string;
  gitHash?: string;
}

const COMPILORE_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

interface QueryResponseCardJson {
  format?: string;
  headline?: string;
  body?: string;
  source_chips?: { title: string; slug: string; page_type: string }[];
  confidence?: number;
  gatekeeper_passed?: boolean;
  gatekeeper_reasoning?: string;
  cost_usd?: number;
}

function mapQueryCardToMock(data: QueryResponseCardJson): MockQueryResponse {
  const headline = (data.headline ?? "").trim();
  const body = (data.body ?? "").trim();
  const bodyMarkdown =
    headline && body ? `## ${headline}\n\n${body}` : body || headline || "_Empty response_";
  const chips = data.source_chips ?? [];
  return {
    queryType: "synthesis",
    confidence: typeof data.confidence === "number" ? data.confidence : 0,
    costUsd: typeof data.cost_usd === "number" ? data.cost_usd : 0,
    bodyMarkdown,
    sourceSlugs: chips.map((c) => c.slug).filter(Boolean),
    gatekeeper: data.gatekeeper_passed ? "saved" : "discarded",
    gatekeeperDetail: (data.gatekeeper_reasoning ?? "").trim() || undefined,
  };
}

interface WorkspaceContextValue {
  stats: typeof MOCK_WIKI_STATS;
  wikiPages: WikiPage[];
  wikiLoading: boolean;
  wikiError: string | null;
  mutateWikiPages: () => void;
  /** Resolved for API calls: session metadata or first wiki page's tenant from detail API. */
  tenantId: string | null;
  selectedWikiPage: WikiPage | null;
  setSelectedWikiPage: (page: WikiPage | null) => void;
  selectWikiPage: (page: WikiPage) => void;
  openPageBySlug: (slug: string) => void;
  openSourceBySlug: (slug: string) => void;
  inspectorSourceCitation: boolean;
  queryInputRef: React.RefObject<HTMLTextAreaElement | null>;
  focusQueryInput: () => void;
  queryText: string;
  setQueryText: (v: string) => void;
  lastResponse: MockQueryResponse | null;
  queryLoading: boolean;
  submitWikiQuery: () => Promise<void>;
  ingestOpen: boolean;
  setIngestOpen: (v: boolean) => void;
  statsModalOpen: boolean;
  setStatsModalOpen: (v: boolean) => void;
  pasteModalOpen: boolean;
  setPasteModalOpen: (v: boolean) => void;
  lintConfirmOpen: boolean;
  setLintConfirmOpen: (v: boolean) => void;
  runMockLint: () => void;
  compileLogOpen: boolean;
  setCompileLogOpen: (v: boolean) => void;
  compileLines: CompileLogLine[];
  startMockIngest: () => void;
  persistentError: string | null;
  setPersistentError: (v: string | null) => void;
  commandOpen: boolean;
  setCommandOpen: (v: boolean) => void;
}

const WorkspaceContext = React.createContext<WorkspaceContextValue | null>(null);

function placeholderWikiPage(slug: string): WikiPage {
  return {
    id: "",
    slug,
    title: slug,
    page_type: "source_summary",
    confidence: 0,
    updated_at: new Date().toISOString(),
    related: [],
  };
}

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { pages: wikiPages, isLoading: wikiLoading, error: wikiError, mutate } = useWikiPages();
  const [tenantId, setTenantId] = React.useState<string | null>(null);
  const [selectedWikiPage, setSelectedWikiPage] = React.useState<WikiPage | null>(null);
  const [inspectorSourceCitation, setInspectorSourceCitation] = React.useState(false);

  const queryInputRef = React.useRef<HTMLTextAreaElement | null>(null);
  const [queryText, setQueryText] = React.useState("");
  const [lastResponse, setLastResponse] = React.useState<MockQueryResponse | null>(null);
  const [queryLoading, setQueryLoading] = React.useState(false);
  const [ingestOpen, setIngestOpen] = React.useState(false);
  const [statsModalOpen, setStatsModalOpen] = React.useState(false);
  const [pasteModalOpen, setPasteModalOpen] = React.useState(false);
  const [lintConfirmOpen, setLintConfirmOpen] = React.useState(false);
  const [compileLogOpen, setCompileLogOpen] = React.useState(false);
  const [compileLines, setCompileLines] = React.useState<CompileLogLine[]>([]);
  const [persistentError, setPersistentError] = React.useState<string | null>(null);
  const [commandOpen, setCommandOpen] = React.useState(false);

  const mutateWikiPages = React.useCallback(() => {
    void mutate();
  }, [mutate]);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const supabase = createSupabaseBrowserClient();
        const { data: { user } } = await supabase.auth.getUser();
        const um = user?.user_metadata as { tenant_id?: string } | undefined;
        const am = user?.app_metadata as { tenant_id?: string } | undefined;
        if (um?.tenant_id) {
          if (!cancelled) setTenantId(um.tenant_id);
          return;
        }
        if (am?.tenant_id) {
          if (!cancelled) setTenantId(am.tenant_id);
          return;
        }
        const first = wikiPages[0];
        if (first?.slug) {
          const r = await fetch(`/api/wiki/pages/${encodeURIComponent(first.slug)}`, {
            credentials: "include",
          });
          if (r.ok) {
            const j = (await r.json()) as { page?: { tenant_id?: string } };
            if (!cancelled) setTenantId(j.page?.tenant_id ?? null);
          }
        }
      } catch {
        if (!cancelled) setTenantId(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [wikiPages]);

  const selectWikiPage = React.useCallback((page: WikiPage) => {
    setSelectedWikiPage(page);
    setInspectorSourceCitation(false);
  }, []);

  const openPageBySlug = React.useCallback(
    (slug: string) => {
      const p = wikiPages.find((x) => x.slug === slug);
      setSelectedWikiPage(p ?? placeholderWikiPage(slug));
      setInspectorSourceCitation(false);
    },
    [wikiPages],
  );

  const openSourceBySlug = React.useCallback(
    (slug: string) => {
      const p = wikiPages.find((x) => x.slug === slug);
      setSelectedWikiPage(p ?? placeholderWikiPage(slug));
      setInspectorSourceCitation(true);
    },
    [wikiPages],
  );

  const focusQueryInput = React.useCallback(() => {
    queryInputRef.current?.focus();
  }, []);

  const submitWikiQuery = React.useCallback(async () => {
    const q = queryText.trim();
    if (!q) return;
    setQueryLoading(true);
    setPersistentError(null);
    try {
      const res = await fetch(`${COMPILORE_API_BASE}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const raw = await res.json().catch(() => ({}));
      if (!res.ok) {
        let detail = res.statusText;
        if (typeof raw === "object" && raw !== null && "detail" in raw) {
          const d = (raw as { detail: unknown }).detail;
          if (typeof d === "string") detail = d;
          else if (Array.isArray(d)) detail = JSON.stringify(d);
          else if (d != null) detail = String(d);
        }
        setPersistentError(detail || `Query failed (${res.status})`);
        return;
      }
      const card = unwrapApiData<QueryResponseCardJson>(raw);
      const data = mapQueryCardToMock(card);
      setLastResponse(data);
      if (card.gatekeeper_passed) {
        mutateWikiPages();
      }
    } catch (e) {
      setPersistentError(e instanceof Error ? e.message : "Query request failed");
    } finally {
      setQueryLoading(false);
    }
  }, [queryText, mutateWikiPages]);

  const runMockLint = React.useCallback(() => {
    setLintConfirmOpen(false);
    setPersistentError(
      "Lint (mock): 2 orphan wikilinks detected in `concepts/`. Fix before next compile.",
    );
  }, []);

  const startMockIngest = React.useCallback(() => {
    setIngestOpen(false);
    setCompileLogOpen(true);
    const steps: CompileLogLine[] = [
      { id: "s1", label: "Fetch URL / normalize markdown", status: "pending" },
      { id: "s2", label: "Compile with Claude (Sonnet)", status: "pending" },
      { id: "s3", label: "Embed chunks + Supabase upsert", status: "pending" },
      { id: "s4", label: "Write wiki files + git commit", status: "pending" },
    ];
    setCompileLines(steps);
    let i = 0;
    const run = () => {
      if (i >= steps.length) return;
      const cur = steps[i]!;
      window.setTimeout(() => {
        setCompileLines((prev) =>
          prev.map((l) => {
            if (l.id !== cur.id) return l;
            return {
              ...l,
              status: "done",
              durationMs: 280 + i * 90,
              costFragment: cur.id === "s2" ? "$0.041" : undefined,
              gitHash: cur.id === "s4" ? "abc123f" : undefined,
            };
          }),
        );
        i += 1;
        run();
      }, 520);
    };
    run();
  }, []);

  const value = React.useMemo<WorkspaceContextValue>(
    () => ({
      stats: MOCK_WIKI_STATS,
      wikiPages,
      wikiLoading,
      wikiError,
      mutateWikiPages,
      tenantId,
      selectedWikiPage,
      setSelectedWikiPage,
      selectWikiPage,
      openPageBySlug,
      openSourceBySlug,
      inspectorSourceCitation,
      queryInputRef,
      focusQueryInput,
      queryText,
      setQueryText,
      lastResponse,
      queryLoading,
      submitWikiQuery,
      ingestOpen,
      setIngestOpen,
      statsModalOpen,
      setStatsModalOpen,
      pasteModalOpen,
      setPasteModalOpen,
      lintConfirmOpen,
      setLintConfirmOpen,
      runMockLint,
      compileLogOpen,
      setCompileLogOpen,
      compileLines,
      startMockIngest,
      persistentError,
      setPersistentError,
      commandOpen,
      setCommandOpen,
    }),
    [
      wikiPages,
      wikiLoading,
      wikiError,
      mutateWikiPages,
      tenantId,
      selectedWikiPage,
      selectWikiPage,
      openPageBySlug,
      openSourceBySlug,
      inspectorSourceCitation,
      queryText,
      lastResponse,
      queryLoading,
      submitWikiQuery,
      ingestOpen,
      statsModalOpen,
      pasteModalOpen,
      lintConfirmOpen,
      runMockLint,
      compileLogOpen,
      compileLines,
      startMockIngest,
      persistentError,
      commandOpen,
      focusQueryInput,
    ],
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspace() {
  const ctx = React.useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider");
  return ctx;
}
