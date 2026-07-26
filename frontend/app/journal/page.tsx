"use client";

import { useState } from "react";
import Link from "next/link";
import { ApiError, JournalEntryInput, api } from "@/lib/api";
import { Wordmark } from "@/components/Wordmark";

const ACTIONS = ["Buy", "Sell", "Hold", "SIP", "Withdrawal", "Loan", "Insurance", "Other"];
const CONFIDENCE = ["High", "Medium", "Low", "Insufficient"];

const today = () => new Date().toISOString().slice(0, 10);
const inSixMonths = () => {
  const d = new Date();
  d.setMonth(d.getMonth() + 6);
  return d.toISOString().slice(0, 10);
};

export default function JournalPage() {
  const [entry, setEntry] = useState<JournalEntryInput>({
    date: today(),
    asset: "",
    action: "SIP",
    thesis: "",
    expected_outcome: "",
    time_horizon: "10+ years",
    review_date: inSixMonths(),
    confidence: "Medium",
    market_context: "",
    risk_factors: [],
    assumptions: [],
    alternatives: [],
    sources: [],
  });
  const [lines, setLines] = useState({ risks: "", assumptions: "", sources: "" });
  const [saved, setSaved] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [reviewDate, setReviewDate] = useState(today());
  const [due, setDue] = useState<number | null>(null);
  const [audit, setAudit] = useState<string | null>(null);

  const set =
    (k: keyof JournalEntryInput) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setEntry({ ...entry, [k]: e.target.value });

  const splitLines = (s: string) =>
    s.split("\n").map((x) => x.trim()).filter(Boolean);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSaved(null);
    try {
      const res = await api.createJournalEntry({
        ...entry,
        risk_factors: splitLines(lines.risks),
        assumptions: splitLines(lines.assumptions),
        sources: splitLines(lines.sources),
      });
      setSaved(res.id);
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.detail ? ": " + err.detail : ""}` : String(err));
    }
  }

  async function loadDue() {
    setError(null);
    try {
      const res = await api.reviewDue(reviewDate);
      setDue(res.count);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    }
  }

  async function checkAudit() {
    setError(null);
    try {
      const res = await api.verifyAudit();
      setAudit(
        res.intact
          ? `Intact — ${res.records_checked ?? 0} records verified`
          : `TAMPER DETECTED — ${res.detail ?? ""}`,
      );
    } catch (err) {
      setAudit(err instanceof ApiError ? err.message : String(err));
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <header className="flex items-baseline justify-between border-b border-line/60 pb-4">
        <Wordmark className="text-xl" />
        <nav className="flex gap-4 text-sm text-muted">
          <Link href="/" className="hover:text-paper">Home</Link>
          <Link href="/dashboard" className="hover:text-paper">Dashboard</Link>
        </nav>
      </header>

      <h1 className="mt-8 text-lg font-medium">Decision Journal</h1>
      <p className="mt-2 text-sm text-muted">
        Record a decision with its thesis, assumptions, and risks — captured now, so
        that at the review date PAISAI can compare the thesis against what actually
        happened. The objective is better judgement, not just better returns.
      </p>

      <form onSubmit={onSubmit} className="mt-6 grid gap-4 sm:grid-cols-2">
        <Text label="Asset / decision" value={entry.asset} onChange={set("asset")} required />
        <Select label="Action" value={entry.action} onChange={set("action")} options={ACTIONS} />
        <Text label="Decision date" type="date" value={entry.date} onChange={set("date")} />
        <Text label="Review date" type="date" value={entry.review_date} onChange={set("review_date")} />
        <Text label="Time horizon" value={entry.time_horizon} onChange={set("time_horizon")} />
        <Select label="Confidence" value={entry.confidence} onChange={set("confidence")} options={CONFIDENCE} />
        <Area label="Thesis (why this decision)" value={entry.thesis} onChange={set("thesis")} />
        <Area label="Expected outcome" value={entry.expected_outcome} onChange={set("expected_outcome")} />
        <Area label="Assumptions (one per line)" value={lines.assumptions} onChange={(e) => setLines({ ...lines, assumptions: e.target.value })} />
        <Area label="Risks identified (one per line)" value={lines.risks} onChange={(e) => setLines({ ...lines, risks: e.target.value })} />
        <Area label="Sources (one per line)" value={lines.sources} onChange={(e) => setLines({ ...lines, sources: e.target.value })} />
        <Area label="Market context" value={entry.market_context || ""} onChange={set("market_context")} />
        <div className="sm:col-span-2">
          <button type="submit" className="rounded-sm border border-verified px-4 py-2 text-sm text-verified hover:bg-verified/10">
            Record decision
          </button>
        </div>
      </form>

      {saved && (
        <p className="mt-4 rounded-sm border border-verified/50 px-3 py-2 text-sm text-verified">
          Recorded. Entry id: <span className="tnum">{saved}</span>
        </p>
      )}
      {error && (
        <p className="mt-4 rounded-sm border border-risk/50 px-3 py-2 text-sm text-risk">{error}</p>
      )}

      <section className="mt-10 grid gap-6 border-t border-line/60 pt-6 sm:grid-cols-2">
        <div>
          <h2 className="text-xs uppercase tracking-widest text-muted">Reviews due</h2>
          <div className="mt-2 flex items-center gap-2">
            <input type="date" value={reviewDate} onChange={(e) => setReviewDate(e.target.value)}
              className="rounded-sm border border-line/60 bg-transparent px-2 py-1 text-sm text-paper" />
            <button onClick={loadDue} className="rounded-sm border border-line/60 px-3 py-1 text-sm text-muted hover:text-paper">
              Check
            </button>
          </div>
          {due !== null && (
            <p className="mt-2 text-sm text-paper">
              <span className="tnum">{due}</span> decision(s) due for review on or before {reviewDate}.
            </p>
          )}
        </div>
        <div>
          <h2 className="text-xs uppercase tracking-widest text-muted">Audit integrity</h2>
          <button onClick={checkAudit} className="mt-2 rounded-sm border border-line/60 px-3 py-1 text-sm text-muted hover:text-paper">
            Verify audit chain
          </button>
          {audit && <p className="mt-2 text-sm text-paper">{audit}</p>}
        </div>
      </section>
    </main>
  );
}

function Text(props: {
  label: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; type?: string; required?: boolean;
}) {
  return (
    <div>
      <label className="block text-xs uppercase tracking-wider text-muted">{props.label}</label>
      <input type={props.type || "text"} value={props.value} onChange={props.onChange} required={props.required}
        className="mt-1 w-full rounded-sm border border-line/60 bg-transparent px-3 py-2 text-sm text-paper outline-none focus:border-verified" />
    </div>
  );
}

function Area(props: {
  label: string; value: string; onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}) {
  return (
    <div className="sm:col-span-2">
      <label className="block text-xs uppercase tracking-wider text-muted">{props.label}</label>
      <textarea value={props.value} onChange={props.onChange} rows={2}
        className="mt-1 w-full rounded-sm border border-line/60 bg-transparent px-3 py-2 text-sm text-paper outline-none focus:border-verified" />
    </div>
  );
}

function Select(props: {
  label: string; value: string; onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void; options: string[];
}) {
  return (
    <div>
      <label className="block text-xs uppercase tracking-wider text-muted">{props.label}</label>
      <select value={props.value} onChange={props.onChange}
        className="mt-1 w-full rounded-sm border border-line/60 bg-ink px-3 py-2 text-sm text-paper outline-none focus:border-verified">
        {props.options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}
