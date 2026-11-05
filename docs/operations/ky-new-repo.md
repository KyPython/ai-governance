# ky-new-repo

Create a new repository with the governance bundle and branch protection from day one.
Companion to `optin.sh` (existing repos) and `sweep.sh` (fleet audit) in
`KyPython/ai-governance/scripts/`.

## Usage

```bash
ky-new-repo [--org NAME | --user NAME] [--private | --public]
            [--template] [--dry-run] <name> [--description "..."] [--ci node|python|none]
```

| Flag | Meaning |
|---|---|
| `--org NAME` | Create under an org (default: `KyLamportLogic`) |
| `--user NAME` | Create under a user account (default owner if neither flag: org) |
| `--private` / `--public` | Visibility (default: `private`) |
| `--template` | Create from `KyPython/template`, then still pin the live SHA + protect |
| `--ci node\|python\|none` | Minimal `ci.yml` variant (default: `node`) |
| `--dry-run` | Print every command without executing anything (fully offline) |

```bash
ky-new-repo my-service --description "Does the thing"
ky-new-repo --user KyPython --public --ci python my-lib
ky-new-repo --dry-run my-service   # plan only, never touches the network
```

## What it does

1. Validates the name; refuses to run inside the shared checkout (`/Users/ky/...`).
2. `gh repo create` (wikis/projects disabled), then a fresh clone into
   `/tmp/ky-new-repo-<name>/`.
3. Resolves the pinned governance SHA **live** from `KyPython/ai-governance@main`.
4. Installs the bundle: caller workflow (pinned), `AGENTS.md` section, `CODEOWNERS`,
   PR template, optional minimal `ci.yml`. Initial commit
   `chore(repo): bootstrap <name> with governance bundle`, pushed (never force-pushed).
5. Protection: org repos inherit the `governance-mandatory` ruleset (verified active,
   plus a probe PR proving the verdict runs); user repos get a no-op PR and then
   `optin.sh --protect` once `ai-governance / verdict` is green (polls, exits
   non-zero with an `unresolved:` note if it never passes).
6. Re-fetches protection/ruleset state and prints the per-repo checklist.

The CLI never merges, approves, force-pushes, bypasses, deletes, or changes
visibility. Ky merges/closes the probe PR.

## Open decision (needs Ky)

Default owner (`KyLamportLogic` org) and default visibility (`private`) are
provisional: Ky's standing decision is pending (rollout design gap 7). Note that
private repos on a free plan cannot use classic branch protection (HTTP 403), so a
private default pairs with the org ruleset, not with per-repo protection.
