"use client";

import * as React from "react";
import {
  BookMarked,
  Brain,
  FileText,
  Sparkles,
  User,
} from "lucide-react";
import { ResponseCard } from "@/components/response-card";
import { CompileLog } from "@/components/compile-log";
import { useWorkspace } from "@/components/workspace-context";
import { cn } from "@/lib/utils";
import { buildApiQueryForSubmission } from "@/lib/query-submit-hint";
import type { WikiPage, WikiPageType } from "@/lib/types/wiki";
import { confidenceDotClass } from "@/lib/wiki/confidence-dot";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const COMPILORE_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const PAGE_GROUPS: { type: WikiPageType; label: string }[] = [
  { type: "concept", label: "Concepts" },
  { type: "entity", label: "Entities" },
  { type: "source_summary", label: "Sources" },
  { type: "output", label: "Outputs" },
  { type: "index", label: "Index" },
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

function QueryLoadingIndicator() {
  return (
    <div className="flex items-center gap-2 px-1 py-3">
      <span className="inline-flex gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--color-accent)]"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </span>
      <span className="font-mono text-xs text-muted-foreground">Searching wiki · synthesizing answer...</span>
    </div>
  );
}

export interface QueryPanelProps {
  children?: React.ReactNode;
}

/**
 * Center column: **query** loop entry (natural language) and empty-state health for the
 * **compile** loop. Renders optional route `children` below the response stream.
 */
const ALLOWED_UPLOAD_EXT = new Set([".md", ".txt", ".pdf"]);

/** Absolute times from ingest start: step 2 @1.5s, step 3 @3s, then 4.5s, 6s, 7.5s. */
const INGEST_STEP_ADVANCE_MS = [1500, 3000, 4500, 6000, 7500] as const;

type IngestRunMode = "url" | "paste" | "file";

type IngestProgressState = {
  mode: IngestRunMode;
  labels: string[];
  completedCount: number;
  summaryLine: string | null;
  errorLine: string | null;
  /** Shown below the error line (e.g. switch to paste for blocked social URLs). */
  errorCta?: "switch_to_paste" | null;
};

function parseIngestErrorDetail(raw: unknown): string | null {
  if (typeof raw !== "object" || raw === null) return null;
  const o = raw as Record<string, unknown>;
  if ("detail" in o) {
    const d = o.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      const parts = d.map((item) => {
        if (typeof item === "object" && item !== null && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return typeof item === "string" ? item : JSON.stringify(item);
      });
      return parts.join("; ");
    }
    if (d != null) return typeof d === "string" ? d : JSON.stringify(d);
  }
  if (typeof o.message === "string") return o.message;
  if (typeof o.error === "string") return o.error;
  return null;
}

function ingestHttpErrorMessage(res: Response, raw: unknown): string {
  const parsed = parseIngestErrorDetail(raw);
  if (parsed) return parsed;
  if (res.status === 422) return "Invalid request — check the URL format";
  if (res.status === 500) return "Backend error — check terminal for details";
  return `Unknown error (status ${res.status})`;
}

const INGEST_NETWORK_ERROR = "Could not reach backend (is it running on :8001?)";

function validateIngestUrl(url: string): string | null {
  const t = url.trim();
  if (!t.startsWith("http://") && !t.startsWith("https://")) {
    return "URL must start with http:// or https://";
  }
  try {
    new URL(t);
    return null;
  } catch {
    return "Invalid URL";
  }
}

/** Domains that block scraping; skip fetch and show an immediate message. */
function blockedIngestUrlAction(url: string): { message: string; cta: "switch_to_paste" | null } | null {
  let parsed: URL;
  try {
    parsed = new URL(url.trim());
  } catch {
    return null;
  }
  const host = parsed.hostname.replace(/^www\./i, "").toLowerCase();
  if (host === "linkedin.com" || host.endsWith(".linkedin.com")) {
    return {
      message: "LinkedIn blocks scraping — paste the post text instead",
      cta: "switch_to_paste",
    };
  }
  if (host === "instagram.com" || host.endsWith(".instagram.com")) {
    return {
      message: "Instagram blocks scraping — use SociaVault adapter (coming soon)",
      cta: null,
    };
  }
  if (host === "twitter.com" || host === "x.com" || host.endsWith(".twitter.com")) {
    return {
      message: "X/Twitter blocks scraping — paste the text instead",
      cta: "switch_to_paste",
    };
  }
  return null;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function ingestStepLabels(mode: IngestRunMode): string[] {
  const first =
    mode === "url"
      ? "Fetching content..."
      : mode === "paste"
        ? "Reading text..."
        : "Reading file...";
  return [
    first,
    "Extracting chunks...",
    "Generating wiki pages...",
    "Storing to Supabase...",
    "Committing to git...",
  ];
}

function parseWikiPagesFromIngestResponse(raw: unknown): WikiPage[] | "queued" | null {
  if (typeof raw !== "object" || raw === null) return null;
  const o = raw as Record<string, unknown>;
  const data = o.data;
  if (Array.isArray(data)) {
    const out: WikiPage[] = [];
    for (const row of data) {
      if (typeof row !== "object" || row === null) continue;
      const r = row as Record<string, unknown>;
      const page_type = r.page_type as WikiPageType | undefined;
      if (
        page_type === "concept" ||
        page_type === "entity" ||
        page_type === "source_summary" ||
        page_type === "output" ||
        page_type === "index"
      ) {
        out.push({
          id: String(r.id ?? ""),
          slug: String(r.slug ?? ""),
          title: String(r.title ?? ""),
          page_type,
          confidence: typeof r.confidence === "number" ? r.confidence : 0,
          updated_at: String(r.updated_at ?? ""),
          related: Array.isArray(r.related) ? (r.related as string[]) : [],
        });
      }
    }
    return out;
  }
  if (typeof data === "object" && data !== null) {
    const st = (data as Record<string, unknown>).status;
    if (st === "queued") return "queued";
  }
  return null;
}

function formatIngestPageSummary(pages: WikiPage[]): string {
  const n = pages.length;
  const concept = pages.filter((p) => p.page_type === "concept").length;
  const entity = pages.filter((p) => p.page_type === "entity").length;
  const source = pages.filter((p) => p.page_type === "source_summary").length;
  const parts: string[] = [`${n} pages`];
  if (concept) parts.push(`${concept} concept`);
  if (entity) parts.push(`${entity} entity`);
  if (source) parts.push(`${source} source`);
  return `✓ Done — ${parts.join(" · ")}`;
}

function IngestCompileProgress({
  progress,
  onDismiss,
  onSwitchToPaste,
  onDismissSuccess,
}: {
  progress: IngestProgressState;
  onDismiss: () => void;
  onSwitchToPaste: () => void;
  /** Clears success log, runs wiki refresh; form already reset when summary appeared. */
  onDismissSuccess?: () => void;
}) {
  const hasError = progress.errorLine != null;
  const numVisible =
    progress.summaryLine != null ? 5 : Math.min(progress.completedCount + 1, 5);
  const failureRowIndex =
    hasError && numVisible > 0 ? Math.min(progress.completedCount, numVisible - 1) : -1;

  return (
    <div
      className="mt-2 rounded-md border border-border bg-surface/50 p-3 font-mono leading-relaxed"
      aria-live="polite"
    >
      {progress.labels.slice(0, numVisible).map((label, i) => {
        const stepDone =
          (!hasError && (progress.summaryLine != null || i < progress.completedCount)) ||
          (hasError && failureRowIndex >= 0 && i < failureRowIndex);
        const stepFailed = hasError && failureRowIndex >= 0 && i === failureRowIndex;
        const active =
          !hasError &&
          !progress.summaryLine &&
          i === progress.completedCount &&
          progress.completedCount < 5;
        return (
          <div
            key={i}
            className="compilore-log-line mb-2 flex flex-wrap items-baseline gap-x-2 text-xs animate-slide-in last:mb-0"
          >
            <span className="inline-flex w-4 shrink-0 justify-center" aria-hidden>
              {stepDone ? (
                <span className="text-[var(--accent-green)]">✓</span>
              ) : stepFailed ? (
                <span className="text-[var(--color-red)]">✗</span>
              ) : (
                <span className={cn("text-indigo-500", active && "animate-pulse")}>●</span>
              )}
            </span>
            <span className="text-muted-foreground">{label}</span>
          </div>
        );
      })}
      {progress.summaryLine ? (
        <div className="mt-2 flex flex-wrap items-center border-t border-border pt-2 font-mono text-xs text-[var(--accent-green)] animate-slide-in">
          <span>{progress.summaryLine}</span>
          {onDismissSuccess ? (
            <button
              type="button"
              onClick={onDismissSuccess}
              className="ml-3 font-mono text-xs text-[var(--color-muted)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
            >
              dismiss ×
            </button>
          ) : null}
        </div>
      ) : null}
      {progress.errorLine ? (
        <div className="mt-2 space-y-2 border-t border-border pt-2" role="alert">
          <div className="flex items-start justify-between gap-2">
            <p className="min-w-0 flex-1 font-mono text-xs text-[var(--color-red)]">
              ✗ Failed — {progress.errorLine}
            </p>
            <button
              type="button"
              onClick={onDismiss}
              className="shrink-0 rounded border border-border px-1.5 py-0.5 font-mono text-xs text-muted-foreground transition-colors hover:border-[var(--color-red)] hover:text-[var(--color-red)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
              aria-label="Dismiss"
            >
              ×
            </button>
          </div>
          {progress.errorCta === "switch_to_paste" ? (
            <button
              type="button"
              onClick={onSwitchToPaste}
              className="rounded-md border border-border bg-background px-2 py-1 font-mono text-xs text-foreground transition-colors hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
            >
              Switch to Paste text →
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

export function QueryPanel({ children }: QueryPanelProps) {
  const [submittedQuery, setSubmittedQuery] = React.useState("");
  const [ingestMode, setIngestMode] = React.useState<null | "url" | "paste" | "file">(null);
  const [urlDraft, setUrlDraft] = React.useState("");
  const [pasteDraft, setPasteDraft] = React.useState("");
  const [urlHint, setUrlHint] = React.useState("");
  const [pasteHint, setPasteHint] = React.useState("");
  const [fileHint, setFileHint] = React.useState("");
  const [urlBusy, setUrlBusy] = React.useState(false);
  const [pasteBusy, setPasteBusy] = React.useState(false);
  const [fileBusy, setFileBusy] = React.useState(false);
  const [ingestProgress, setIngestProgress] = React.useState<IngestProgressState | null>(null);
  const [filePickLabel, setFilePickLabel] = React.useState<string | null>(null);
  const [ingestError, setIngestError] = React.useState<string | null>(null);
  const [pagesDialogOpen, setPagesDialogOpen] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const ingestTimeoutsRef = React.useRef<number[]>([]);
  const ingestSuccessHideTimeoutRef = React.useRef<number | null>(null);

  const clearIngestTimers = React.useCallback(() => {
    ingestTimeoutsRef.current.forEach((id) => window.clearTimeout(id));
    ingestTimeoutsRef.current = [];
  }, []);

  const clearIngestSuccessHideTimeout = React.useCallback(() => {
    if (ingestSuccessHideTimeoutRef.current != null) {
      window.clearTimeout(ingestSuccessHideTimeoutRef.current);
      ingestSuccessHideTimeoutRef.current = null;
    }
  }, []);

  const startIngestStepTimers = React.useCallback(() => {
    clearIngestTimers();
    INGEST_STEP_ADVANCE_MS.forEach((delay, idx) => {
      const target = idx + 1;
      const id = window.setTimeout(() => {
        setIngestProgress((p) =>
          p ? { ...p, completedCount: Math.max(p.completedCount, target) } : null,
        );
      }, delay);
      ingestTimeoutsRef.current.push(id);
    });
  }, [clearIngestTimers]);

  React.useEffect(
    () => () => {
      clearIngestTimers();
      clearIngestSuccessHideTimeout();
    },
    [clearIngestTimers, clearIngestSuccessHideTimeout],
  );

  const {
    stats,
    wikiPages,
    queryInputRef,
    queryText,
    setQueryText,
    submitWikiQuery,
    queryLoading,
    lastResponse,
    openSourceBySlug,
    compileLogOpen,
    persistentError,
    mutateWikiPages,
    tenantId,
    selectWikiPage,
    openPageBySlug,
  } = useWorkspace();

  const runQuerySubmit = React.useCallback(() => {
    const trimmed = queryText.trim();
    if (!trimmed || queryLoading) return;
    setSubmittedQuery(trimmed);
    buildApiQueryForSubmission(trimmed);
    void submitWikiQuery();
  }, [queryText, queryLoading, submitWikiQuery]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Enter" || e.shiftKey || queryLoading) return;
    const trimmed = queryText.trim();
    if (!trimmed) return;
    e.preventDefault();
    runQuerySubmit();
  };

  React.useEffect(() => {
    if (!lastResponse?.sourceSlugs?.length) return;
    openPageBySlug(lastResponse.sourceSlugs[0]!);
  }, [lastResponse, openPageBySlug]);

  const lastCompile = React.useMemo(() => {
    try {
      return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(new Date(stats.lastCompileAt));
    } catch {
      return stats.lastCompileAt;
    }
  }, [stats.lastCompileAt]);

  const pagesByType = React.useMemo(() => {
    const m = new Map<WikiPageType, WikiPage[]>();
    for (const g of PAGE_GROUPS) m.set(g.type, []);
    for (const p of wikiPages) {
      const list = m.get(p.page_type);
      if (list) list.push(p);
    }
    return m;
  }, [wikiPages]);

  const summarizeIngestResponse = React.useCallback((raw: unknown): string => {
    const parsed = parseWikiPagesFromIngestResponse(raw);
    if (parsed === "queued") {
      return "✓ Done — compile queued · refresh wiki in ~30s";
    }
    if (Array.isArray(parsed)) {
      return parsed.length ? formatIngestPageSummary(parsed) : "✓ Done — 0 pages";
    }
    return "✓ Done — wiki updated";
  }, []);

  const dismissIngestSuccessComplete = React.useCallback(() => {
    clearIngestSuccessHideTimeout();
    setIngestProgress(null);
    setUrlBusy(false);
    setPasteBusy(false);
    setFileBusy(false);
    mutateWikiPages();
  }, [clearIngestSuccessHideTimeout, mutateWikiPages]);

  const finalizeIngestSuccess = React.useCallback(
    (summary: string, reset: () => void) => {
      clearIngestTimers();
      clearIngestSuccessHideTimeout();
      reset();
      setIngestProgress((p) =>
        p ? { ...p, completedCount: 5, summaryLine: summary, errorLine: null, errorCta: null } : null,
      );
      ingestSuccessHideTimeoutRef.current = window.setTimeout(() => {
        ingestSuccessHideTimeoutRef.current = null;
        setIngestProgress(null);
        mutateWikiPages();
      }, 8000);
    },
    [clearIngestTimers, clearIngestSuccessHideTimeout, mutateWikiPages],
  );

  const finalizeIngestError = React.useCallback(
    (msg: string, cta?: "switch_to_paste" | null) => {
      clearIngestTimers();
      setIngestProgress((p) =>
        p
          ? {
              ...p,
              errorLine: msg,
              errorCta: cta === undefined ? null : cta,
            }
          : null,
      );
    },
    [clearIngestTimers],
  );

  const dismissIngestProgress = React.useCallback(() => {
    clearIngestTimers();
    clearIngestSuccessHideTimeout();
    setIngestProgress(null);
    setUrlBusy(false);
    setPasteBusy(false);
    setFileBusy(false);
  }, [clearIngestTimers, clearIngestSuccessHideTimeout]);

  const switchIngestToPaste = React.useCallback(() => {
    dismissIngestProgress();
    setIngestMode("paste");
  }, [dismissIngestProgress]);

  const runUrlIngest = React.useCallback(async () => {
    const url = urlDraft.trim();
    if (!url) return;
    setIngestError(null);
    const hint = urlHint.trim();
    const labels = ingestStepLabels("url");

    const urlValidationError = validateIngestUrl(url);
    if (urlValidationError) {
      setIngestProgress({
        mode: "url",
        labels,
        completedCount: 0,
        summaryLine: null,
        errorLine: urlValidationError,
        errorCta: null,
      });
      return;
    }

    const blocked = blockedIngestUrlAction(url);
    if (blocked) {
      setIngestProgress({
        mode: "url",
        labels,
        completedCount: 0,
        summaryLine: null,
        errorLine: blocked.message,
        errorCta: blocked.cta ?? null,
      });
      return;
    }

    setIngestProgress({
      mode: "url",
      labels,
      completedCount: 0,
      summaryLine: null,
      errorLine: null,
      errorCta: null,
    });
    startIngestStepTimers();
    setUrlBusy(true);
    try {
      const body: { url: string; tenant_id?: string; hint?: string } = { url };
      if (tenantId) body.tenant_id = tenantId;
      if (hint) body.hint = hint;
      const res = await fetch(`${COMPILORE_API_BASE}/ingest/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const raw = await res.json().catch(() => ({}));
      if (!res.ok) {
        finalizeIngestError(ingestHttpErrorMessage(res, raw), null);
        return;
      }
      finalizeIngestSuccess(summarizeIngestResponse(raw), () => {
        setUrlDraft("");
        setUrlHint("");
        setIngestMode(null);
      });
    } catch {
      finalizeIngestError(INGEST_NETWORK_ERROR, null);
    } finally {
      setUrlBusy(false);
    }
  }, [
    urlDraft,
    urlHint,
    tenantId,
    startIngestStepTimers,
    finalizeIngestSuccess,
    finalizeIngestError,
    summarizeIngestResponse,
  ]);

  const runPasteIngest = React.useCallback(async () => {
    const text = pasteDraft.trim();
    if (!text) return;
    setIngestError(null);
    const hint = pasteHint.trim();
    const labels = ingestStepLabels("paste");
    setIngestProgress({
      mode: "paste",
      labels,
      completedCount: 0,
      summaryLine: null,
      errorLine: null,
    });
    startIngestStepTimers();
    setPasteBusy(true);
    try {
      const body: { content: string; tenant_id?: string; hint?: string } = { content: text };
      if (tenantId) body.tenant_id = tenantId;
      if (hint) body.hint = hint;
      const res = await fetch(`${COMPILORE_API_BASE}/ingest/paste`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const raw = await res.json().catch(() => ({}));
      if (!res.ok) {
        finalizeIngestError(ingestHttpErrorMessage(res, raw), null);
        return;
      }
      finalizeIngestSuccess(summarizeIngestResponse(raw), () => {
        setPasteDraft("");
        setPasteHint("");
        setIngestMode(null);
      });
    } catch {
      finalizeIngestError(INGEST_NETWORK_ERROR, null);
    } finally {
      setPasteBusy(false);
    }
  }, [
    pasteDraft,
    pasteHint,
    tenantId,
    startIngestStepTimers,
    finalizeIngestSuccess,
    finalizeIngestError,
    summarizeIngestResponse,
  ]);

  const runFileIngest = React.useCallback(
    async (file: File) => {
      const lower = file.name.toLowerCase();
      const dot = lower.lastIndexOf(".");
      const ext = dot >= 0 ? lower.slice(dot) : "";
      if (!ALLOWED_UPLOAD_EXT.has(ext)) {
        setIngestError("Supported uploads: .md, .txt, .pdf");
        return;
      }
      setIngestError(null);
      const hint = fileHint.trim();
      const labels = ingestStepLabels("file");
      setIngestProgress({
        mode: "file",
        labels,
        completedCount: 0,
        summaryLine: null,
        errorLine: null,
      });
      startIngestStepTimers();
      setFileBusy(true);
      setFilePickLabel(`${file.name} · ${formatFileSize(file.size)}`);
      try {
        const fd = new FormData();
        fd.append("file", file, file.name);
        if (hint) fd.append("hint", hint);
        const res = await fetch(`${COMPILORE_API_BASE}/ingest`, {
          method: "POST",
          body: fd,
        });
        const raw = await res.json().catch(() => ({}));
        if (!res.ok) {
          finalizeIngestError(ingestHttpErrorMessage(res, raw), null);
          return;
        }
        finalizeIngestSuccess(summarizeIngestResponse(raw), () => {
          setIngestMode(null);
          setFilePickLabel(null);
          setFileHint("");
          if (fileInputRef.current) fileInputRef.current.value = "";
        });
      } catch {
        finalizeIngestError(INGEST_NETWORK_ERROR, null);
      } finally {
        setFileBusy(false);
      }
    },
    [
      fileHint,
      startIngestStepTimers,
      finalizeIngestSuccess,
      finalizeIngestError,
      summarizeIngestResponse,
    ],
  );

  const onFileInputChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) void runFileIngest(f);
    },
    [runFileIngest],
  );

  const onFileDrop = React.useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const f = e.dataTransfer.files?.[0];
      if (f) void runFileIngest(f);
    },
    [runFileIngest],
  );

  return (
    <div className="flex h-full min-h-0 flex-col bg-background">
      <div className="border-b border-border p-3">
        <label className="sr-only" htmlFor="compilore-query">
          Query
        </label>
        <div
          className={cn(
            "flex items-end gap-2 rounded-md border border-border bg-surface px-3 py-2 transition-[border-color] duration-200 ease-out",
            "focus-within:border-accent focus-within:outline focus-within:outline-2 focus-within:outline-offset-0 focus-within:outline-[var(--accent)]",
            queryLoading && "pointer-events-none opacity-50",
          )}
        >
          <span className="select-none pb-2 font-mono text-accent" aria-hidden>
            [
          </span>
          <textarea
            id="compilore-query"
            ref={queryInputRef}
            rows={2}
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask anything about your wiki..."
            className="min-h-[52px] w-full resize-none border-0 bg-transparent font-sans text-sm text-foreground outline-none placeholder:text-muted-foreground"
          />
          <span className="hidden max-w-[8rem] shrink-0 pb-2 text-right font-mono text-[10px] leading-tight text-muted-foreground sm:inline">
            ↵ to send · ⇧↵ new line
          </span>
        </div>
      </div>

      <div className="border-b border-border px-3 py-3">
        <p className="mb-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Ingest</p>
        <div className="flex flex-col gap-2 md:flex-row md:flex-wrap">
          <button
            type="button"
            onClick={() => {
              setIngestMode((m) => (m === "url" ? null : "url"));
              setIngestError(null);
            }}
            className={cn(
              "min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm font-mono text-foreground transition-colors md:min-h-0 md:w-auto md:py-2",
              ingestMode === "url" && "border-accent ring-1 ring-[var(--accent)]",
            )}
          >
            Ingest URL
          </button>
          <button
            type="button"
            onClick={() => {
              setIngestMode((m) => (m === "paste" ? null : "paste"));
              setIngestError(null);
            }}
            className={cn(
              "min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm font-mono text-foreground transition-colors md:min-h-0 md:w-auto md:py-2",
              ingestMode === "paste" && "border-accent ring-1 ring-[var(--accent)]",
            )}
          >
            Paste text
          </button>
          <button
            type="button"
            onClick={() => {
              setIngestError(null);
              setIngestMode((m) => {
                if (m === "file") {
                  setFilePickLabel(null);
                  setIngestProgress(null);
                  clearIngestTimers();
                  return null;
                }
                return "file";
              });
            }}
            className={cn(
              "min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm font-mono text-foreground transition-colors md:min-h-0 md:w-auto md:py-2",
              ingestMode === "file" && "border-accent ring-1 ring-[var(--accent)]",
            )}
          >
            Upload file
          </button>
        </div>
        {ingestProgress?.summaryLine ? (
          <div className="mt-3">
            <IngestCompileProgress
              progress={ingestProgress}
              onDismiss={dismissIngestProgress}
              onSwitchToPaste={switchIngestToPaste}
              onDismissSuccess={dismissIngestSuccessComplete}
            />
          </div>
        ) : null}
        {!tenantId ? (
          <p className="mt-2 font-mono text-[10px] text-muted-foreground">
            Sign in and load wiki pages to resolve tenant for ingest metadata.
          </p>
        ) : null}
        {ingestError ? (
          <p className="mt-2 font-mono text-xs text-[var(--accent-red)]" role="alert">
            {ingestError}
          </p>
        ) : null}
        {ingestMode === "url" && (
          <div className="mt-3 space-y-2 rounded-md border border-border bg-background p-3">
            <input
              type="url"
              value={urlDraft}
              onChange={(e) => setUrlDraft(e.target.value)}
              placeholder="https://... (articles, YouTube, Instagram Reels)"
              className="min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-foreground outline-none focus-visible:border-accent md:min-h-0"
            />
            <p className="font-mono text-[10px] leading-snug text-muted-foreground">
              Supports articles, YouTube transcripts, Instagram Reels via SociaVault
            </p>
            <div>
              <label className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                HINT (optional)
              </label>
              <input
                type="text"
                value={urlHint}
                onChange={(e) => setUrlHint(e.target.value)}
                placeholder="e.g. work, AI research, personal — helps guide compilation"
                className="min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-foreground outline-none focus-visible:border-accent md:min-h-0"
              />
            </div>
            <button
              type="button"
              disabled={urlBusy || !urlDraft.trim()}
              onClick={() => void runUrlIngest()}
              className="min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2.5 font-mono text-sm hover:border-accent disabled:opacity-50 md:min-h-0 md:w-auto md:py-1.5"
            >
              {urlBusy ? "Compiling…" : "Compile →"}
            </button>
            {ingestProgress?.mode === "url" && !ingestProgress.summaryLine ? (
              <IngestCompileProgress
                progress={ingestProgress}
                onDismiss={dismissIngestProgress}
                onSwitchToPaste={switchIngestToPaste}
              />
            ) : null}
          </div>
        )}
        {ingestMode === "paste" && (
          <div className="mt-3 space-y-2 rounded-md border border-border bg-background p-3">
            <textarea
              value={pasteDraft}
              onChange={(e) => setPasteDraft(e.target.value)}
              placeholder="Paste article text, notes, transcript..."
              rows={5}
              className="min-h-[120px] w-full resize-y rounded-md border border-border bg-surface p-3 font-mono text-xs text-foreground outline-none focus-visible:border-accent md:min-h-[100px]"
            />
            <div>
              <label className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                HINT (optional)
              </label>
              <input
                type="text"
                value={pasteHint}
                onChange={(e) => setPasteHint(e.target.value)}
                placeholder="e.g. work, AI research, personal — helps guide compilation"
                className="min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-foreground outline-none focus-visible:border-accent md:min-h-0"
              />
            </div>
            <button
              type="button"
              disabled={pasteBusy || !pasteDraft.trim()}
              onClick={() => void runPasteIngest()}
              className="min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2.5 font-mono text-sm hover:border-accent disabled:opacity-50 md:min-h-0 md:w-auto md:py-1.5"
            >
              {pasteBusy ? "Compiling…" : "Compile →"}
            </button>
            {ingestProgress?.mode === "paste" && !ingestProgress.summaryLine ? (
              <IngestCompileProgress
                progress={ingestProgress}
                onDismiss={dismissIngestProgress}
                onSwitchToPaste={switchIngestToPaste}
              />
            ) : null}
          </div>
        )}
        {ingestMode === "file" && (
          <div className="mt-3 space-y-2 rounded-md border border-border bg-background p-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".md,.txt,.pdf"
              className="sr-only"
              aria-label="Choose file to upload"
              onChange={onFileInputChange}
            />
            <button
              type="button"
              disabled={fileBusy}
              onDragOver={(e) => {
                e.preventDefault();
                e.stopPropagation();
              }}
              onDrop={onFileDrop}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "w-full rounded-md border border-dashed border-border p-6 text-center transition-colors",
                "hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]",
                fileBusy && "pointer-events-none opacity-60",
              )}
            >
              <span className="font-mono text-sm text-muted-foreground">Drop .md, .txt, or .pdf</span>
              <span className="mt-1 block font-mono text-[10px] text-muted-foreground">or tap to choose</span>
            </button>
            <div>
              <label className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                HINT (optional)
              </label>
              <input
                type="text"
                value={fileHint}
                onChange={(e) => setFileHint(e.target.value)}
                placeholder="e.g. work, AI research, personal — helps guide compilation"
                className="min-h-11 w-full rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-foreground outline-none focus-visible:border-accent md:min-h-0"
              />
            </div>
            {filePickLabel ? (
              <p className="font-mono text-xs text-foreground" aria-live="polite">
                {filePickLabel}
              </p>
            ) : null}
            {ingestProgress?.mode === "file" && !ingestProgress.summaryLine ? (
              <IngestCompileProgress
                progress={ingestProgress}
                onDismiss={dismissIngestProgress}
                onSwitchToPaste={switchIngestToPaste}
              />
            ) : null}
          </div>
        )}
      </div>

      {persistentError && (
        <div
          role="alert"
          className="mx-3 mt-3 rounded-md border border-[var(--accent-red)] bg-[var(--accent-red)]/10 px-3 py-2 font-mono text-xs text-[var(--accent-red)]"
        >
          {persistentError}
        </div>
      )}

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {compileLogOpen ? (
          <CompileLog />
        ) : queryLoading ? (
          <QueryLoadingIndicator />
        ) : lastResponse ? (
          <ResponseCard
            result={lastResponse}
            submittedQuery={submittedQuery}
            onSourceClick={openSourceBySlug}
          />
        ) : (
          <div className="rounded-md border border-dashed border-border bg-surface p-6 transition-colors duration-200 ease-out">
            <p className="mb-4 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              Wiki health
            </p>
            <div className="grid gap-3 font-mono text-sm text-foreground sm:grid-cols-3">
              <button
                type="button"
                onClick={() => setPagesDialogOpen(true)}
                className="rounded-md border border-border p-3 text-left transition-colors hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
              >
                <div className="text-[10px] uppercase text-muted-foreground">Pages</div>
                <div className="text-lg">{wikiPages.length || stats.totalPages}</div>
              </button>
              <div className="rounded-md border border-border p-3">
                <div className="text-[10px] uppercase text-muted-foreground">Last compile</div>
                <div className="text-xs leading-snug" suppressHydrationWarning>{lastCompile}</div>
              </div>
              <div className="rounded-md border border-border p-3">
                <div className="text-[10px] uppercase text-muted-foreground">Cost (month)</div>
                <div className="text-[var(--cost)]">${stats.costThisMonthUsd.toFixed(2)}</div>
              </div>
            </div>
            <p className="mt-4 font-sans text-sm text-muted-foreground">
              Submit a query with ↵ (⇧↵ for a new line) to run retrieval + synthesis against the backend.
            </p>
          </div>
        )}
        {children ? <div className="mt-6 border-t border-border pt-6">{children}</div> : null}
      </div>

      <Dialog open={pagesDialogOpen} onOpenChange={setPagesDialogOpen}>
        <DialogContent className="max-h-[min(80vh,560px)] overflow-hidden sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-serif text-lg">Wiki pages</DialogTitle>
          </DialogHeader>
          <div className="min-h-0 flex-1 overflow-y-auto pr-1">
            {PAGE_GROUPS.map((g) => {
              const list = pagesByType.get(g.type) ?? [];
              if (list.length === 0) return null;
              return (
                <div key={g.type} className="mb-4">
                  <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    {g.label}
                  </div>
                  <ul className="space-y-1">
                    {list.map((p) => {
                      const Icon = pageTypeIcon(p.page_type);
                      return (
                        <li key={p.id || p.slug}>
                          <button
                            type="button"
                            onClick={() => {
                              selectWikiPage(p);
                              setPagesDialogOpen(false);
                            }}
                            className="flex w-full items-center gap-2 rounded-md border border-transparent px-2 py-2 text-left transition-colors hover:border-border hover:bg-background"
                          >
                            <span
                              className={cn("size-1.5 shrink-0 rounded-full", confidenceDotClass(p.confidence))}
                              title={`confidence ${p.confidence.toFixed(2)}`}
                            />
                            <Icon className="size-3.5 shrink-0 text-muted-foreground" aria-hidden />
                            <span className="min-w-0 flex-1 truncate font-sans text-sm text-foreground">
                              {p.title}
                            </span>
                            <span className="shrink-0 font-mono text-[10px] text-muted-foreground">{p.slug}</span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            })}
            {wikiPages.length === 0 && (
              <p className="font-mono text-xs text-muted-foreground">No pages loaded yet.</p>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
