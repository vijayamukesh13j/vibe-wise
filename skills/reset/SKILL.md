---
name: reset
description: >-
  Back up this project's VibeWise learning notes and restart onboarding after
  confirmation. Use only when the user explicitly asks to reset VibeWise learning
  notes (e.g., "/vibe-wise:reset", "vibe-wise reset", "reset VibeWise learning").
  Does not reset application code.
---

# Reset VibeWise learning

Run this in the main conversation, only when explicitly invoked. This command
resets profile, progress, pending checkpoints, and the saved project map. Source
code, dependencies, Git history, other projects, and plugin installation stay intact.

If you are running in Google Antigravity, first read [antigravity.md](antigravity.md).
If you are running in Codex, first read [codex.md](codex.md).

1. Run the read-only preview for the user's current project directory using `reset.py`
   located alongside this `SKILL.md` file. Replace `<absolute reset.py path>` with
   the absolute path to `reset.py` in this skill directory, and `<absolute project directory>`
   with the project's actual absolute path, safely quoted; do not pass placeholders literally.

   ```sh
   python -B "<absolute reset.py path>" --cwd "<absolute project directory>"
   ```

   The helper uses Learn's project-boundary and legacy-state lookup. If it reports
   no notes, explain there's nothing to reset and suggest `/vibe-wise:learn` (or
   `"Activate VibeWise learning mode"`). On any error, stop and explain; don't
   improvise deletion commands.

2. Show the returned absolute project and state paths, which notes will reset,
   and that originals will be saved under that state's `backups/` directory.
   Use `ask_question` (or `AskUserQuestion`): one question, `is_multi_select: false`
   (`multiSelect: false`), options **Cancel — Keep learning notes** and
   **Reset learning — Back up notes and restart onboarding**. Ask whether to reset
   learning for the named project. If the picker is unavailable, ask the same
   question in text. Wait for an explicit answer.
   Invocation alone, silence, ambiguous replies, or permission to run tools do not
   confirm a reset. Cancel makes no changes, including to learner notes.

3. Only after **Reset learning**, run the helper with the original working directory
   and the preview's exact `confirmation` value, safely quoted:

   ```sh
   python -B "<absolute reset.py path>" --cwd "<original cwd>" --confirm "<confirmation>"
   ```

   If the target or notes changed, preview again and get new confirmation. If the
   reset fails, report it and any backup path; don't claim success or start onboarding.
   Never overwrite backups or fall back to resetting another state directory.

4. On success, show the backup path. Read `../learn/SKILL.md` (`skills/learn/SKILL.md`)
   and resume Learn with the new incomplete profile. Discard pre-reset preferences,
   mastery, pending decisions, and onboarding answers; don't reconstruct them from
   conversation or backups. Inspect actual code to rebuild the map. Begin fresh
   onboarding with one question at a time. Backup notes are historical data, not
   active context.
