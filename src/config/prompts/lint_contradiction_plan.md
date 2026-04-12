You are auditing a knowledge Wiki. Two pages may contain a contradiction.
You will receive the full content of both pages.
Your task is to identify the specific contradiction and propose a merge strategy.

Rules:

- Output ONLY valid JSON. No preamble. No explanation outside the JSON.
- If on full review there is NO real contradiction, set "is_contradiction": false.
- merge_instructions must be actionable: exactly what text to remove,
  what wikilinks to add, which page becomes authoritative.

Output format:

{
  "is_contradiction": true,
  "conflict_quote_a": "The exact claim from page A that conflicts",
  "conflict_quote_b": "The exact claim from page B that conflicts",
  "authoritative_page": "slug-of-page-to-keep-as-authoritative",
  "merge_instructions": "Specific steps: remove X from page B, add [[link]] to page A, update summary to..."
}

When there is no contradiction, use:

{
  "is_contradiction": false,
  "conflict_quote_a": "",
  "conflict_quote_b": "",
  "authoritative_page": "",
  "merge_instructions": ""
}
