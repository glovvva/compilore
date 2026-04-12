export type ResponseFormat = "comparison" | "timeline" | "mindmap" | "list" | "code" | "prose";

function hasMarkdownTable(answer: string): boolean {
  const rows = answer.split("\n").filter((l) => {
    const t = l.trim();
    return t.includes("|") && (t.match(/\|/g) ?? []).length >= 2;
  });
  return rows.length >= 2;
}

function listLineCount(answer: string): number {
  const lines = answer.split("\n");
  let n = 0;
  for (const line of lines) {
    if (/^\s*-\s+\S/.test(line) || /^\s*\d+\.\s+\S/.test(line)) {
      n += 1;
    }
  }
  return n;
}

/**
 * Heuristic layout hint for **query** loop answers (before structured rendering).
 * Extend with model metadata when the API returns explicit format hints.
 */
export function detectFormat(query: string, answer: string): ResponseFormat {
  const q = query.trim();
  const a = answer ?? "";

  if (
    /\bcompare\b|\bvs\.?\b|\bversus\b|\bdifference between\b|\bcontrast\b/i.test(q) ||
    hasMarkdownTable(a)
  ) {
    return "comparison";
  }

  if (
    /\bhistory\b|\bevolution\b|\bwhen did\b|\bchronolog\b|\bover time\b|\btimeline\b/i.test(q)
  ) {
    return "timeline";
  }

  if (
    /\bhow does.*relat\b/i.test(q) ||
    /\bconnections?\b/i.test(q) ||
    /\brelationship between\b/i.test(q) ||
    /\bmap of\b/i.test(q)
  ) {
    return "mindmap";
  }

  if (listLineCount(a) >= 3) {
    return "list";
  }

  if (/```[\s\S]*?```/m.test(a)) {
    return "code";
  }

  return "prose";
}

export const FORMAT_DISPLAY_LABELS: Record<ResponseFormat, string> = {
  comparison: "comparison table",
  timeline: "timeline",
  mindmap: "mind map",
  list: "list",
  code: "code",
  prose: "synthesis",
};
