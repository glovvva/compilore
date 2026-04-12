"use client";

import * as React from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { MockQueryResponse } from "@/lib/mock-data";
import { MOCK_EXCERPTS_BY_SLUG } from "@/lib/mock-data";
import { detectFormat, FORMAT_DISPLAY_LABELS, type ResponseFormat } from "@/lib/detect-response-format";
import { ComparisonTable } from "@/components/response-formats/comparison-table";
import { Timeline } from "@/components/response-formats/timeline";
import { MindMap } from "@/components/response-formats/mindmap";
import { CodeBlock } from "@/components/response-formats/code-block";

export interface ResponseCardProps {
  result: MockQueryResponse;
  /** Raw user query (display); used for format detection + mindmap hint on submit. */
  submittedQuery?: string;
  /** Opens the inspector on a source slug (query loop → inspect loop handoff). */
  onSourceClick: (slug: string) => void;
}

function splitWikilinks(text: string): string[] {
  return text.split(/(\[\[[^\]]+\]\])/g);
}

const proseMarkdownComponents: Components = {
  p: ({ children }) => (
    <p className="mb-2 font-sans text-sm leading-relaxed text-foreground last:mb-0">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="font-sans font-semibold text-foreground">{children}</strong>
  ),
  em: ({ children }) => <em className="font-sans text-muted-foreground">{children}</em>,
  h1: ({ children }) => (
    <h1 className="mb-2 font-sans text-base font-semibold text-foreground last:mb-0">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-2 font-sans text-sm font-semibold text-foreground last:mb-0">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-2 font-sans text-xs font-semibold uppercase tracking-wide text-foreground last:mb-0">
      {children}
    </h3>
  ),
  ul: ({ children }) => (
    <ul className="mb-2 ml-4 list-disc space-y-1 font-sans text-sm leading-relaxed">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-2 ml-4 list-decimal space-y-1 font-sans text-sm leading-relaxed">{children}</ol>
  ),
  li: ({ children }) => <li className="font-sans leading-relaxed">{children}</li>,
};

function MarkdownChunk({ text }: { text: string }) {
  if (!text.trim()) return null;
  return <ReactMarkdown components={proseMarkdownComponents}>{text}</ReactMarkdown>;
}

function WikilinkProseBody({
  bodyMarkdown,
  onSourceClick,
}: {
  bodyMarkdown: string;
  onSourceClick: (slug: string) => void;
}) {
  const parts = React.useMemo(() => splitWikilinks(bodyMarkdown), [bodyMarkdown]);

  return (
    <TooltipProvider delayDuration={250}>
      <div className="prose-compilore max-w-none">
        {parts.map((part, i) => {
          const m = /^\[\[([^\]]+)\]\]$/.exec(part);
          if (m) {
            const slug = m[1]!;
            const excerpt = (MOCK_EXCERPTS_BY_SLUG[slug] ?? "No excerpt in mock graph.").slice(0, 200);
            return (
              <Tooltip key={`${slug}-${i}`}>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    onClick={() => onSourceClick(slug)}
                    className="mx-0.5 inline-flex max-w-[12rem] items-center truncate rounded border border-border bg-background px-1.5 py-0.5 font-mono text-[11px] text-accent transition-[border-color,background-color] duration-200 ease-out hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
                  >
                    {slug}
                  </button>
                </TooltipTrigger>
                <TooltipContent side="top" className="whitespace-pre-wrap">
                  {excerpt}
                  {(MOCK_EXCERPTS_BY_SLUG[slug]?.length ?? 0) > 200 ? "…" : ""}
                </TooltipContent>
              </Tooltip>
            );
          }
          return <MarkdownChunk key={i} text={part} />;
        })}
      </div>
    </TooltipProvider>
  );
}

/**
 * Presents a **query** loop result: typed answer, cost, grounded markdown with wikilinks,
 * and optional **gatekeeper** outcome from the compounding loop.
 */
export function ResponseCard({ result, submittedQuery = "", onSourceClick }: ResponseCardProps) {
  const query = submittedQuery ?? "";
  const answer = result.bodyMarkdown ?? "";
  const format: ResponseFormat = React.useMemo(() => detectFormat(query, answer), [query, answer]);
  const formatLabel = FORMAT_DISPLAY_LABELS[format];

  const renderBody = () => {
    switch (format) {
      case "comparison":
        return <ComparisonTable answer={answer} query={query} />;
      case "timeline":
        return <Timeline answer={answer} />;
      case "mindmap":
        return <MindMap answer={answer} />;
      case "code":
        return <CodeBlock answer={answer} />;
      case "list":
      case "prose":
        return <WikilinkProseBody bodyMarkdown={answer} onSourceClick={onSourceClick} />;
    }
  };

  return (
    <article className="rounded-md border border-border bg-surface p-4 transition-[border-color] duration-200 ease-out">
      <header className="mb-3 flex flex-wrap items-center gap-2">
        <Badge variant="accent" className="rounded">
          {formatLabel}
        </Badge>
        <span className="font-mono text-xs text-[var(--cost)]">{result.confidence.toFixed(2)} conf</span>
        <span className="font-mono text-xs text-muted-foreground">${result.costUsd.toFixed(3)}</span>
      </header>

      <div className="mb-4 text-foreground">{renderBody()}</div>

      {result.sourceSlugs.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          <span className="w-full font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Sources</span>
          {result.sourceSlugs.map((slug) => (
            <button
              key={slug}
              type="button"
              onClick={() => onSourceClick(slug)}
              className={cn(
                "rounded border border-border bg-background px-2 py-0.5 font-mono text-[11px] text-muted-foreground transition-[border-color,color] duration-200 ease-out hover:border-accent hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]",
              )}
            >
              {slug}
            </button>
          ))}
        </div>
      )}

      {result.gatekeeper && (
        <footer className="border-t border-border pt-3 font-sans text-xs">
          {result.gatekeeper === "saved" ? (
            <p className="text-[var(--accent-green)]">
              Saved to wiki/outputs/
              {result.gatekeeperDetail ? ` — ${result.gatekeeperDetail}` : ""}
            </p>
          ) : (
            <p className="text-muted-foreground">Discarded (not novel)</p>
          )}
        </footer>
      )}
    </article>
  );
}
