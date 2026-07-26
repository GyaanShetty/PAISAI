import Link from "next/link";
import { Wordmark } from "@/components/Wordmark";
import {
  ProvenancedFigure,
  Unavailable,
} from "@/components/ProvenanceChip";

const PRINCIPLES: [string, string][] = [
  ["Truth over confidence", "A calibrated “I'm not sure” beats a confident wrong answer."],
  ["Evidence over opinions", "Claims are tied to verifiable sources, or labelled as inference."],
  ["Transparency over persuasion", "We explain. We do not sell. Reasoning is always visible."],
  ["Education over prediction", "We raise your judgement rather than play oracle."],
  ["Long-term wealth over short-term excitement", "Loyal to what compounds, indifferent to what is loud."],
  ["Honesty over completeness", "An honest partial answer beats a complete fabrication."],
];

export default function Home() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16 md:py-24">
      {/* Masthead */}
      <header className="border-b border-line/60 pb-8">
        <Wordmark className="text-3xl" />
        <p className="mt-4 text-lg text-muted">
          Your AI Financial Operating System.
        </p>
        <nav className="mt-6 flex gap-3 text-sm">
          <Link
            href="/dashboard"
            className="rounded-sm border border-verified/60 px-3 py-1.5 text-verified hover:bg-verified/10"
          >
            Open Dashboard →
          </Link>
          <Link
            href="/journal"
            className="rounded-sm border border-line/60 px-3 py-1.5 text-muted hover:text-paper"
          >
            Decision Journal →
          </Link>
        </nav>
        <p className="mt-6 max-w-2xl text-sm leading-relaxed text-paper/80">
          The most trustworthy AI-powered personal finance platform ever built.
          Not the smartest. Not the flashiest. The most trustworthy. Every
          conclusion is transparent, evidence-backed, explainable, auditable, and
          conservative under uncertainty.
        </p>
      </header>

      {/* Founding principles */}
      <section className="mt-12">
        <h2 className="text-xs uppercase tracking-widest text-muted">
          Six non-negotiable principles
        </h2>
        <ol className="mt-6 grid gap-x-10 gap-y-6 md:grid-cols-2">
          {PRINCIPLES.map(([title, body], i) => (
            <li key={title} className="flex gap-4">
              <span className="tnum text-sm text-verified">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div>
                <h3 className="text-sm font-medium text-paper">{title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-muted">{body}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* Provenance demonstration — the design system's core promise */}
      <section className="mt-16">
        <h2 className="text-xs uppercase tracking-widest text-muted">
          Every value knows where it came from
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted">
          A user can always tell, at a glance, whether a number is fact or
          forecast. When verified data is missing, PAISAI says so — it never
          invents a figure. (Illustrative layout; figures are sample data.)
        </p>
        <div className="mt-6 rounded-md border border-line/60 p-5">
          <ProvenancedFigure
            label="Net worth"
            value="₹ 42,80,000"
            provenance="Calculated"
          />
          <ProvenancedFigure
            label="Portfolio value (live)"
            value="₹ 31,10,500"
            provenance="Verified"
          />
          <ProvenancedFigure
            label="Monthly expenses"
            value="₹ 84,000"
            provenance="User Provided"
          />
          <ProvenancedFigure
            label="Retirement corpus at 60"
            value="₹ 6.4 – 9.1 Cr"
            provenance="Projected"
          />
          <ProvenancedFigure
            label="Assumed inflation"
            value="6.0%"
            provenance="Assumed"
          />
          <Unavailable label="Live P/E of an unlisted holding" />
        </div>
      </section>

      {/* The governing rule */}
      <section className="mt-16 border-t border-line/60 pt-8">
        <blockquote className="max-w-3xl text-sm leading-relaxed text-paper/80">
          If we don&apos;t know, we say we don&apos;t know. If we believe
          something, we explain exactly why. If we recommend something, we show
          the evidence, the risks, the alternatives, and the assumptions.
        </blockquote>
        <p className="mt-6 text-xs uppercase tracking-widest text-muted">
          The defining feature is not intelligence. It is trust.
        </p>
      </section>

      <footer className="mt-16 border-t border-line/60 pt-6 text-xs text-muted">
        <Wordmark className="text-sm" /> · Foundational build · See{" "}
        <code className="text-paper/70">docs/</code> for the full constitution.
      </footer>
    </main>
  );
}
