# Citation Enhancements (Client Build)

Built on upstream Open WebUI **v0.6.36**, this branch introduces inline citation improvements, build tweaks, and deployment helpers. The list below documents every file that diverges from the stock upstream release so another team can re-apply or maintain the changes when upgrading.

## Modified / Added Files

| Path | Purpose of Change |
| --- | --- |
| `Dockerfile` | Sets `SKIP_PYODIDE_FETCH=1` during the frontend build stage so Docker builds do not attempt to download large Pyodide bundles (which often fail in restricted builders). |
| `package.json`, `package-lock.json` | No dependency changes—only updated to align with the locally rebuilt lockfile after the citation work. Keep in sync if upstream changes deps. |
| `scripts/prepare-pyodide.js` | Honors env var `SKIP_PYODIDE_FETCH=1` by exiting early. This prevents unnecessary Pyodide downloads when the env var is set. |
| `docker-compose.coolify.yaml` | Client-specific compose file used by Coolify deployments (port exposure, env vars, volumes). |
| `src/lib/utils/citations.ts` *(new)* | Normalizes backend `sources` arrays, extracts page metadata, and builds document URLs (`/api/files/{file_id}/content#page=`). |
| `src/lib/utils/index.ts` | Updates `replaceTokens()` to convert inline markers `[1]`, `†1`, and `†(1:p25)` into `<source_id>` tags that carry citation index and optional page hints. This is the core parser update. |
| `src/lib/components/chat/Messages/types.ts` *(new)* | Defines `CitationLinkTarget` shape shared between `ContentRenderer` and Markdown components. |
| `src/lib/components/chat/Messages/ContentRenderer.svelte` | Normalizes citations via `normalizeCitations()`, builds `citationSourceIds` + `citationTargets`, and passes them into `Markdown`. Also imports `extractPageInfo` for per-page lookups. |
| `src/lib/components/chat/Messages/Markdown.svelte` | Accepts the `sourceTargets` prop and threads it into the Markdown renderer. |
| `src/lib/components/chat/Messages/Markdown/MarkdownTokens.svelte` | Propagates `sourceTargets` down into inline token renderer + HTML tokens. |
| `src/lib/components/chat/Messages/Markdown/MarkdownInlineTokens.svelte` | Mirrors the prop plumbing for inline tokens. |
| `src/lib/components/chat/Messages/Markdown/HTMLToken.svelte` | Ensures `<source_id …>` custom elements render via the `Source` component with the correct targets. |
| `src/lib/components/chat/Messages/Markdown/Source.svelte` | Renders the dagger chip (`†n`) and each page label. Clicking a page label uses the URL resolved from `CitationLinkTarget.pageTargets`; falls back to the citation modal if no file link exists. |
| `src/lib/components/chat/Messages/Markdown/MarkdownInlineTokens/TextToken.svelte` | Minor adjustments to allow inline dagger chips to render correctly (ensures they are treated as HTML tokens). |
| `jansen-docs/citation-fixes.md`, `jansen-docs/setup.md` | Documentation for the client team (this file + deployment/setup guidance). |

## Behavior Summary

1. **Citation normalization**: `ContentRenderer.svelte` calls `normalizeCitations(sources)` and builds two arrays:
   - `sourceIds`: human-readable labels displayed by Markdown.
   - `sourceTargets`: array of `{ defaultTarget, pageTargets }` describing each citation’s link(s).
2. **Inline parsing**: During Markdown preprocessing (`src/lib/utils/index.ts`), any `[1]`, `†1`, or `†(1:p25)` sequences outside code fences become `<source_id data="1" title="…" data-page="p25" />`.
3. **Rendering**: The Markdown renderer treats `<source_id>` as an HTML token and passes it to `Source.svelte`. That component renders a dagger button (`†1`) plus clickable page links (e.g., `p20`, `p27`). Each link opens the underlying PDF page when possible; otherwise it calls the citation modal.
4. **Build/deploy**: Docker builds run `npm run build` with `SKIP_PYODIDE_FETCH=1` to avoid Pyodide downloads. Coolify deployments reference `docker-compose.coolify.yaml` included here.

## Upgrading to Future Releases

1. Start from the new upstream tag/branch (e.g., `git checkout upstream/v0.6.37`).
2. Copy or cherry-pick the files listed above onto the new base.
3. Run `npm install && npm run build` to confirm the frontend compiles.
4. Update `package-lock.json` only if dependency versions changed.
5. Update this documentation with any additional files touched.

Keeping this table current will make future upgrades straightforward—if a file is not listed here, it should match the upstream release verbatim.
