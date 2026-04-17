#!/usr/bin/env python3
"""Seed two onboarding/reference Wiki pages for the Technical Advisor pilot tenant.

Run from repository root:
  python3 scripts/seed_technical_advisor_wiki.py --tenant-id <uuid> --tenant-name "<name>"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from git import Repo
from git.exc import GitCommandError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError as exc:  # pragma: no cover - startup guard
    print("❌ python-dotenv is not installed:", exc)
    print("   pip install python-dotenv")
    sys.exit(1)

load_dotenv(ROOT / ".env")

from src.lib.openai_client import create_embedding
from src.lib.supabase import create_supabase_client, ensure_tenant_exists


@dataclass(frozen=True)
class SeedPage:
    """One static page to create for the pilot tenant."""

    slug: str
    title: str
    page_type: str
    confidence: float
    status: str
    tags: list[str]
    summary: str
    context_hierarchy: list[str]
    content_markdown: str


def _tenant_slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "tenant"


def _require_env(name: str) -> str:
    value = (os.environ.get(name) or "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set in .env")
    return value


def _render_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    text = str(value)
    if text == "" or any(ch in text for ch in [":", "#", "[", "]", "{", "}", ","]):
        escaped = text.replace('"', '\\"')
        return f'"{escaped}"'
    return text


def _yaml_lines(data: dict[str, Any], indent: int = 0) -> list[str]:
    lines: list[str] = []
    pad = " " * indent
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{pad}{key}:")
            if not value:
                lines.append(f"{pad}  []")
                continue
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{pad}  -")
                    lines.extend(_yaml_lines(item, indent + 4))
                else:
                    lines.append(f"{pad}  - {_render_scalar(item)}")
        elif isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            if not value:
                lines.append(f"{pad}  {{}}")
                continue
            lines.extend(_yaml_lines(value, indent + 2))
        else:
            lines.append(f"{pad}{key}: {_render_scalar(value)}")
    return lines


def _render_markdown(frontmatter: dict[str, Any], body: str) -> str:
    header = "\n".join(_yaml_lines(frontmatter))
    return f"---\n{header}\n---\n\n{body.strip()}\n"


def _build_frontmatter(page: SeedPage, today: str) -> dict[str, Any]:
    return {
        "title": page.title,
        "date_created": today,
        "date_modified": today,
        "summary": page.summary,
        "type": page.page_type,
        "status": page.status,
        "confidence": page.confidence,
        "last_verified": today,
        "git_commit_hash": "manual-seed",
        "sources": [],
        "related": [],
        "tags": page.tags,
        "context_hierarchy": page.context_hierarchy,
    }


def _technical_advisor_pages() -> list[SeedPage]:
    onboarding = """## Do czego służy Compilore

Compilore pomaga szybko przeszukiwać katalogi producentów bez ręcznego przeklikiwania folderów i PDFów. Wgrywasz katalogi, zadajesz pytanie po polsku, a system zwraca odpowiedź z odniesieniem do konkretnego katalogu i strony.

## Jak wgrać katalog

1. Kliknij `Upload file`.
2. Wybierz plik PDF z katalogiem producenta.
3. Poczekaj około 30 sekund, aż katalog zostanie skompilowany do Wiki.
4. Po zakończeniu możesz od razu zadawać pytania o produkty i parametry.

## Jak zadać pytanie

Możesz pisać normalnym językiem, tak jak do kolegi z działu technicznego. Przykłady:

- „Znajdź wyłącznik silnikowy 400V 3-fazy, max 5A, montaż na szynie DIN”
- „Jaki jest zakres temperatur pracy dla przekaźników firmy [nazwa]?”
- „Które komponenty mają stopień ochrony IP67 i nadają się do pracy na zewnątrz?”

## Co oznaczają cytowania

Każda odpowiedź podaje nazwę katalogu i numer strony, z której pochodzi informacja. To znaczy, że zawsze możesz wrócić do oryginału i sprawdzić parametr przed zamówieniem lub wysłaniem oferty do klienta.

## Co oznacza ⚠️ ZWERYFIKUJ Z PRODUCENTEM

Ten znacznik oznacza, że system nie jest pewien danego parametru albo nie znalazł go wprost w źródle. W takiej sytuacji trzeba sprawdzić katalog ręcznie albo potwierdzić informację bezpośrednio u producenta.

## Ograniczenia (bądź szczery)

Tabele w PDF mogą być czasem wyekstrahowane nieczytelnie, szczególnie jeśli katalog ma wielokolumnowe specyfikacje. Jeśli odpowiedź wygląda podejrzanie, jest niepełna albo parametr wydaje się dziwny — zawsze sprawdź oryginalny katalog."""

    glossary = """## Podstawowe parametry

**Napięcie znamionowe (EN: Rated voltage)** — V — określa napięcie pracy urządzenia. Przy doborze sprawdź, czy zgadza się z instalacją klienta oraz czy nie przekracza dopuszczalnego zakresu pracy komponentu.

**Prąd znamionowy (EN: Rated current)** — A — mówi, jaki prąd urządzenie może bezpiecznie przenosić lub obsługiwać w pracy ciągłej. Sprawdź, czy parametr pokrywa maksymalne obciążenie w aplikacji klienta.

**Stopień ochrony IP (EN: Ingress Protection)** — IP67 / IP65 itd. — pokazuje odporność na pył i wodę. Przy doborze zweryfikuj warunki środowiskowe: hala, zewnątrz, wilgoć, mycie, zapylenie.

**Zakres temperatur pracy (EN: Operating temperature range)** — °C — określa temperatury, w których producent dopuszcza pracę urządzenia. Porównaj z realnymi warunkami w szafie, na zewnątrz lub przy źródle ciepła.

**Sposób montażu (EN: Mounting type)** — szyna DIN / panel / przewód — mówi, jak fizycznie zamontować komponent. Sprawdź, czy pasuje do istniejącej rozdzielnicy, obudowy lub sposobu zabudowy u klienta.

**Moc znamionowa (EN: Rated power)** — W / kW — określa moc roboczą urządzenia albo obsługiwanego obciążenia. Weryfikuj ją zawsze razem z napięciem i prądem, żeby uniknąć złego doboru.

**Częstotliwość (EN: Frequency)** — Hz — informuje, przy jakiej częstotliwości zasilania urządzenie pracuje poprawnie. Sprawdź zgodność z siecią klienta, szczególnie przy rozwiązaniach eksportowych lub specjalnych zastosowaniach.

**Typ obudowy (EN: Enclosure type)** — tworzywo / metal / stal — opisuje materiał i konstrukcję obudowy. Przy doborze zwróć uwagę na środowisko pracy, odporność mechaniczną, korozję i wymagania klienta.

**Certyfikaty (EN: Certifications)** — CE / UL / ATEX / IECEx — potwierdzają zgodność z wybranymi normami lub dopuszczeniami. Sprawdź, które z nich są wymagane przez klienta, branżę lub kraj docelowy.

**Prąd zwarciowy (EN: Short-circuit current)** — kA — ważny szczególnie dla bezpieczników i wyłączników. Określa, jaki poziom zwarcia aparat może bezpiecznie wytrzymać lub przerwać. Zawsze porównaj z warunkami instalacji i wymaganiami zabezpieczenia."""

    return [
        SeedPage(
            slug="ta-onboarding-guide",
            title="Jak używać Compilore — Przewodnik",
            page_type="concept",
            confidence=1.0,
            status="final",
            tags=["onboarding", "guide"],
            summary="Praktyczny przewodnik wdrożeniowy dla technicznego doradcy korzystającego z Compilore.",
            context_hierarchy=["technical_advisor", "onboarding"],
            content_markdown=onboarding,
        ),
        SeedPage(
            slug="ta-parameter-glossary",
            title="Słownik Parametrów Technicznych",
            page_type="concept",
            confidence=1.0,
            status="final",
            tags=["reference", "parameters", "glossary"],
            summary="Referencyjny słownik parametrów technicznych używanych przy doborze komponentów.",
            context_hierarchy=["technical_advisor", "reference"],
            content_markdown=glossary,
        ),
    ]


def _insert_wiki_page(
    client: Any,
    *,
    tenant_id: str,
    page: SeedPage,
    frontmatter: dict[str, Any],
) -> str:
    row = {
        "tenant_id": tenant_id,
        "slug": page.slug,
        "title": page.title,
        "page_type": page.page_type,
        "content_markdown": page.content_markdown,
        "frontmatter": frontmatter,
        "confidence": page.confidence,
        "status": page.status,
    }
    res = client.table("wiki_pages").insert(row).execute()
    data = getattr(res, "data", None) or []
    if not data or not data[0].get("id"):
        raise RuntimeError(f"wiki_pages insert failed for {page.slug}")
    return str(data[0]["id"])


def _insert_chunk(
    client: Any,
    *,
    tenant_id: str,
    wiki_page_id: str,
    chunk_text: str,
    embedding: list[float],
) -> None:
    row = {
        "tenant_id": tenant_id,
        "wiki_page_id": wiki_page_id,
        "document_id": None,
        "chunk_text": chunk_text,
        "chunk_index": 0,
        "embedding": embedding,
    }
    client.table("document_chunks").insert(row).execute()


def _write_page_file(
    *,
    wiki_repo_path: Path,
    tenant_slug: str,
    page: SeedPage,
    frontmatter: dict[str, Any],
) -> Path:
    out_path = wiki_repo_path / "tenants" / tenant_slug / "concepts" / f"{page.slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render_markdown(frontmatter, page.content_markdown), encoding="utf-8")
    return out_path


def _commit_page(repo: Repo, repo_root: Path, page_path: Path, page: SeedPage, tenant_name: str) -> None:
    rel = str(page_path.relative_to(repo_root))
    repo.index.add([rel])
    message = f"seed: {page.slug} for tenant {tenant_name}"
    try:
        repo.index.commit(message)
    except GitCommandError as exc:
        lowered = str(exc).lower()
        if "nothing to commit" in lowered or "no changes" in lowered:
            return
        raise


def _tenant_exists(client: Any, tenant_id: str) -> bool:
    res = client.table("tenants").select("id").eq("id", tenant_id).limit(1).execute()
    rows = getattr(res, "data", None) or []
    return bool(rows)


def _page_exists(client: Any, tenant_id: str, slug: str) -> bool:
    res = (
        client.table("wiki_pages")
        .select("slug")
        .eq("tenant_id", tenant_id)
        .eq("slug", slug)
        .limit(1)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    return bool(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed Technical Advisor onboarding pages")
    parser.add_argument("--tenant-id", required=True, help="Target tenant UUID")
    parser.add_argument("--tenant-name", required=True, help="Tenant display name for git commit messages")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tenant_id = args.tenant_id.strip()
    tenant_name = args.tenant_name.strip()
    if not tenant_id:
        print("❌ --tenant-id is required")
        return 1
    if not tenant_name:
        print("❌ --tenant-name is required")
        return 1

    try:
        _require_env("SUPABASE_URL")
        _require_env("SUPABASE_SERVICE_ROLE_KEY")
        _require_env("WIKI_REPO_PATH")
        _require_env("OPENAI_API_KEY")
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1

    wiki_repo_path = Path(_require_env("WIKI_REPO_PATH")).expanduser().resolve()
    if not wiki_repo_path.is_dir():
        print(f"❌ WIKI_REPO_PATH does not exist: {wiki_repo_path}")
        return 1

    try:
        client = create_supabase_client(service_key=_require_env("SUPABASE_SERVICE_ROLE_KEY"))
        if not _tenant_exists(client, tenant_id):
            print(f"❌ Tenant not found: {tenant_id}")
            print("   Aborting. Add the tenant row first in public.tenants.")
            return 1
        ensure_tenant_exists(client, tenant_id)
        repo = Repo(wiki_repo_path)
    except Exception as exc:
        print(f"❌ Startup failed: {exc}")
        return 1

    tenant_slug = _tenant_slug(tenant_name)
    today = date.today().isoformat()

    for page in _technical_advisor_pages():
        try:
            if _page_exists(client, tenant_id, page.slug):
                print(f"⚠️ Already exists: {page.slug} — skipped")
                continue

            frontmatter = _build_frontmatter(page, today)
            wiki_page_id = _insert_wiki_page(
                client,
                tenant_id=tenant_id,
                page=page,
                frontmatter=frontmatter,
            )
            embedding = create_embedding(page.content_markdown)
            _insert_chunk(
                client,
                tenant_id=tenant_id,
                wiki_page_id=wiki_page_id,
                chunk_text=page.content_markdown,
                embedding=embedding,
            )
            page_path = _write_page_file(
                wiki_repo_path=wiki_repo_path,
                tenant_slug=tenant_slug,
                page=page,
                frontmatter=frontmatter,
            )
            _commit_page(repo, wiki_repo_path, page_path, page, tenant_name)
            print(f"✅ Created {page.slug}")
        except Exception as exc:
            print(f"❌ Failed {page.slug}: {exc}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
