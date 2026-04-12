/**
 * Timeline — renders chronological answers from the Query loop.
 * Parses date/year patterns to build a visual vertical timeline.
 * Part of Compilore's Query loop response rendering layer.
 */

"use client";

import * as React from "react";
import ReactMarkdown from "react-markdown";

export interface TimelineProps {
  answer: string;
}

export interface TimelineEntry {
  year: string;
  text: string;
}

function parseTimelineEntries(answer: string): TimelineEntry[] {
  const entries: TimelineEntry[] = [];
  const seen = new Set<string>();

  const push = (year: string, text: string) => {
    const k = `${year}:${text.slice(0, 40)}`;
    if (seen.has(k)) return;
    seen.add(k);
    entries.push({ year, text: text.trim() });
  };

  const lines = answer.split("\n");
  const re1 = /^[-*]\s+\*?\*?(20\d\d|19\d\d)\*?\*?[:\s–-]+(.+)/;
  const re2 = /^\d+\.\s+\*?\*?(20\d\d|19\d\d)\*?\*?[:\s–-]+(.+)/;

  for (const line of lines) {
    const m1 = re1.exec(line);
    if (m1) {
      push(m1[1]!, m1[2]!);
      continue;
    }
    const m2 = re2.exec(line);
    if (m2) {
      push(m2[1]!, m2[2]!);
      continue;
    }
  }

  if (entries.length >= 2) return entries;

  const sentenceSplit = answer.split(/(?<=[.!?])\s+/);
  const yearRe = /\b(20\d{2}|19\d{2})\b/;
  for (const sent of sentenceSplit) {
    const ym = yearRe.exec(sent);
    if (!ym) continue;
    const year = ym[1]!;
    const idx = sent.indexOf(year) + year.length;
    let rest = sent.slice(idx).replace(/^[:\s–-]+/, "").trim();
    if (!rest) rest = sent.replace(yearRe, "").trim();
    if (rest.length > 120) rest = rest.slice(0, 117) + "…";
    if (rest.length > 5) push(year, rest);
  }

  return entries;
}

export function Timeline({ answer }: TimelineProps) {
  const entries = React.useMemo(() => parseTimelineEntries(answer), [answer]);

  if (entries.length < 2) {
    return (
      <div className="prose-compilore max-w-none font-serif text-[15px] leading-relaxed text-[var(--color-foreground)]">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="relative flex flex-col gap-0 pl-6">
      <div className="absolute bottom-2 left-[7px] top-2 w-px bg-border" aria-hidden />
      {entries.map((e, index) => (
        <div
          key={`${e.year}-${index}`}
          className="relative mb-4 pl-4 animate-slide-in last:mb-0"
          style={{ animationDelay: `${index * 60}ms` }}
        >
          <div
            className="absolute left-0 mt-1 h-3.5 w-3.5 rounded-full border-2 border-[var(--color-accent)] bg-[var(--color-background)]"
            aria-hidden
          />
          <div className="mb-0.5 font-mono text-xs font-medium text-[var(--color-cost)]">{e.year}</div>
          <div className="text-sm leading-relaxed text-[var(--color-foreground)]">{e.text}</div>
        </div>
      ))}
    </div>
  );
}
