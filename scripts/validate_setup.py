#!/usr/bin/env python3
"""End-to-end validation for Compilore + Supabase (Sprint 4).

Run from the repository root:
  python scripts/validate_setup.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env before importing app libs that read os.environ
try:
    from dotenv import load_dotenv
except ImportError as exc:
    print("❌ python-dotenv is not installed:", exc)
    print("   pip install python-dotenv")
    sys.exit(1)

load_dotenv(ROOT / ".env")

FAILURES: list[str] = []


def ok(name: str, detail: str = "") -> None:
    extra = f" ({detail})" if detail else ""
    print(f"✅ {name}{extra}")


def bad(name: str, msg: str) -> None:
    print(f"❌ {name}: {msg}")
    FAILURES.append(name)


def main() -> None:
    print("Compilore validate_setup — Sprint 4\n")

    # --- Environment ---
    supabase_url = (os.environ.get("SUPABASE_URL") or "").strip()
    service_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    tenant_id = (os.environ.get("COMPILORE_DEFAULT_TENANT_ID") or "").strip()
    db_url = (os.environ.get("SUPABASE_DB_URL") or "").strip()
    anthropic_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    openai_key = (os.environ.get("OPENAI_API_KEY") or "").strip()

    if not supabase_url or not service_key:
        bad(
            "Environment",
            "SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_SERVICE_ROLE_KEY) must be set",
        )
    else:
        ok("Environment", "Supabase URL + service key present")

    if not tenant_id:
        bad("COMPILORE_DEFAULT_TENANT_ID", "not set in .env")
    else:
        ok("COMPILORE_DEFAULT_TENANT_ID", "set")

    if not db_url:
        bad(
            "SUPABASE_DB_URL",
            "not set — add Postgres URI from Supabase → Project Settings → Database "
            "(required for SELECT 1 + pgvector checks)",
        )
    else:
        ok("SUPABASE_DB_URL", "set")

    if not anthropic_key:
        bad("ANTHROPIC_API_KEY", "not set")
    else:
        ok("ANTHROPIC_API_KEY", "set")

    if not openai_key:
        bad("OPENAI_API_KEY", "not set")
    else:
        ok("OPENAI_API_KEY", "set")

    # --- Supabase REST ---
    if supabase_url and service_key:
        try:
            from supabase import create_client

            client = create_client(supabase_url, service_key)
            res = client.table("tenants").select("id").limit(1).execute()
            _ = getattr(res, "data", None)
            ok("Supabase REST", "tenants table reachable")
        except Exception as exc:
            bad("Supabase REST", str(exc))
            client = None
    else:
        client = None
        print("⏭️  Supabase REST skipped (missing URL or key)")

    # --- Tenant row ---
    if client and tenant_id:
        try:
            res = client.table("tenants").select("id").eq("id", tenant_id).limit(1).execute()
            rows = getattr(res, "data", None) or []
            if not rows:
                bad(
                    "Tenant row",
                    f"no tenants.id = {tenant_id!r} — run sql/003_seed_tenant.sql and copy id into .env",
                )
            else:
                ok("Tenant row", f"id {tenant_id[:8]}… exists")
        except Exception as exc:
            bad("Tenant row", str(exc))

    # --- SQL: SELECT 1 + pgvector ---
    if db_url:
        try:
            import psycopg2 as _pg
        except ImportError:
            bad("psycopg2", "install psycopg2-binary: pip install psycopg2-binary")
            _pg = None

        if _pg is not None:
            try:
                conn = _pg.connect(db_url)
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT 1")
                    one = cur.fetchone()
                    if one != (1,):
                        bad("SQL SELECT 1", f"unexpected result: {one!r}")
                    else:
                        ok("SQL SELECT 1", "database connection OK")

                    cur.execute(
                        "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                    )
                    row = cur.fetchone()
                    if row and row[0]:
                        ok("pgvector extension", "enabled")
                    else:
                        bad("pgvector extension", "not enabled — run sql/001_initial_schema.sql")
                    cur.close()
                finally:
                    conn.close()
            except Exception as exc:
                bad("Postgres connection", str(exc))
    else:
        print("⏭️  SQL SELECT 1 / pgvector skipped (no SUPABASE_DB_URL)")

    # --- wiki git ---
    wiki = ROOT / "wiki"
    git_marker = wiki / ".git"
    if not wiki.is_dir():
        bad("wiki/", f"directory missing: {wiki}")
    elif not git_marker.exists():
        bad("wiki git", f"not a git repo (missing {git_marker})")
    else:
        ok("wiki/", "directory + git present")

    # --- Anthropic ---
    if anthropic_key:
        try:
            import anthropic

            ac = anthropic.Anthropic(api_key=anthropic_key)
            msg = ac.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=32,
                messages=[{"role": "user", "content": "say hello"}],
            )
            text = ""
            for block in msg.content:
                if getattr(block, "type", None) == "text":
                    text += block.text
            if not text.strip():
                bad("Anthropic API", "empty response text")
            else:
                ok("Anthropic API", "non-empty reply")
        except Exception as exc:
            bad("Anthropic API", str(exc))

    # --- OpenAI embedding ---
    if openai_key:
        try:
            from src.lib.openai_client import create_embedding

            vec = create_embedding("hello")
            if len(vec) != 1536:
                bad("OpenAI embedding", f"expected 1536 dims, got {len(vec)}")
            else:
                ok("OpenAI embedding", "text-embedding-3-small 1536 dims")
        except Exception as exc:
            bad("OpenAI embedding", str(exc))

    print()
    if FAILURES:
        print(f"Failed checks ({len(FAILURES)}): {', '.join(FAILURES)}")
        sys.exit(1)
    print("All checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
