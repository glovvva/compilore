"use client";

import useSWR from "swr";
import type { WikiPage } from "@/lib/types/wiki";

const fetcher = async (url: string): Promise<{ pages: WikiPage[] }> => {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error ?? res.statusText);
  }
  return res.json();
};

/**
 * Live wiki graph for the nav + command palette; revalidates on focus and every 30s.
 */
export function useWikiPages() {
  const { data, error, isLoading, isValidating, mutate } = useSWR<{ pages: WikiPage[] }>(
    "/api/wiki/pages",
    fetcher,
    {
      refreshInterval: 30_000,
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    },
  );

  return {
    pages: data?.pages ?? [],
    isLoading,
    isValidating,
    error: error instanceof Error ? error.message : error ? String(error) : null,
    mutate,
  };
}
