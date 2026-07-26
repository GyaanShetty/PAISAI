// Renders one API Figure — either a provenanced value (with its chip) or an
// honest "no verified data" row. This is the atomic unit of trust in the UI:
// the user can always see whether a number is fact, forecast, or missing.

import { Figure, formatFigureValue, isUnavailable } from "@/lib/api";
import { ProvenanceChip } from "./ProvenanceChip";

export function FigureRow({ label, figure }: { label: string; figure: Figure }) {
  if (isUnavailable(figure)) {
    return (
      <div className="flex items-baseline justify-between gap-4 border-b border-line/60 py-2">
        <span className="text-sm text-muted">{label}</span>
        <span
          className="text-right text-sm italic text-muted"
          title={figure.reason}
        >
          No verified data
        </span>
      </div>
    );
  }
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-line/60 py-2">
      <span className="text-sm text-muted">{label}</span>
      <span className="flex items-center gap-2">
        <span className="tnum text-sm text-paper">
          {formatFigureValue(figure)}
        </span>
        <ProvenanceChip kind={figure.provenance} />
      </span>
    </div>
  );
}
