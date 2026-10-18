# VibeWise in Google Antigravity

These notes adapt VibeWise tool and command names for Google Antigravity (IDE, 2.0 App, and `agy` CLI). They don't change the learning behavior; follow `SKILL.md` and its guides as written.

- **Commands**: Users can activate learning mode with `/vibe-wise:learn`, `vibe-wise learn`, or `"Activate VibeWise learning mode"`. Users can reset learning notes with `/vibe-wise:reset`, `vibe-wise reset`, or `"Reset VibeWise learning notes"`. Do not confuse `/vibe-wise:learn` with Antigravity's built-in `/learn` slash command.
- **Paths**: The plugin root is two directories above this file (`skills/learn/`). Guides such as `behavior.md`, `onboarding.md`, and `state-templates.md` sit beside this file in `skills/learn/`.
- **Reading & Searching Files**:
  - Where the guides say `Read`, use `view_file`.
  - Where the guides say `Glob`, use `find_by_name` (or check existence cleanly) to discover optional `.vibe-wise/` files before reading them with `view_file`.
  - Use `grep_search` on `progress.md` to locate `## Pending decision` and relevant topic sections across large progress histories.
  - When updating `.vibe-wise/profile.md`, `.vibe-wise/progress.md`, or `.vibe-wise/project-map.md`, use `write_to_file` (with `Overwrite: true` for initial creation) or `replace_file_content` for targeted edits. Always write these files inside the project's `.vibe-wise/` directory, never in the conversation's artifact directory.
- **Interactive Choices (`ask_question`)**:
  - Where the guides say `AskUserQuestion`, use Antigravity's native `ask_question` tool (`is_multi_select: false`).
  - Pass a single question in `questions` with 2–4 options. Format options as `"Label — brief description"` (for example, `"Confirm and continue — This approach makes sense to me; move to the next piece."` and `"Discuss — Ask questions or clarify anything that doesn't make sense before deciding."`).
  - Do not add an `"Other"` option—Antigravity's `ask_question` UI provides a write-in field automatically.
  - Never use `ask_question` for open-ended reasoning questions (`✦ Build checkpoint`). Ask open-ended reasoning questions in normal chat Markdown and end your turn to wait for the learner's response.
- **Session Restoration (`hooks.json`)**:
  - Antigravity runs `hooks/session_start.py` on `PreInvocation`. When `.vibe-wise/profile.md` has `Learning mode: active`, the hook injects a transient `ephemeralMessage` on the first invocation of a turn (`invocationNum == 1`) reminding the agent to load `skills/learn/SKILL.md` and the project's `.vibe-wise/` notes.
- **Replies**:
  - Present each checkpoint or question once, at the end of your reply. For Design and Implementation checkpoints, write the checkpoint summary in chat first, then call `ask_question`. Don't restate the question after calling `ask_question` or quote internal plugin guides to the learner.
