# VibeWise Plugin Rules

VibeWise is a learning-first development plugin (`vibe-wise`).

- **Activation boundary**: Installing or enabling this plugin does **not** activate learning mode in every project automatically. Learning mode is only active when:
  1. The user explicitly invokes VibeWise learning (for example: `/vibe-wise:learn`, `vibe-wise learn`, `"Activate VibeWise learning mode"`, or `"Resume VibeWise"`), OR
  2. The current project has an existing `.vibe-wise/profile.md` (or legacy `.sensible-vibes/profile.md`) with `Learning mode: active` (which is also restored via the `PreInvocation` hook).
- **Commands & Skill Routing**:
  - When the user types `/vibe-wise:learn`, `vibe-wise learn`, or asks to start/resume VibeWise learning mode, activate and follow the `learn` skill (`skills/learn/SKILL.md`). Do not confuse `/vibe-wise:learn` with the built-in `/learn` slash command.
  - When the user types `/vibe-wise:reset`, `vibe-wise reset`, or asks to reset VibeWise learning notes, activate and follow the `reset` skill (`skills/reset/SKILL.md`).
