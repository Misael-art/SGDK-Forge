# FORGE_REFERENCE

Neutral SGDK 2.11 technical fixture used to demonstrate bounded runtime telemetry
contracts. It contains no branded assets and is not a game, vertical slice, or AAA
claim. Its canonical checks are run from the workspace root:

```text
python3 tools/sgdk_wrapper/ci/test_canonical_fixture_contracts.py
python3 tools/sgdk_wrapper/ci/test_project_learning_loop.py
```

`build_policy` is intentionally `disabled` in this main-compatible backport. The
fixture is source-and-contract reference only until the main branch gains the
portable SGDK route and a reproducible ROM build is recorded.
