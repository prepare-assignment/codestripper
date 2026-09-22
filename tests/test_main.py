import json
from pathlib import Path
from typing import Any, Dict

import pytest
import pytest_mock
import yaml

from prepare_codestripper.main import strip

TASK = Path(__file__).parent.parent / "task.yml"

JAVA = """public class A {
    public int answer() {
        //cs:replace:return 0;
        return 42;
    }
    //cs:remove:start
    private void solution() {}
    //cs:remove:end
}
"""

STRIPPED_JAVA = """public class A {
    public int answer() {
        return 0;
        return 42;
    }
}
"""


def set_inputs(monkeypatch: pytest.MonkeyPatch, **inputs: Any) -> None:
    """
    Pass the inputs like prepare-assignment core does: as JSON in PREPARE_<NAME> environment variables,
    including the defaults from task.yml. Use the names from task.yml, with '_' for '-'.
    """
    definition: Dict[str, Any] = yaml.safe_load(TASK.read_text(encoding="utf-8"))["inputs"]
    values = {name: spec["default"] for name, spec in definition.items() if "default" in spec}
    values.update({key.replace("_", "-"): value for key, value in inputs.items()})
    for key, value in values.items():
        if value is not None:
            monkeypatch.setenv(f"PREPARE_{key.upper()}", json.dumps(value))


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "solution" / "src").mkdir(parents=True)
    (tmp_path / "solution" / "src" / "A.java").write_text(JAVA)
    (tmp_path / "solution" / "src" / "B.java").write_text("class B {}\n")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_strip(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockerFixture) -> None:
    set_inputs(monkeypatch, include=["**/*.java"], working_directory="solution", output_directory="out/assignment")
    set_output = mocker.patch("prepare_codestripper.main.set_output")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_not_called()
    assert (project / "out" / "assignment" / "src" / "A.java").read_text() == STRIPPED_JAVA
    assert (project / "out" / "assignment" / "src" / "B.java").read_text() == "class B {}\n"
    set_output.assert_any_call("matched-files", ["src/A.java", "src/B.java"])
    set_output.assert_any_call("stripped-files", ["src/A.java", "src/B.java"])


def test_exclude(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockerFixture) -> None:
    set_inputs(monkeypatch, include=["**/*.java"], exclude=["**/B.java"], working_directory="solution")
    set_output = mocker.patch("prepare_codestripper.main.set_output")
    strip()
    assert (project / "out" / "src" / "A.java").is_file()
    assert not (project / "out" / "src" / "B.java").exists()
    set_output.assert_any_call("matched-files", ["src/A.java"])


def test_no_matches(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockerFixture) -> None:
    set_inputs(monkeypatch, include=["**/*.kt"], working_directory="solution")
    info = mocker.patch("prepare_codestripper.main.info")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    info.assert_called_once_with("No files matched")
    failed.assert_not_called()
    assert not (project / "out").exists()


def test_dry_run(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockerFixture) -> None:
    set_inputs(monkeypatch, include=["**/*.java"], working_directory="solution", dry_run=True)
    set_output = mocker.patch("prepare_codestripper.main.set_output")
    strip()
    assert not (project / "out").exists()
    set_output.assert_any_call("stripped-files", ["src/A.java", "src/B.java"])


@pytest.mark.parametrize("fail_on_error, should_fail", [(True, True), (False, False)])
def test_fail_on_error(fail_on_error: bool, should_fail: bool, project: Path, monkeypatch: pytest.MonkeyPatch,
                       mocker: pytest_mock.MockerFixture) -> None:
    (project / "solution" / "src" / "Invalid.java").write_text("class Invalid {\n//cs:remove:start\n}\n")
    set_inputs(monkeypatch, include=["**/Invalid.java"], working_directory="solution", fail_on_error=fail_on_error)
    mocker.patch("prepare_codestripper.main.set_output")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    assert failed.called == should_fail
