"use client";

import * as React from "react";
import { ChevronDown, ChevronRight, X } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Skeleton } from "@/components/ui/skeleton";
import { useWorkspace } from "@/components/workspace-context";
import { useWikiPageDetail } from "@/hooks/use-wiki-page-detail";
import { confidenceBarClass } from "@/lib/wiki/confidence-dot";

export interface InspectorPanelProps {
  onClose: () => void;
}

export function InspectorPanel({ onClose }: InspectorPanelProps) {
  const { selectedWikiPage, openPageBySlug, inspectorSourceCitation } = useWorkspace();
  const slug = selectedWikiPage?.slug ?? null;
  const { page: detail, isLoading, error } = useWikiPageDetail(slug);
  const [fmOpen, setFmOpen] = React.useState(false);

  const displayTitle = detail?.title ?? selectedWikiPage?.title ?? "";
  const displaySlug = detail?.slug ?? selectedWikiPage?.slug ?? "";
  const displayConfidence = detail?.confidence ?? selectedWikiPage?.confidence ?? 0;
  const related = detail?.related?.length ? detail.related : selectedWikiPage?.related ?? [];
  const normalizedBodyMarkdown = React.useMemo(() => {
    const raw = detail?.content_markdown ?? "";
    return raw.replace(/\[\[\[\[([^\]]+)\]\]\]\]/g, "[[$1]]");
  }, [detail?.content_markdown]);

  return (
    <aside className="fixed right-0 top-10 z-20 flex h-[calc(100dvh-2.5rem)] w-80 flex-col border-l border-border bg-surface">
      <div className="flex h-10 shrink-0 items-center justify-between border-b border-border px-3">
        <span className="font-mono text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
          Inspector
        </span>
        <button
          type="button"
          className="flex size-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-background hover:text-foreground"
          aria-label="Close inspector"
          onClick={onClose}
        >
          <X className="size-4" />
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {!selectedWikiPage && (
          <p className="font-mono text-xs text-muted-foreground">No selection.</p>
        )}

        {selectedWikiPage && error && (
          <div
            role="alert"
            className="mb-3 rounded-md border border-[var(--accent-red)] bg-[var(--accent-red)]/10 px-3 py-2 font-mono text-xs text-[var(--accent-red)]"
          >
            {error}
          </div>
        )}

        {selectedWikiPage && isLoading && (
          <div className="space-y-3">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
            <Skeleton className="h-2 w-full" />
            <Skeleton className="h-40 w-full" />
          </div>
        )}

        {selectedWikiPage && !isLoading && detail && (
          <>
            {inspectorSourceCitation && (
              <div className="mb-3 rounded-md border border-accent/40 bg-accent/5 px-2 py-1.5 font-mono text-[10px] text-accent">
                Source detail view
              </div>
            )}
            {inspectorSourceCitation && (
              <button
                type="button"
                className="mb-3 font-mono text-[10px] text-accent transition-opacity duration-200 ease-out hover:opacity-80"
                onClick={() => openPageBySlug(detail.slug)}
              >
                ← Back to full page
              </button>
            )}

            <h1 className="font-serif text-2xl font-normal leading-tight text-foreground">
              {displayTitle}
            </h1>
            <p className="mt-1 font-mono text-[11px] text-muted-foreground">{displaySlug}</p>

            <div className="mt-4">
              <div className="mb-1 flex items-center justify-between font-mono text-[10px] uppercase text-muted-foreground">
                <span>Confidence</span>
                <span className="text-[var(--cost)]">{displayConfidence.toFixed(2)}</span>
              </div>
              <div className="h-1 w-full overflow-hidden rounded-full border border-border bg-background">
                <div
                  className={confidenceBarClass(displayConfidence)}
                  style={{ width: `${Math.round(displayConfidence * 100)}%` }}
                />
              </div>
            </div>

            <Collapsible open={fmOpen} onOpenChange={setFmOpen} className="mt-4">
              <CollapsibleTrigger className="flex w-full items-center gap-1 rounded-md border border-border bg-background px-2 py-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground transition-[border-color] duration-200 ease-out hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]">
                {fmOpen ? (
                  <ChevronDown className="size-3" />
                ) : (
                  <ChevronRight className="size-3" />
                )}
                Frontmatter
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-2 rounded-md border border-border bg-background p-2">
                <pre className="font-mono text-[11px] leading-relaxed text-muted-foreground">
                  {JSON.stringify(detail.frontmatter ?? {}, null, 2)}
                </pre>
              </CollapsibleContent>
            </Collapsible>

            <section className="mt-4">
              <h2 className="mb-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                Related
              </h2>
              {related.length === 0 ? (
                <p className="font-mono text-xs text-muted-foreground">—</p>
              ) : (
                <ul className="space-y-1">
                  {related.map((relSlug) => (
                    <li key={relSlug}>
                      <button
                        type="button"
                        onClick={() => openPageBySlug(relSlug)}
                        className="font-mono text-xs text-accent transition-opacity duration-200 ease-out hover:opacity-80 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
                      >
                        [[{relSlug}]]
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {detail.source_documents && detail.source_documents.length > 0 && (
              <section className="mt-4">
                <h2 className="mb-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  Source documents
                </h2>
                <ul className="font-mono text-[11px] text-muted-foreground">
                  {detail.source_documents.map((id) => (
                    <li key={id}>{id}</li>
                  ))}
                </ul>
              </section>
            )}

            <section className="mt-6 border-t border-border pt-4">
              <h2 className="mb-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                Body
              </h2>
              <div className="prose-compilore font-sans text-sm leading-relaxed text-foreground">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    strong: ({ children }) => (
                      <strong className="font-sans font-semibold">{children}</strong>
                    ),
                    em: ({ children }) => (
                      <em className="text-muted-foreground">{children}</em>
                    ),
                  }}
                >
                  {normalizedBodyMarkdown}
                </ReactMarkdown>
              </div>
            </section>
          </>
        )}

        {selectedWikiPage && !isLoading && !detail && !error && (
          <p className="font-mono text-xs text-muted-foreground">Page not found.</p>
        )}
      </div>
    </aside>
  );
}
