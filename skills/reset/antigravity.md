# VibeWise Reset in Google Antigravity

These notes adapt VibeWise Reset tool and command names for Google Antigravity. Follow `SKILL.md` as written otherwise.

- **Paths**: `reset.py` sits in the same directory as this file (`skills/reset/reset.py`). Pass its resolved absolute path to `python -B` via `run_command`. The Learn guide is `../learn/SKILL.md` relative to this file; load it with `view_file`.
- **Commands**: Suggest `/vibe-wise:learn` or `"Activate VibeWise learning mode"` when no learning notes exist yet.
- **Confirmation Picker (`ask_question`)**: Use Antigravity's native `ask_question` tool (`is_multi_select: false`) with two options:
  - `Cancel — Keep learning notes`
  - `Reset learning — Back up notes and restart onboarding`
  If `ask_question` is unavailable, ask the same question in plain text and end your turn to wait for an explicit answer.
- **Replies**: Show the preview summary in chat first, then call `ask_question` once. Do not restate the confirmation after calling `ask_question` or quote internal plugin guides to the user.
