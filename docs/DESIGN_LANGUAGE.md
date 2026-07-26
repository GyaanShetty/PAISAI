# Design Language

**Bloomberg Terminal meets Apple.** Institutional density with consumer-grade
craft. The design exists to serve trust: it must make evidence, provenance, and
uncertainty *visible*, never bury them.

---

## Character

- **Premium. Institutional.** It should feel like professional-grade equipment,
  not a lifestyle app.
- **Palette:** black, white, and muted colours. Colour carries meaning (e.g.
  provenance, risk) — it is never decorative.
- **Minimal.** Nothing on screen that does not inform.
- **Information dense.** Respect the user's screen and intelligence; do not
  infantilise the layout with excessive whitespace where data belongs.
- **No unnecessary animations. No gimmicks.** Motion is used only to aid
  comprehension (state transitions, focus), never to entertain.

---

## Principles

- **Professional typography.** A disciplined type scale; tabular figures for all
  numerics so columns align and scan cleanly.
- **Accessible.** WCAG-compliant contrast and semantics. Colour is never the sole
  carrier of meaning — provenance and risk always have a text/label equivalent.
- **Keyboard-first.** Every primary action is reachable and efficient from the
  keyboard. Power users should rarely need the mouse.
- **Lightning fast.** Perceived performance is a feature. No spinner where a
  cached value or an honest "unavailable" state will do.

---

## Design in service of the principles

The visual system is not neutral — it is an enforcement layer for the founding
principles:

- **Provenance is visible.** Verified, Calculated, Estimated, Projected, User
  Provided, and Assumed values are visually distinguishable (see
  [`DATA_INTEGRITY.md`](DATA_INTEGRITY.md)). A user can tell at a glance whether a
  number is fact or forecast.
- **Uncertainty has a home on screen.** Confidence levels, assumptions, and
  limitations are first-class UI, not fine print hidden behind tooltips.
- **No persuasion patterns.** No manufactured urgency, no engagement bait, no
  colour used to nudge a transaction. The interface informs; it does not sell.
- **Reasoning is expandable, not hidden.** Every recommendation can be unfolded to
  its full evidence / risks / alternatives / assumptions, honouring
  "transparency over persuasion."

---

## The PAISAI wordmark

The brand intentionally highlights **AI** inside **PAIS·AI**. In the wordmark, the
"AI" is made visually distinct — through typography, colour, weight, or a
restrained animation — while the whole reads as one word. The treatment stays
within the muted, institutional palette: the distinction is deliberate and
tasteful, never a gimmick.
