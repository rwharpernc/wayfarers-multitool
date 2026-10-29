# Wayfarer's Multitool: working notes

- Tests run only in Docker: `npm run test:docker`. Do not run the suite natively.
- Documentation must match the code. Before finishing any change that touches a screen, setting, file, module or behavior, follow "Keeping the docs current" in `docs/DEVELOPMENT.md` and run `python scripts/check_docs.py` until it reports 0 problems. The pre-commit hook and `tests/test_docs_current.py` enforce the same checks.
- New or renamed screen labels, Settings tabs, files and modules must be reflected in the guides in `docs/guide/`, `docs/MODULES.md`, `CHANGELOG.md` and `docs/guide/planned.md` (move built items out) in the same change.
- Names that are not WFMT's (game, Discord, GitHub, EDMC) go in `docs/doc_terms.txt` with a comment, never as a way to silence a real mismatch.
- American English; no AI credit in commits or files; ask before committing, bumping a version or releasing.
