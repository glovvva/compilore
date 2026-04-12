/**
 * CodeBlock — renders code-heavy answers with syntax awareness.
 * Handles responses from the Query loop that reference code/configs.
 */

"use client";

import * as React from "react";
import ReactMarkdown, { type Components } from "react-markdown";

export interface CodeBlockProps {
  answer: string;
}

function extractLang(className: string | undefined): string {
  if (!className) return "";
  const m = /language-(\w+)/.exec(className);
  return m ? m[1]! : "";
}

export function CodeBlock({ answer }: CodeBlockProps) {
  const [copied, setCopied] = React.useState(false);

  const components: Components = {
    code: ({ className, children, ...props }) => {
      const inline = !className?.includes("language-");
      if (inline) {
        return (
          <code
            className="rounded bg-[var(--color-surface)] px-1 py-0.5 font-mono text-[13px] text-[var(--color-accent)]"
            {...props}
          >
            {children}
          </code>
        );
      }

      const lang = extractLang(className);
      const raw = String(children).replace(/\n$/, "");

      return (
        <div className="overflow-hidden rounded-md border border-border">
          <div className="flex h-6 items-center justify-between border-b border-border bg-[var(--color-surface)] px-2">
            <span className="font-mono text-[11px] uppercase tracking-wide text-[var(--color-muted-foreground)]">
              {lang || "code"}
            </span>
            <button
              type="button"
              className="font-mono text-[11px] text-[var(--color-muted-foreground)] transition-colors hover:text-[var(--color-foreground)]"
              onClick={() => {
                void navigator.clipboard.writeText(raw).then(() => {
                  setCopied(true);
                  window.setTimeout(() => setCopied(false), 1500);
                });
              }}
            >
              {copied ? "Copied ✓" : "Copy"}
            </button>
          </div>
          <pre className="overflow-x-auto bg-[var(--color-background)] p-4 font-mono text-sm leading-relaxed text-[var(--color-foreground)]">
            <code className={className} {...props}>
              {children}
            </code>
          </pre>
        </div>
      );
    },
    p: ({ children }) => (
      <p className="mb-2 font-serif text-[15px] leading-relaxed text-[var(--color-foreground)] last:mb-0">
        {children}
      </p>
    ),
  };

  return (
    <div className="max-w-none">
      <ReactMarkdown components={components}>{answer}</ReactMarkdown>
    </div>
  );
}
