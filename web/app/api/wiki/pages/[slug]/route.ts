import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";
import { normalizeWikiPageType } from "@/lib/wiki/page-type";
import { relatedFromFrontmatter } from "@/lib/wiki/related";
import type { WikiPageDetail } from "@/lib/types/wiki";

export async function GET(_request: Request, context: { params: Promise<{ slug: string }> }) {
  const { slug } = await context.params;
  const decoded = decodeURIComponent(slug);

  try {
    // Resolve user identity from session cookie
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Use service-role client to bypass RLS, look up tenant_id
    const admin = createSupabaseAdminClient();
    const { data: profile, error: profileError } = await admin
      .from("user_profiles")
      .select("tenant_id")
      .eq("id", user.id)
      .single();

    if (profileError || !profile) {
      return NextResponse.json({ error: "No tenant for this user" }, { status: 403 });
    }

    const { data: row, error } = await admin
      .from("wiki_pages")
      .select("*")
      .eq("tenant_id", profile.tenant_id)
      .eq("slug", decoded)
      .maybeSingle();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    if (!row) {
      return NextResponse.json({ error: "Not found" }, { status: 404 });
    }

    const fm = (row.frontmatter ?? {}) as Record<string, unknown>;
    const page: WikiPageDetail = {
      id: row.id as string,
      slug: row.slug as string,
      title: row.title as string,
      page_type: normalizeWikiPageType(String(row.page_type)),
      confidence: Number(row.confidence ?? 0),
      updated_at: row.updated_at as string,
      related: relatedFromFrontmatter(row.frontmatter),
      content_markdown: String(row.content_markdown ?? ""),
      frontmatter: fm,
      source_documents: (row.source_documents as string[] | null) ?? null,
      status: row.status != null ? String(row.status) : null,
      tenant_id: row.tenant_id as string,
      created_at: row.created_at as string,
    };

    return NextResponse.json({ page });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
