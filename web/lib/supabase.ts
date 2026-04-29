/** Server Supabase client (cookie session + RLS). Use only in Route Handlers / Server Components. */
export { createSupabaseServerClient } from "@/lib/supabase/server";

/** Service-role client — bypasses RLS. Server-only. */
export { createSupabaseAdminClient } from "@/lib/supabase/admin";
