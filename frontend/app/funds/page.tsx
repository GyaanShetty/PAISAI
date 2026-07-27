"use client";

import { useState } from "react";
import Link from "next/link";
import { ApiError, Figure, api, isUnavailable } from "@/lib/api";
import { Wordmark } from "@/components/Wordmark";
import { FigureRow } from "@/components/FigureRow";

export default function FundsPage() {
  const [code, setCode] = useState("");
  const [nav, setNav] = useState<Figure | null>(null);
  const [limitations, setLimitations] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function lookup(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setNav(null);
    try {
      const res = await api.fund(code.trim());
      setNav(res.nav);
      setLimitations(res.limitations || []);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <header className="flex items-baseline justify-between border-b border-line/60 pb-4">
        <Wordmark className="text-xl" />
        <nav className="flex gap-4 text-sm text-muted">
          <Link href="/" className="hover:text-paper">Home</Link>
          <Link href="/dashboard" className="hover:text-paper">Dashboard</Link>
          <Link href="/journal" className="hover:text-paper">Journal</Link>
        </nav>
      </header>

      <h1 className="mt-8 text-lg font-medium">Mutual Fund NAV</h1>
      <p className="mt-2 text-sm text-muted">
        Look up a fund&apos;s latest NAV by its AMFI scheme code. Values come{" "}
        <span className="text-paper">Verified</span> from AMFI with the date AMFI
        reported them — or, if the source is unreachable or the provider is not
        enabled, an honest &ldquo;No verified data&rdquo;. Never a fabricated price.
      </p>

      <form onSubmit={lookup} className="mt-6 flex items-end gap-3">
        <div className="flex-1">
          <label className="block text-xs uppercase tracking-wider text-muted">
            AMFI scheme code
          </label>
          <input
            className="mt-1 w-full rounded-sm border border-line/60 bg-transparent px-3 py-2 text-sm text-paper outline-none focus:border-verified"
            placeholder="e.g. 119551"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !code.trim()}
          className="rounded-sm border border-verified px-4 py-2 text-sm text-verified hover:bg-verified/10 disabled:opacity-50"
        >
          {loading ? "Looking up…" : "Look up NAV"}
        </button>
      </form>

      {error && (
        <p className="mt-6 rounded-sm border border-risk/50 px-3 py-2 text-sm text-risk">
          {error}
        </p>
      )}

      {nav && (
        <section className="mt-8">
          <div className="rounded-md border border-line/60 p-5">
            <FigureRow label={`Scheme ${code.trim()} — latest NAV`} figure={nav} />
            {!isUnavailable(nav) && nav.source && (
              <p className="mt-3 text-xs text-muted">
                Source: {nav.source}
                {nav.as_of ? ` · as of ${nav.as_of.slice(0, 10)}` : ""}
              </p>
            )}
          </div>
          {limitations.map((l) => (
            <p key={l} className="mt-3 text-xs italic text-muted">{l}</p>
          ))}
        </section>
      )}
    </main>
  );
}
