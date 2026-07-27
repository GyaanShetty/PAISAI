"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ApiError,
  DashboardInput,
  DashboardResult,
  api,
  isUnavailable,
} from "@/lib/api";
import { Wordmark } from "@/components/Wordmark";
import { FigureRow } from "@/components/FigureRow";
import { ProvenanceChip } from "@/components/ProvenanceChip";

type FormState = {
  assets: string;
  liabilities: string;
  monthly_income: string;
  monthly_expenses: string;
  liquid_savings: string;
  holdings: string; // "Equity=600000, Debt=400000"
};

const EMPTY: FormState = {
  assets: "",
  liabilities: "",
  monthly_income: "",
  monthly_expenses: "",
  liquid_savings: "",
  holdings: "",
};

function num(s: string): number | undefined {
  const t = s.trim();
  if (t === "") return undefined;
  const n = Number(t);
  return Number.isFinite(n) ? n : undefined;
}

function parseHoldings(s: string): Record<string, number> | undefined {
  const t = s.trim();
  if (t === "") return undefined;
  const out: Record<string, number> = {};
  for (const pair of t.split(",")) {
    const [name, value] = pair.split("=").map((x) => x.trim());
    const n = Number(value);
    if (name && Number.isFinite(n)) out[name] = n;
  }
  return Object.keys(out).length ? out : undefined;
}

export default function DashboardPage() {
  const [form, setForm] = useState<FormState>(EMPTY);
  const [result, setResult] = useState<DashboardResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const set = (k: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const input: DashboardInput = {
      assets: num(form.assets),
      liabilities: num(form.liabilities),
      monthly_income: num(form.monthly_income),
      monthly_expenses: num(form.monthly_expenses),
      liquid_savings: num(form.liquid_savings),
      holdings: parseHoldings(form.holdings),
    };
    try {
      setResult(await api.dashboard(input));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <header className="flex items-baseline justify-between border-b border-line/60 pb-4">
        <Wordmark className="text-xl" />
        <nav className="flex gap-4 text-sm text-muted">
          <Link href="/" className="hover:text-paper">
            Home
          </Link>
          <Link href="/journal" className="hover:text-paper">
            Journal
          </Link>
        </nav>
      </header>

      <h1 className="mt-8 text-lg font-medium">Dashboard</h1>
      <p className="mt-2 text-sm text-muted">
        Enter your figures. Everything computed is derived from your own inputs and
        labelled <span className="text-paper">User Provided</span> →{" "}
        <span className="text-paper">Calculated</span>. Leave a field blank and the
        result is honestly marked unavailable — never guessed.
      </p>

      <form onSubmit={onSubmit} className="mt-6 grid gap-4 sm:grid-cols-2">
        <Field label="Total assets" value={form.assets} onChange={set("assets")} />
        <Field
          label="Total liabilities"
          value={form.liabilities}
          onChange={set("liabilities")}
        />
        <Field
          label="Monthly income"
          value={form.monthly_income}
          onChange={set("monthly_income")}
        />
        <Field
          label="Monthly expenses"
          value={form.monthly_expenses}
          onChange={set("monthly_expenses")}
        />
        <Field
          label="Liquid savings"
          value={form.liquid_savings}
          onChange={set("liquid_savings")}
        />
        <div className="sm:col-span-2">
          <label className="block text-xs uppercase tracking-wider text-muted">
            Holdings (name=value, comma-separated)
          </label>
          <input
            className="mt-1 w-full rounded-sm border border-line/60 bg-transparent px-3 py-2 text-sm text-paper outline-none focus:border-verified"
            placeholder="Equity=600000, Debt=400000, Gold=100000"
            value={form.holdings}
            onChange={set("holdings")}
          />
        </div>
        <div className="sm:col-span-2">
          <button
            type="submit"
            disabled={loading}
            className="rounded-sm border border-verified px-4 py-2 text-sm text-verified hover:bg-verified/10 disabled:opacity-50"
          >
            {loading ? "Computing…" : "Compute dashboard"}
          </button>
        </div>
      </form>

      {error && (
        <p className="mt-6 rounded-sm border border-risk/50 px-3 py-2 text-sm text-risk">
          {error}
        </p>
      )}

      {result && (
        <section className="mt-8">
          <h2 className="text-xs uppercase tracking-widest text-muted">Results</h2>
          <div className="mt-3 rounded-md border border-line/60 p-5">
            <FigureRow label="Net worth" figure={result.net_worth} />
            <FigureRow label="Savings rate" figure={result.savings_rate} />
            <FigureRow
              label="Emergency fund coverage"
              figure={result.emergency_fund_months}
            />
            {isUnavailable(result.portfolio_weights) ? (
              <FigureRow
                label="Portfolio weights"
                figure={result.portfolio_weights}
              />
            ) : (
              <div className="pt-2">
                <div className="flex items-center justify-between py-1">
                  <span className="text-sm text-muted">Portfolio weights</span>
                  <ProvenanceChip kind="Calculated" />
                </div>
                {Object.entries(result.portfolio_weights).map(([name, w]) => (
                  <div
                    key={name}
                    className="flex items-baseline justify-between border-b border-line/40 py-1.5 pl-4"
                  >
                    <span className="text-sm text-muted">{name}</span>
                    <span className="tnum text-sm text-paper">
                      {(w.value * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
          {result.notes.map((n) => (
            <p key={n} className="mt-3 text-xs italic text-muted">
              {n}
            </p>
          ))}
        </section>
      )}
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <div>
      <label className="block text-xs uppercase tracking-wider text-muted">
        {label}
      </label>
      <input
        inputMode="decimal"
        className="mt-1 w-full rounded-sm border border-line/60 bg-transparent px-3 py-2 text-sm text-paper outline-none focus:border-verified"
        value={value}
        onChange={onChange}
      />
    </div>
  );
}
