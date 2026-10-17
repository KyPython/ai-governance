# Parcel Indexer Infrastructure

This synthetic project defines the local infrastructure template for a small parcel-indexing worker. It uses only the Python standard library and never contacts a cloud account.

## Requirements

- Python 3.11 or newer

## Baseline

From this directory, synthesize the template:

```sh
python -m infra.synth --output build/template.json
```

Inspect the generated resource and policy document:

```sh
python -m json.tool build/template.json
```

Run the existing policy checks and tests:

```sh
python -m policy.validate build/template.json
python -m unittest discover -s tests -v
```

The workload contract is in `docs/workload-contract.md`. Keep generated files under `build/` out of source control.
