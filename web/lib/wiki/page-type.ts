import type { WikiPageType } from "@/lib/types/wiki";

const PAGE_TYPES: readonly WikiPageType[] = [
  "concept",
  "entity",
  "source_summary",
  "output",
  "index",
] as const;

export function normalizeWikiPageType(raw: string): WikiPageType {
  if (PAGE_TYPES.includes(raw as WikiPageType)) return raw as WikiPageType;
  return "concept";
}
