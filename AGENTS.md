<!-- graphcode:start -->
# GraphCode — Code Intelligence

This project is indexed by GraphCode as **security-agent** (786 symbols, 1204 relationships). Use GraphCode graph tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .graphcode/run.cjs analyze --index-only` from the project root — it auto-selects an available runner. No `.graphcode/run.cjs` yet? Install from source (`npm link` in the repo) or `npm i -g graphcode-cli` once published — then `graphcode analyze`.

## Always Do

- **MUST run impact analysis before editing.** Use `impact({name: "symbolName", direction: "upstream"})` (MCP) or `node .graphcode/run.cjs impact --name "symbolName" --direction upstream` (CLI); report callers and risk. Never substitute grep for graph analysis.
- **MUST analyze graph changes before committing.** Use `detect_changes({scope: "all"})` (MCP) or `node .graphcode/run.cjs detect-changes` (CLI). For a regression diff against a branch/commit: `detect_changes({base_ref: "main"})` (MCP; the CLI detects working-tree changes only).
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- **MUST treat `risk: UNKNOWN` as unresolved, not as low.** An empty caller set is not evidence the symbol is unused — it can also mean the callers are not resolvable by the index. Confirm with a text search before treating the symbol as safe to change or delete.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find the symbols that implement it instead of grepping.
- When you need full context on a specific symbol — callers, callees, references, file location — use `context({name: "symbolName"})`.
- When you need a symbol's role summarized, use `explain({name: "symbolName"})` (deterministic graph explanation; add `use_llm: true` for a natural-language summary).
- When you need the actual code of a symbol, use `read_file({file_path, start_line?, end_line?})` (MCP) — one call instead of an external file tool. Paths are repo-root-relative.
- Before trusting results after git operations (commit, branch switch, pull), check `repo_status({repo})` (MCP) — if it reports the index is stale, run a sync bundle first.
- Use `note_read` / `note_write` (MCP) as a per-repo scratchpad to persist task context across sessions.
- When you need intra-method data flow, use `pdg_query({name: "symbolName"})` — variable reads, callees, and callers/callees edges the parser observed (statement-level v1; control/data-flow across statements is not tracked yet).

## Never Do

- NEVER edit a function, class, or method before MCP/CLI impact analysis.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis, and never read `UNKNOWN` as an all-clear — it means the walk could not answer, which is the one verdict that requires confirming by other means.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit before MCP/CLI graph change analysis.

## Resources

| Resource | Use for |
| --- | --- |
| `graphcode://repo/security-agent/context` | Codebase overview, check index freshness |
| `graphcode://repo/security-agent/clusters` | All functional areas |
| `graphcode://repo/security-agent/processes` | All execution flows |
| `graphcode://repo/security-agent/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
| --- | --- |
| Understand architecture / "How does X work?" | `.claude/skills/graphcode-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/graphcode-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/graphcode-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/graphcode-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/graphcode-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/graphcode-cli/SKILL.md` |

<!-- graphcode:end -->
