# Tasks: Governed by default (GBD)

Each coder task is one PR, reviewed by a different agent. Ky merges. Tasks marked **Ky** are settings, tokens or
transfers; agents never do them (GBD-5). Order is dependency order. No code until Ky merges this spec.

- [ ] **K1. Ky: sweep token** (GBD-3.1, GBD-5.2). Create a token for the sweep (classic PAT: `repo`, `workflow`;
  admin on the target repos for protection) and store it as the `SWEEP_TOKEN` secret in `KyPython/ai-governance`.
  Then run the "Governance sweep" workflow once by hand.
- [ ] **K2. Ky: decide D1 and D2** (requirements.md, "Decisions for Ky"). Record them in a comment on #282.
- [ ] **K3. Ky: org ruleset** (GBD-1.1 to GBD-1.5). In `KyLamportLogic`, go to Settings, Rules, Rulesets, and
  confirm or create the ruleset (named `governance-mandatory` in `ky-new-repo`):
  - target all repositories and the default branch;
  - require a PR;
  - block force-push and deletion;
  - require the `ai-governance / verdict` status check;
  - if offered on the plan, require the workflow `KyPython/ai-governance/.github/workflows/governance.yml` at a
    pinned SHA;
  - set the bypass list per D2.

  Also fix `KyPython/odin-tasks`: remove `~ALL` from its `main` ruleset (GBD-1.5).
- [ ] **K4. Ky: restrict creation** (GBD-2.1). In `KyLamportLogic`, go to Settings, Member privileges, Repository
  creation, and allow owners only.
- [ ] **T1. Sweep repairs** (GBD-3.1 to GBD-3.5). Code PR to `scripts/sweep.sh` and `.github/workflows/sweep.yml`,
  with tests citing GBD IDs:
  - open or update an issue when the token is missing;
  - open or keep one bump PR per stale pin;
  - allow-list `.github/actions/*@*` next to the workflow pattern;
  - keep never merging, changing visibility, deleting, or changing rulesets.

  Depends on: spec merge.
- [ ] **T2. Status report and pinned issue** (GBD-4.1 to GBD-4.3). Code PR: the sweep writes a per-repo status
  report, keeps one pinned issue current, and names the blocking setting when a repo cannot take a PR. Depends
  on: T1.
- [ ] **T3. Creation path** (GBD-2.2, GBD-2.3). Code PR: `ky-new-repo` pins `main`'s SHA live, and its docs
  name it as the only supported way to create a repo. The sweep keeps `repo-starter`'s pin current. Depends on:
  T1.
- [ ] **T5. Creation preflight** (GBD-2.4, GBD-2.5). Code PR to `scripts/ky-new-repo` with tests citing GBD IDs:
  - check the org ruleset before `gh repo create`, and create nothing if it cannot be confirmed;
  - require `--allow-personal` for personal-account repos, and print the limit.

  Depends on: spec merge. K3 must be done before org creation succeeds, which is intended.
- [ ] **T4. README** (GBD-5.2). The three layers, the token scopes, and the personal-account limit. Can ride with
  T1.
- [ ] **K5. Ky: per D1**, move personal repos into `KyLamportLogic` one by one (Settings, Transfer), reconnecting
  integrations; or record that they stay personal and sweep-covered.

| Requirement | Tasks |
|---|---|
| GBD-1 | K2, K3 |
| GBD-2 | K4, T3, T5 |
| GBD-3 | K1, T1 |
| GBD-4 | T2 |
| GBD-5 | K1, K3, K4, K5, T4 |
