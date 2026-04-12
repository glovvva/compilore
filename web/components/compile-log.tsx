"use client";

import * as React from "react";
import { Check } from "lucide-react";
import { useWorkspace } from "@/components/workspace-context";
import { cn } from "@/lib/utils";

/**
 * Streams **ingest + compile** loop steps in the center column (mock timers).
 * Mirrors future LangGraph node transitions before git commit and Supabase writes.
 */
export function CompileLog() {
  const { compileLines, stats, setCompileLogOpen } = useWorkspace();
  const bottomRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [compileLines]);

  const allDone = compileLines.length > 0 && compileLines.every((l) => l.status === "done");
  const totalCost = "$0.063";

  return (
    <div className="flex h-full min-h-0 flex-col rounded-md border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
          Compile log
        </span>
        <button
          type="button"
          className="font-mono text-[10px] text-muted-foreground underline-offset-2 transition-colors duration-200 ease-out hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--accent)]"
          onClick={() => setCompileLogOpen(false)}
        >
          Close
        </button>
      </div>
      <pre className="min-h-0 flex-1 overflow-y-auto p-3 font-mono text-xs leading-relaxed text-muted-foreground">
        {compileLines.map((line) => (
          <div key={line.id} className="compilore-log-line mb-2 flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
            <span className="text-foreground">
              {line.status === "pending" ? (
                <span
                  className={cn(
                    "compilore-skeleton inline-block size-3.5 rounded border border-border align-middle",
                  )}
                  aria-hidden
                />
              ) : (
                <Check className="inline size-3.5 text-[var(--accent-green)]" />
              )}
            </span>
            <span>{line.label}</span>
            {line.durationMs != null && (
              <span className="text-[var(--cost)]">{line.durationMs}ms</span>
            )}
            {line.costFragment && <span className="text-[var(--cost)]">{line.costFragment}</span>}
            {line.gitHash && <span className="text-accent">{line.gitHash}</span>}
          </div>
        ))}
        {allDone && (
          <div className="compilore-log-line mt-3 border-t border-border pt-3 text-foreground">
            ✓ Done — {totalCost} · 3 concept · 2 entity · git abc123f
          </div>
        )}
        <div ref={bottomRef} />
      </pre>
      <p className="border-t border-border px-3 py-2 font-mono text-[10px] text-muted-foreground">
        Mock totals align with graph: {stats.concepts} concepts seeded in UI data.
      </p>
    </div>
  );
}
