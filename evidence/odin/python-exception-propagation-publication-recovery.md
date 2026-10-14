# Python exception-propagation publication recovery

This record covers only publication-evidence recovery for Bootcamp row
`3f38621e-0a7a-8149-8dd1-c3e0ef4bff3d`. It does not copy, regenerate, repair,
or modify the starter source.

## Recovery status

```json
{
  "ODIN_STARTER_PUBLICATION_BLOCKER": {
    "source_repo": "KyPython/python-exception-propagation",
    "commit": "ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2",
    "branch": "feat/odin-python-exception-starter",
    "pr_title": "feat(odin): add Python exception propagation starter world",
    "pr_url": null,
    "manifest_status": "pending",
    "blocker": "This worker has no GitHub authentication. The named private repository returns HTTP 404 anonymously, and git cannot read it without credentials. Therefore this worker cannot enumerate or base64-encode the starter files, verify their byte identity at the named commit, discover a real existing PR URL, or run the published commit's ordinary-path baseline. An ODIN_STARTER_MANIFEST is intentionally not asserted until an authorized worker can verify all required evidence."
  }
}
```

The requested `ODIN_STARTER_MANIFEST` remains pending. In particular, an empty
file list would not satisfy the requirement to include every exact UTF-8 starter
file and would falsely imply that byte verification occurred.

## Verification attempts

Run on 2026-10-08 from the publication-recovery worker:

```text
$ gh auth status
You are not logged into any GitHub hosts.

$ git ls-remote https://github.com/KyPython/python-exception-propagation.git ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2
fatal: could not read Username for 'https://github.com': No such device or address
exit=128

$ curl https://api.github.com/repos/KyPython/python-exception-propagation/commits/ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2
http_status=404
response={"documentation_url":"https://docs.github.com/rest/commits/commits#get-a-commit","message":"Not Found","status":"404"}

$ curl https://github.com/KyPython/python-exception-propagation
http_status=404
```

No baseline result is reported: running a locally reconstructed or duplicate
starter would violate the recovery instruction and would not verify the
published immutable commit.

## Required authorized follow-up

An authenticated worker with read access to the private source repository must:

1. fetch exactly commit `ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2`;
2. enumerate every UTF-8 starter file and verify each byte sequence against that
   commit before encoding it as `content_b64`;
3. run the existing ordinary-path baseline from that checkout and record the
   exact command and result without adding decisive repair tests; and
4. verify and report an existing real GitHub PR URL, or retain `pr_url: null`
   with the specific publication blocker.

Human recording, review, transfer, admission, diagnosis, implementation, and
repair decisions remain untouched.
