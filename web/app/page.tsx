import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background p-8">
      <p className="font-mono text-sm text-muted-foreground">Compilore</p>
      <Link
        href="/workspace"
        className="rounded-md border border-border bg-surface px-4 py-2 font-sans text-sm text-foreground transition-colors duration-200 ease-out hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
      >
        Open workspace
      </Link>
    </div>
  );
}
