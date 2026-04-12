/**
 * ComparisonTable — renders comparison/contrast answers from the Query loop.
 * Auto-parses markdown tables or extracts structured comparisons from prose.
 * Part of Compilore's Query loop response rendering layer.
 */

"use client";

import * as React from "react";
import ReactMarkdown from "react-markdown";

export interface ComparisonTableProps {
  answer: string;
  query: string;
}

function parseMarkdownTable(answer: string): string[][] | null {
  const lines = answer.split("\n");
  const pipeLines: string[] = [];
  for (const line of lines) {
    if (line.includes("|")) {
      const t = line.trim();
      if (t) pipeLines.push(line);
    }
  }
  if (pipeLines.length < 2) return null;

  const isSep = (line: string) => {
    const core = line.replace(/\|/g, "").trim();
    return /^[\s:-]+$/.test(core) && /-{2,}/.test(line);
  };

  const headerIdx = 0;
  let dataStart = 1;
  if (pipeLines.length >= 2 && isSep(pipeLines[1]!)) {
    dataStart = 2;
  }

  const splitRow = (line: string): string[] =>
    line
      .trim()
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((c) => c.trim());

  const header = splitRow(pipeLines[headerIdx]!);
  if (header.length < 2) return null;

  const rows: string[][] = [];
  for (let i = dataStart; i < pipeLines.length; i++) {
    const row = splitRow(pipeLines[i]!);
    if (row.length === header.length) rows.push(row);
    else if (row.length > 1) {
      while (row.length < header.length) row.push("");
      rows.push(row.slice(0, header.length));
    }
  }

  if (rows.length === 0) return null;
  return [header, ...rows];
}

export function ComparisonTable({ answer, query }: ComparisonTableProps) {
  const table = React.useMemo(() => parseMarkdownTable(answer), [answer]);

  if (!table) {
    return (
      <div className="prose-compilore max-w-none font-serif text-[15px] leading-relaxed text-[var(--color-foreground)]">
        <ReactMarkdown key={query}>{answer}</ReactMarkdown>
      </div>
    );
  }

  const [header, ...dataRows] = table;

  return (
    <div className="overflow-hidden rounded-md border border-border">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-[var(--color-surface)]">
            {header.map((cell, i) => (
              <th
                key={i}
                className="px-3 py-2 text-left font-mono text-[11px] uppercase tracking-wide text-[var(--color-muted-foreground)]"
              >
                {cell}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, ri) => (
            <tr
              key={ri}
              className={`border-t border-border ${ri % 2 === 1 ? "bg-[var(--color-surface)]/40" : "bg-transparent"}`}
            >
              {row.map((cell, ci) => (
                <td
                  key={ci}
                  className={`border-t border-border px-3 py-2 ${
                    ci === 0
                      ? "font-medium text-[var(--color-foreground)]"
                      : "text-[var(--color-muted-foreground)]"
                  }`}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
