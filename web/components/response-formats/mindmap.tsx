/**
 * MindMap — renders relationship/concept map answers using Mermaid.js.
 * Extracts or requests mermaid syntax to visualize knowledge connections.
 * Part of Compilore's Query loop response rendering layer.
 */

"use client";

import * as React from "react";
import ReactMarkdown from "react-markdown";

export interface MindMapProps {
  answer: string;
  onFallback?: () => void;
}

const MERMAID_BLOCK = /```mermaid\n([\s\S]+?)```/i;

export function MindMap({ answer, onFallback }: MindMapProps) {
  const id = React.useId().replace(/:/g, "");
  const [svg, setSvg] = React.useState<string | null>(null);
  const [error, setError] = React.useState(false);

  const diagramCode = React.useMemo(() => {
    const m = MERMAID_BLOCK.exec(answer);
    return m ? m[1]!.trim() : null;
  }, [answer]);

  React.useEffect(() => {
    if (!diagramCode) {
      setSvg(null);
      onFallback?.();
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: "dark",
          themeVariables: {
            background: "transparent",
            primaryColor: "oklch(0.60 0.18 270)",
            primaryTextColor: "oklch(0.92 0.012 75)",
            lineColor: "oklch(0.18 0.008 265)",
            fontSize: "13px",
          },
        });
        const out = await mermaid.render(`mindmap-${id}`, diagramCode);
        if (!cancelled) setSvg(out.svg);
      } catch {
        if (!cancelled) {
          setError(true);
          onFallback?.();
        }
      }
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- onFallback is optional notify; omit to avoid effect churn
  }, [diagramCode, id]);

  if (!diagramCode || error) {
    return (
      <div className="space-y-3">
        <div className="rounded-md border border-border bg-[var(--color-surface)]/50 p-4 text-sm text-[var(--color-muted-foreground)]">
          Ask me to &quot;map&quot; or &quot;show connections&quot; to get a visual mindmap (Mermaid block in the
          answer).
        </div>
        <div className="prose-compilore max-w-none font-serif text-[15px] leading-relaxed text-[var(--color-foreground)]">
          <ReactMarkdown>{answer}</ReactMarkdown>
        </div>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="rounded-md border border-border bg-[var(--color-surface)]/50 p-4 text-sm text-[var(--color-muted-foreground)]">
        Rendering diagram…
      </div>
    );
  }

  return (
    <div className="overflow-auto rounded-md border border-border bg-[var(--color-surface)]/50 p-4">
      <div dangerouslySetInnerHTML={{ __html: svg }} />
    </div>
  );
}
