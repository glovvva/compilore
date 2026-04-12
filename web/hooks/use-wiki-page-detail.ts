"use client";

import useSWR from "swr";
import type { WikiPageDetail } from "@/lib/types/wiki";

function fetcher(url: string) {
  return fetch(url, { credentials: "include" }).then(async (res) => {
    if (res.status === 404) return null;
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error((err as { error?: string }).error ?? res.statusText);
    }
    const json = (await res.json()) as { page: WikiPageDetail };
    return json.page;
  });
}

/**
 * Loads full markdown + frontmatter for the inspector when a page slug is selected.
 */
export function useWikiPageDetail(slug: string | null) {
  const key = slug ? `/api/wiki/pages/${encodeURIComponent(slug)}` : null;
  const { data, error, isLoading, mutate } = useSWR<WikiPageDetail | null>(key, fetcher, {
    revalidateOnFocus: true,
  });

  return {
    page: data ?? null,
    isLoading,
    error: error instanceof Error ? error.message : error ? String(error) : null,
    mutate,
  };
}
