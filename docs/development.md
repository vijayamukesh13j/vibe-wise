# Development

VibeWise for Google Antigravity uses Antigravity plugin manifests (`plugin.json`),
skills (`skills/learn/`, `skills/reset/`), rules (`rules/AGENTS.md`), one read-only
Python `PreInvocation` hook (`hooks.json` -> `hooks/session_start.py`), and a small
Python helper for confirmed learning resets (`skills/reset/reset.py`).
There are no external packages to install. Python 3.8+ is sufficient for the hook and tests.

## Local checks

```sh
python -B -m unittest discover -s tests -v
git diff --check
```

The unit tests execute the registered hook command (`hooks.json` and `hooks/hooks.json`)
with real JSON `stdin` in temporary projects. They cover:

- Antigravity `PreInvocation` restoration (`injectSteps` with `ephemeralMessage`)
- `file://` workspace URIs and plain filesystem paths
- Skipping duplicate injections on `invocationNum > 1` within the same turn
- Returning `{}` cleanly on inactive or paused projects
- Activation, restoration, partial onboarding, paused mode, subdirectories, and
  repository/worktree boundaries
- Legacy `.sensible-vibes/` restoration without migration
- Missing/invalid files, symlinks, constant-size restoration instructions as notes
  grow, and read-only hook behavior
- `reset.py` read-only preview, confirmed backup/reset, stale confirmation rejection,
  legacy and partial notes, nested projects, repeated backups, rejected symlinks,
  backup/write failures, and restoring incomplete onboarding after reset

## Manual conversation checks in Antigravity

Install the plugin into `~/.gemini/config/plugins/vibe-wise/` (global) or
`.agents/plugins/vibe-wise/` (workspace) and restart Antigravity.

For a manual walkthrough based on the playground notes app, see the
[Notion-style demo](demos/notion-dupe.md).

1. **Fresh project:** Run `/vibe-wise:learn` (or `"Activate VibeWise learning mode"`).
   Choose a new project, describe a small CLI, and accept preference defaults.
   Check that all three state files (`profile.md`, `progress.md`, `project-map.md`)
   are created inside `.vibe-wise/`, the map separates proposed from implemented
   components, and no understanding is marked demonstrated without evidence.
   Choice questions must use Antigravity's native `ask_question` modal with one
   question at a time.
2. **Existing unfamiliar repository:** Use a copy of a real repository. Choose the
   existing-repository flow. Confirm Antigravity reads actual entry points and
   configuration, gives an accurate short map before familiarity questions, asks
   whole-system versus focused scope, and doesn't invent a frontend or database.
3. **Checkpoint → implementation:** Ask for a meaningful feature, such as durable
   storage or retrying an external request. Confirm Antigravity asks one open-ended
   reasoning question under `✦ Build checkpoint: <decision>` before suggesting its
   own solution or implementing the decision. Give a partial answer; check that it
   refines the answer, names the coding scope in an `✦ Implementation checkpoint`,
   and offers **Implement this step** / **Discuss** via `ask_question`.
4. **Skip and adaptation:** Say “I'm completely lost.” Confirm Antigravity explains
   the relevant pieces using `✦ Concept` / `✦ Why this matters` and returns one
   manageable reasoning step without dumping a complete plan.
5. **Lifecycle:** Start a new conversation or `/compact`. Confirm `PreInvocation`
   restores preferences, the map, and pending checkpoints without repeating onboarding.
   Pause learning, start a new session, and confirm it stays paused until
   `/vibe-wise:learn` is invoked again.
6. **Reset:** In a project with saved learning notes, invoke `/vibe-wise:reset`.
   Confirm it runs the read-only preview, shows the absolute project and state paths,
   and asks **Cancel** / **Reset learning** via `ask_question`. Confirming backs up
   all three notes under `.vibe-wise/backups/` and restarts fresh onboarding.
