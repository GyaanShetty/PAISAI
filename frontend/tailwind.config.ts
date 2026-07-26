import type { Config } from "tailwindcss";

// Design language: Bloomberg Terminal meets Apple. Black, white, muted colours;
// colour carries meaning (provenance, risk), never decoration. See
// ../docs/DESIGN_LANGUAGE.md.
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0a0a0a",       // near-black surface
        paper: "#f7f7f5",     // muted off-white
        muted: "#6b7280",     // secondary text
        line: "#1f2937",      // hairline borders on dark
        // Provenance accents — muted, meaningful, never loud.
        verified: "#3f8f6f",
        calculated: "#5b7fb0",
        estimated: "#a98a4b",
        projected: "#8a6ea6",
        assumed: "#9aa0a6",
        risk: "#b0553f",
      },
      fontFamily: {
        // Tabular numerics so columns of figures align and scan cleanly.
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
