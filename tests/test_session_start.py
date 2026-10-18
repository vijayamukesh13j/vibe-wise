"""Exercise the actual hook command in isolated new and existing projects."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGY_CONFIG = json.loads((ROOT / "hooks.json").read_text(encoding="utf-8"))
AGY_HANDLER = AGY_CONFIG["vibe-wise-restore"]["PreInvocation"][0]
CLAUDE_CONFIG = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
CLAUDE_REGISTRATION = CLAUDE_CONFIG["hooks"]["SessionStart"][0]


class SessionStartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="vibe-wise-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / "project with spaces"
        self.project.mkdir()
        (self.project / ".git").mkdir()

    def state(self, project=None, mode="active"):
        directory = (project or self.project) / ".vibe-wise"
        directory.mkdir()
        (directory / "profile.md").write_text(
            f"# Learner Profile\nLearning mode: {mode}\nOnboarding: complete\n"
            "Checkpoint frequency: Light\nQuestion style: Open-ended\n"
            "Implementation style: AI writes code\n"
            "Strong concepts: HTTP request flow\n", encoding="utf-8"
        )
        (directory / "project-map.md").write_text(
            "# Project Map\nCLI → service.py → SQLite\n", encoding="utf-8"
        )
        (directory / "progress.md").write_text(
            "# Learning Progress\n## Transactions\n"
            "Demonstrated understanding: two writes must succeed together.\n"
            "## Queues\nNeeds reinforcement: retries.\n", encoding="utf-8"
        )
        return directory

    def _exec_hook_cmd(self, command, payload):
        env = os.environ.copy()
        env["PATH"] = os.pathsep.join((str(Path(sys.executable).parent), env.get("PATH", os.defpath)))
        env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
        result = subprocess.run(
            command, shell=True,
            input=payload, text=True, capture_output=True, timeout=5,
            # Antigravity sets the working directory of hook commands to the
            # directory containing hooks.json (the plugin root).
            env=env, cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout) if result.stdout else None

    def run_hook(self, cwd=None, source="startup", raw=None):
        payload = raw if raw is not None else json.dumps({
            "hook_event_name": "SessionStart", "source": source,
            "cwd": str(cwd or self.project),
        })
        return self._exec_hook_cmd(CLAUDE_REGISTRATION["hooks"][0]["command"], payload)

    def run_agy_hook(self, workspace_paths=None, invocation_num=1, raw=None):
        if raw is None:
            paths = [str(self.project)] if workspace_paths is None else workspace_paths
            payload = json.dumps({
                "conversationId": "e11f1f52-7ce5-43a8-8e9c-b442282a10d9",
                "workspacePaths": paths,
                "invocationNum": invocation_num,
                "initialNumSteps": 2,
                "modelName": "auto",
            })
        else:
            payload = raw
        return self._exec_hook_cmd(AGY_HANDLER["command"], payload)

    def context(self, **kwargs):
        result = self.run_hook(**kwargs)["hookSpecificOutput"]
        self.assertEqual(result["hookEventName"], "SessionStart")
        return result["additionalContext"]

    def agy_context(self, **kwargs):
        result = self.run_agy_hook(**kwargs)
        self.assertIn("injectSteps", result)
        self.assertEqual(len(result["injectSteps"]), 1)
        return result["injectSteps"][0]["ephemeralMessage"]

    def test_antigravity_pre_invocation_restores_active_project(self):
        self.state()
        context = self.agy_context()
        self.assertIn(str(ROOT / "skills/learn/SKILL.md"), context)
        self.assertIn(str(self.project / ".vibe-wise"), context)
        self.assertIn("view_file", context)
        self.assertIn("Read profile.md and project-map.md", context)
        self.assertIn("Search the entire progress.md", context)

    def test_antigravity_pre_invocation_supports_file_uri_workspace(self):
        self.state()
        uri = self.project.as_uri()
        context = self.agy_context(workspace_paths=[uri])
        self.assertIn(str(self.project / ".vibe-wise"), context)

    def test_antigravity_pre_invocation_skips_subsequent_invocations_in_turn(self):
        self.state()
        self.assertEqual(self.run_agy_hook(invocation_num=2), {})
        self.assertEqual(self.run_agy_hook(invocation_num=5), {})

    def test_antigravity_fresh_or_paused_project_returns_empty_json_object(self):
        self.assertEqual(self.run_agy_hook(), {})
        self.state(mode="paused")
        self.assertEqual(self.run_agy_hook(), {})

    def test_fresh_project_is_inactive_and_hook_writes_nothing(self):
        self.assertIsNone(self.run_hook())
        self.assertEqual(list(self.project.iterdir()), [self.project / ".git"])

    def test_restore_all_registered_session_lifecycles(self):
        self.state()
        for source in ("startup", "resume", "clear", "compact", "fork"):
            with self.subTest(source=source):
                self.assertTrue(re.fullmatch(CLAUDE_REGISTRATION["matcher"], source))
                context = self.context(source=source)
                self.assertIn(str(ROOT / "skills/learn/SKILL.md"), context)
                self.assertIn(str(self.project / ".vibe-wise"), context)
                self.assertIn("Read profile.md and project-map.md", context)
                self.assertIn("Search the entire progress.md", context)
                self.assertNotIn("Checkpoint frequency: Light", context)
                self.assertNotIn("two writes must succeed together", context)

    def test_existing_repo_restores_from_nested_working_directory(self):
        self.state()
        nested = self.project / "src" / "services"
        nested.mkdir(parents=True)
        (nested / "service.py").write_text("def run():\n    return 'ok'\n", encoding="utf-8")
        self.assertIn(str(self.project / ".vibe-wise"), self.context(cwd=nested))
        self.assertIn(str(self.project / ".vibe-wise"), self.agy_context(workspace_paths=[str(nested)]))

    def test_no_git_project_restores(self):
        project = self.root / "fresh-no-git"
        project.mkdir()
        self.state(project)
        self.assertIn(str(project / ".vibe-wise"), self.context(cwd=project))
        self.assertIn(str(project / ".vibe-wise"), self.agy_context(workspace_paths=[str(project)]))

    def test_no_git_project_ignores_parent_folder_notes(self):
        parent = self.root / "documents"
        project = parent / "throwaway" / "plain-project"
        project.mkdir(parents=True)
        self.state(parent)
        self.assertIsNone(self.run_hook(cwd=project))
        self.assertEqual(self.run_agy_hook(workspace_paths=[str(project)]), {})
        empty = parent / "other"
        empty.mkdir()
        (empty / ".vibe-wise").mkdir()
        nested = empty / "plain"
        nested.mkdir()
        self.assertIsNone(self.run_hook(cwd=nested))

    def test_no_git_project_prefers_its_own_notes_over_parent_notes(self):
        parent = self.root / "documents"
        project = parent / "plain-project"
        project.mkdir(parents=True)
        self.state(parent, mode="paused")
        self.state(project)
        self.assertIn(str(project / ".vibe-wise"), self.context(cwd=project))

    def test_legacy_notes_restore_without_migration(self):
        state = self.state()
        legacy = state.with_name(".sensible-vibes")
        state.rename(legacy)
        before = {p.name: p.read_bytes() for p in legacy.iterdir()}
        context = self.context(source="compact")
        self.assertIn("VibeWise is active", context)
        self.assertIn(str(legacy), context)
        self.assertIn("Read profile.md and project-map.md", context)
        self.assertFalse(state.exists())
        self.assertEqual(before, {p.name: p.read_bytes() for p in legacy.iterdir()})

    def test_new_notes_take_precedence_over_legacy_at_same_location(self):
        self.state().rename(self.project / ".sensible-vibes")
        self.state(mode="paused")
        self.assertIsNone(self.run_hook())

    def test_nearest_legacy_notes_take_precedence_over_parent_notes(self):
        self.state()
        child = self.project / "package"
        child.mkdir()
        self.state(child, mode="paused").rename(child / ".sensible-vibes")
        self.assertIsNone(self.run_hook(cwd=child))

    def test_legacy_notes_respect_worktree_boundary(self):
        self.state().rename(self.project / ".sensible-vibes")
        child = self.project / "worktree"
        child.mkdir()
        (child / ".git").write_text("gitdir: /another/repo/.git/worktrees/test", encoding="utf-8")
        self.assertIsNone(self.run_hook(cwd=child))

    def test_symlinked_new_state_does_not_fall_back_to_legacy(self):
        self.state().rename(self.project / ".sensible-vibes")
        (self.project / ".vibe-wise").symlink_to(self.root / "missing", target_is_directory=True)
        self.assertIsNone(self.run_hook())

    def test_nested_repository_and_worktree_do_not_borrow_parent_profile(self):
        self.state()
        for name, git_is_file in (("nested-repo", False), ("worktree", True)):
            child = self.project / name
            child.mkdir()
            if git_is_file:
                (child / ".git").write_text("gitdir: /some/other/repo/.git/worktrees/test", encoding="utf-8")
            else:
                (child / ".git").mkdir()
            self.assertIsNone(self.run_hook(cwd=child))

    def test_nearest_state_wins(self):
        self.state()
        child = self.project / "package"
        child.mkdir()
        self.state(child, mode="paused")
        self.assertIsNone(self.run_hook(cwd=child))

    def test_paused_state_is_not_reactivated_by_compaction(self):
        self.state(mode="paused")
        self.assertIsNone(self.run_hook(source="compact"))

    def test_incomplete_onboarding_survives_restart(self):
        state = self.state()
        (state / "profile.md").write_text(
            "Learning mode: active\nOnboarding: incomplete\n"
            "Remaining onboarding: stack familiarity\n", encoding="utf-8"
        )
        context = self.context()
        self.assertIn(str(state), context)
        self.assertIn("If onboarding is incomplete", context)
        self.assertIn("ask only unanswered questions", context)

    def test_missing_map_and_progress_do_not_discard_preferences(self):
        state = self.state()
        (state / "project-map.md").unlink()
        (state / "progress.md").unlink()
        context = self.context()
        self.assertIn(str(state), context)
        self.assertIn("Discover optional files before reading", context)
        self.assertIn("Recreate missing notes only from evidence", context)

    def test_large_notes_do_not_change_bootstrap_or_hide_pending_restore(self):
        state = self.state()
        before = self.context(source="compact")
        with (state / "profile.md").open("a", encoding="utf-8") as stream:
            stream.write("a" * 100000)
        (state / "project-map.md").write_text("b" * 100000, encoding="utf-8")
        (state / "progress.md").write_text(
            "## Earlier learning\n" + "Older summary.\n" * 10000 +
            "## Pending decision\nAwaiting approval to implement SQLite.\n",
            encoding="utf-8"
        )
        context = self.context(source="compact")
        self.assertLess(len(context), 10000)
        self.assertEqual(context, before)
        self.assertIn("Search the entire progress.md", context)
        self.assertIn("read their complete sections", context)
        self.assertNotIn("Earlier learning", context)
        self.assertNotIn("SQLite", context)

    def test_paused_mode_beyond_old_profile_cutoff_is_respected(self):
        state = self.state()
        (state / "profile.md").write_text(
            "# Profile\n" + "Older preference.\n" * 1000 + "Learning mode: paused\n",
            encoding="utf-8"
        )
        self.assertIsNone(self.run_hook(source="compact"))

    def test_legacy_profile_without_mode_still_restores(self):
        state = self.state()
        (state / "profile.md").write_text("# Learner Profile\nExperience: Beginner\n", encoding="utf-8")
        self.assertIn(str(state), self.context())

    def test_malformed_inputs_exit_cleanly(self):
        for raw in ("", "{", "[]", "null", "42", '{"cwd": 4}',
                    '{"hook_event_name":"SessionStart","cwd":"relative"}'):
            with self.subTest(raw=raw):
                self.assertIsNone(self.run_hook(raw=raw))

    def test_unreadable_or_empty_profile_does_not_activate(self):
        state = self.state()
        for content in (b"", b" \n\t", b"\xff\xfe"):
            (state / "profile.md").write_bytes(content)
            self.assertIsNone(self.run_hook())

    def test_symlinked_profile_is_not_read(self):
        state = self.state()
        outside = self.root / "outside.md"
        outside.write_text("Learning mode: active\nPRIVATE", encoding="utf-8")
        (state / "profile.md").unlink()
        (state / "profile.md").symlink_to(outside)
        self.assertIsNone(self.run_hook())

    def test_symlinked_state_directory_is_not_read(self):
        state = self.state()
        alternate = self.root / "alternate"
        alternate.mkdir()
        (alternate / ".vibe-wise").symlink_to(state, target_is_directory=True)
        self.assertIsNone(self.run_hook(cwd=alternate))

    def test_hook_never_changes_state(self):
        state = self.state()
        before = {p.name: p.read_bytes() for p in state.iterdir()}
        self.run_hook(source="compact")
        self.run_agy_hook()
        after = {p.name: p.read_bytes() for p in state.iterdir()}
        self.assertEqual(before, after)

    def test_compaction_points_to_pending_decision_without_inventing_approval(self):
        state = self.state()
        with (state / "progress.md").open("a", encoding="utf-8") as stream:
            stream.write("## Pending decision\nUse SQLite. Awaiting Implement or a question.\n"
                         "- Pending decision: JSON storage; waiting for Implement.\n")
        context = self.context(source="compact")
        self.assertIn("Search the entire progress.md for pending decisions", context)
        self.assertIn("before coding", context)
        self.assertIn("await implementation approval", context)
        self.assertIn("Restarting or compacting is not approval", context)
        self.assertNotIn("Use SQLite", context)
        self.assertNotIn("JSON storage", context)


if __name__ == "__main__":
    unittest.main()
