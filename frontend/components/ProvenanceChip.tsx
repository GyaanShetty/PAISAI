// A provenance chip: the design system's promise that a user can always tell,
// at a glance, whether a number is fact or forecast. Every value in PAISAI
// carries exactly one of these. See ../docs/DATA_INTEGRITY.md.

export type Provenance =
  | "Verified"
  | "Calculated"
  | "Estimated"
  | "Projected"
  | "User Provided"
  | "Assumed";

const STYLES: Record<Provenance, string> = {
  Verified: "border-verified/50 text-verified",
  Calculated: "border-calculated/50 text-calculated",
  Estimated: "border-estimated/50 text-estimated",
  Projected: "border-projected/50 text-projected",
  "User Provided": "border-muted/50 text-muted",
  Assumed: "border-assumed/50 text-assumed",
};

export function ProvenanceChip({ kind }: { kind: Provenance }) {
  return (
    <span
      className={`inline-block rounded-sm border px-1.5 py-0.5 text-[10px] uppercase tracking-wider ${STYLES[kind]}`}
      // Colour is never the sole carrier of meaning — the label text is always present.
      title={`Provenance: ${kind}`}
    >
      {kind}
    </span>
  );
}

// A value rendered with its provenance attached — the atomic unit of trust.
export function ProvenancedFigure({
  label,
  value,
  provenance,
}: {
  label: string;
  value: string;
  provenance: Provenance;
}) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-line/60 py-2">
      <span className="text-sm text-muted">{label}</span>
      <span className="flex items-center gap-2">
        <span className="tnum text-sm text-paper">{value}</span>
        <ProvenanceChip kind={provenance} />
      </span>
    </div>
  );
}

// The honest alternative to a fabricated number.
export function Unavailable({ label }: { label: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-line/60 py-2">
      <span className="text-sm text-muted">{label}</span>
      <span className="text-sm italic text-muted">
        No verified data
      </span>
    </div>
  );
}
