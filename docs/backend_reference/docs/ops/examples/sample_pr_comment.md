### Quick links
- PR: https://github.com/org/repo/pull/123
- Checks: https://github.com/org/repo/pull/123/checks
- Workflow run: https://github.com/org/repo/actions/runs/999999999

### Change since last report
**Transition:** CHECKS: worsened (0 -> 2 failing)

**Top blocker:** checks failing: `2` (top: `CI / unit (failure)` https://github.com/org/repo/actions/runs/999999999)
- actions added: `rerun_ci`, `collect_logs`
- actions removed: `merge`

| check | status | note |
|---|---|---|
| CI/unit | failure | flakes in test_x |
| Lint | success | - |
