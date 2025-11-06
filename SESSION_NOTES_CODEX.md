# Session Notes (Codex)

- Restored inline citations to modal-only behavior by reverting `ContentRenderer.svelte`, `Markdown/Source.svelte`, and `utils/index.ts` to the version on `dev/custom-gpt-interface` (commit 4f9e696).
- Modal improvements (sorted by page, markdown styling, link badge) remain live.
- Branch `status` deleted; `dev/custom-gpt-interface` already held its changes.
- `dev/modal-citation-formatting` currently matches `dev/custom-gpt-interface` for inline citation handling; only the modal enhancements differ.
- Build reminder: `npm run dev` / `npm run build` can stall on Pyodide (seaborn). Set `SKIP_PYODIDE=1` if needed during testing.
