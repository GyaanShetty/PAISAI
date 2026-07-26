# Security & Privacy

Treat PAISAI like **regulated financial software**. It holds some of the most
sensitive data a person has. Security and privacy are not features bolted on
later — they are preconditions for trust, which is the entire product.

---

## Requirements

- **Encryption**
  - End-to-end encryption where appropriate.
  - Sensitive financial data **encrypted at rest.**
  - Secrets **encrypted** and never committed to source control.
- **Access control**
  - **Role-based access control (RBAC).**
  - **Multi-factor authentication (MFA).**
  - **Secure session handling** (short-lived tokens, safe rotation, secure cookies).
- **Abuse & integrity**
  - **Rate limiting** on all public and expensive endpoints.
  - **Input validation** on every boundary.
  - **OWASP compliance** (Top 10 addressed by design and verified in CI).
- **Accountability**
  - **Audit logging** of security-relevant and financially material events.
- **Privacy**
  - **Privacy-first architecture** — collect the minimum, retain the minimum,
    expose the minimum.
  - **Never expose credentials** in logs, errors, responses, or the client.

---

## Practices

- **Secrets** live in a managed secret store, are injected at runtime, and are
  rotated. `.env` files and keys are git-ignored and never pushed.
- **Least privilege** across services, database roles, and provider credentials.
- **Defence in depth** — validation, authorization, and rate limiting are applied
  at multiple layers, not a single gate.
- **Dependency hygiene** — automated vulnerability scanning in CI; pinned,
  reviewed dependencies.
- **Data minimisation** — the system stores what it needs to serve the user and
  no more; retention is bounded and documented.

---

## Where security meets the founding principles

- **Auditability** (a trust property) depends on the audit log defined here and in
  [`ARCHITECTURE.md`](ARCHITECTURE.md).
- **Honesty on failure** extends to security: when an operation cannot be
  performed safely, the system refuses and says so — it does not silently proceed.
- **Privacy-first** reinforces "transparency over persuasion": the user's data is
  used to serve the user, never to manipulate them.

> A platform that asks to be trusted with someone's financial life must earn that
> trust at the security layer first. Everything else is built on top of it.
