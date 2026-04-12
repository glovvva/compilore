import { detectFormat } from "@/lib/detect-response-format";

const MINDMAP_HINT =
  " Please include a mermaid mindmap code block showing the key relationships.";

const STORAGE_KEY = "compilore:query-for-api";

/** Text sent to the synthesizer (display query + optional hints). */
export function buildApiQueryForSubmission(displayQuery: string): string {
  const q = displayQuery.trim();
  if (!q) return q;
  const out = detectFormat(q, "") === "mindmap" ? q + MINDMAP_HINT : q;
  if (typeof window !== "undefined") {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ question: out, display: q }));
    } catch {
      /* quota / private mode */
    }
  }
  return out;
}

/** Read the last payload stashed for `POST /query` (then clears storage). */
export function consumeQueryForApiFromStorage(displayFallback: string): string {
  if (typeof window === "undefined") return displayFallback;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    sessionStorage.removeItem(STORAGE_KEY);
    if (!raw) return displayFallback;
    const o = JSON.parse(raw) as { question?: string };
    return typeof o.question === "string" ? o.question : displayFallback;
  } catch {
    return displayFallback;
  }
}
