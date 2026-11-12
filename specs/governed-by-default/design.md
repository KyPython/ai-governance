# Design: Governed by default (GBD)

Complements `requirements.md`. Status: proposed with the spec-only PR.

## Three layers

1. **Prevention (org):** An org ruleset requires `ai-governance / verdict` on every repo's default branch,
   including repos created later (GBD-1), and only org owners may create repos (GBD-2.1). A new repo cannot
   merge anything until its caller is in place and the verdict passes. Where the plan supports "Require
   workflows", the ruleset runs the workflow even with no caller file (GBD-1.3).
2. **Creation path:** `ky-new-repo` from the `repo-starter` template creates repos with the caller, the
   `AGENTS.md` section and `CODEOWNERS` already present (GBD-2.2).
3. **Detection and repair (everything, including the personal account):** A daily sweep with a working token:
   - opts repos in;
   - bumps stale pins;
   - fixes Actions allow-lists for every `ai-governance` path;
   - reports every repo's status to a pinned issue (GBD-3, GBD-4).

   This is the only layer that reaches `KyPython`'s personal repos, unless D1 moves them into the org.

## Why the personal account cannot be prevented

GitHub offers no account-wide ruleset and no creation hook for personal accounts. D1 is therefore a real choice:
move repos into the org (prevention), or accept detection within a day (sweep).

## Risks

- **A repo-wide outage.** If the gate itself breaks, an org ruleset with no bypass blocks every merge in every
  repo. D2 decides the escape hatch.
- **Breaking third-party links.** Moving a repo changes its URL. GitHub redirects git and web traffic, but
  integrations such as Vercel, Cloudflare, Pages and Snyk may need reconnecting. Each move is Ky's.
- **Bump PRs exposing real failures.** A bump PR runs the new gate on the repo. If a repo was only passing
  because of the old gate, the bump fails, as `ky-cloud-control-plane#8` (a non-Linux OPA binary) does. The
  sweep reports it and does not loosen anything.
