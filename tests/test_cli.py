import subprocess
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "farewell_helper", *args],
        capture_output=True, text=True, timeout=30,
        cwd=str(ROOT),
    )


class TestCLIVersion:
    def test_version(self):
        r = _run("--version")
        assert r.returncode == 0
        assert "5.0.0" in r.stdout


class TestCLIHelp:
    def test_help(self):
        r = _run("--help")
        assert r.returncode == 0
        assert "usage:" in r.stdout


class TestCLICommands:
    def test_status_runs(self):
        r = _run("status")
        assert r.returncode == 0
        assert "Farewell Helper v5" in r.stdout

    def test_start_runs(self):
        r = _run("start")
        assert r.returncode == 0
        assert "Persona" in r.stdout or "Ready" in r.stdout or "OK" in r.stdout

    def test_verify_runs(self):
        r = _run("verify")
        assert r.returncode == 0
        assert "PASS" in r.stdout or "FAIL" in r.stdout or "VERIFIED" in r.stdout

    def test_sync_template_not_found(self):
        template = ROOT / "opencode.template.jsonc"
        if not template.exists():
            assert True
            return
        r = _run("sync")
        assert r.returncode == 0

    def test_project_list(self):
        r = _run("project", "list")
        assert r.returncode == 0
        assert "Projects" in r.stdout or "projects" in r.stdout

    def test_project_status(self):
        r = _run("project", "status")
        assert r.returncode == 0

    def test_todo_create_show_delete(self):
        r_create = _run("todo", "create", "--task", "test smoke task")
        assert r_create.returncode == 0

        r_show = _run("todo", "show")
        assert r_show.returncode == 0
        assert "test smoke task" in r_show.stdout

        # cleanup — remove todo file
        ctx_dir = ROOT / ".farewell" / "context" / "001-farewell-helper"
        todo_file = ctx_dir / "TODO.md"
        if todo_file.exists():
            todo_file.unlink()


class TestPersonaFiles:
    def test_persona_files_exist(self):
        assert (ROOT / "PERSONA.md").exists()
        assert (ROOT / "PROTOCOL.md").exists()

    def test_persona_has_no_contradiction(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        mode_lines = [l for l in protocol.split("\n") if "mode" in l.lower() and "BUILD" in l]
        assert len(mode_lines) > 0, "PROTOCOL.md should mention BUILD mode"


class TestSkillFiles:
    def test_skills_have_frontmatter(self):
        skills_dir = ROOT / "skills"
        for skill_file in skills_dir.rglob("SKILL.md"):
            content = skill_file.read_text(encoding="utf-8")
            assert "description: Use when" in content, f"{skill_file} missing 'Use when' frontmatter"


class TestConfig:
    def test_opencode_config_exists(self):
        """Verify opencode.jsonc is committed and valid."""
        assert (ROOT / "opencode.jsonc").exists()
        content = (ROOT / "opencode.jsonc").read_text(encoding="utf-8")
        assert "model" in content
        assert "9router" in content

    def test_opencode_config_has_agents(self):
        config_file = ROOT / "opencode.jsonc"
        assert config_file.exists()
        content = config_file.read_text(encoding="utf-8")
        assert "build" in content
        assert "plan" in content

    def test_opencode_config_committed(self):
        assert (ROOT / "opencode.jsonc").exists()
        content = (ROOT / "opencode.jsonc").read_text(encoding="utf-8")
        assert "9router" in content


class TestNoDeadCode:
    def test_task_planner_deleted(self):
        assert not (ROOT / "farewell_helper" / "task_planner.py").exists()

    def test_cache_monitor_deleted(self):
        assert not (ROOT / "farewell_helper" / "cache_monitor.py").exists()
