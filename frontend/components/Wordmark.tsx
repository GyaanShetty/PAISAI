// The PAISAI wordmark. The brand intentionally highlights "AI" inside PAIS·AI —
// distinct in weight and colour, while the whole reads as one word. Restrained,
// within the muted palette. See ../docs/DESIGN_LANGUAGE.md.
export function Wordmark({ className = "" }: { className?: string }) {
  return (
    <span
      className={`font-semibold tracking-tight ${className}`}
      aria-label="PAISAI"
    >
      <span className="text-paper">PAIS</span>
      <span className="text-verified">AI</span>
    </span>
  );
}
