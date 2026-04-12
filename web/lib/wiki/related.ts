/** Pulls `related` slugs from stored JSON frontmatter (`frontmatter.related[]`). */
export function relatedFromFrontmatter(frontmatter: unknown): string[] {
  if (!frontmatter || typeof frontmatter !== "object") return [];
  const r = (frontmatter as Record<string, unknown>).related;
  if (!Array.isArray(r)) return [];
  return r.filter((x): x is string => typeof x === "string");
}
