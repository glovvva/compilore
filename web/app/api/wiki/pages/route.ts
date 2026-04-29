import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase";
import { normalizeWikiPageType } from "@/lib/wiki/page-type";
import { relatedFromFrontmatter } from "@/lib/wiki/related";
import type { WikiPage } from "@/lib/types/wiki";

export async function GET() {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: rows, error } = await supabase
      .from("wiki_pages")
      .select("id, slug, title, page_type, confidence, updated_at, frontmatter")
      .order("page_type", { ascending: true })
      .order("title", { ascending: true });

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const pages: WikiPage[] = (rows ?? []).map((row) => ({
      id: row.id as string,
      slug: row.slug as string,
      title: row.title as string,
      page_type: normalizeWikiPageType(String(row.page_type)),
      confidence: Number(row.confidence ?? 0),
      updated_at: row.updated_at as string,
      related: relatedFromFrontmatter(row.frontmatter),
      frontmatter: (row.frontmatter ?? {}) as Record<string, unknown>,
    }));

    return NextResponse.json({ pages });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
