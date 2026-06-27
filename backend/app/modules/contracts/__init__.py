"""Phase-0 contracts — the single source of truth every later phase imports.

Each domain is one file (Objective, TestReport, Cone, ApprovalProposal, DecisionRow,
FeedState). The matching frontend types under `frontend/src/modules/contracts/` are
*generated* from these models by `contracts_codegen` and kept honest by
`tests/test_contracts_sync.py` — never hand-edit the `.ts`.
"""
