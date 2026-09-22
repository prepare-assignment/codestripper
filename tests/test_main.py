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


@pytest.fixture
def unexpected_files(project: Path) -> Path:
    (project / "solution" / "src" / "A.class").write_bytes(b"\xca\xfe\xba\xbe\x00\x00\xff\xfe")
    (project / "solution" / "src" / "data.foo").write_text("data\n")
    return project


@pytest.mark.parametrize("option, value, file", [
    ("binary", "FAIL", "A.class"), ("binary", "fail", "A.class"),
    ("unknown", "FAIL", "data.foo"), ("unknown", "fail", "data.foo"),
])
def test_fail(option: str, value: str, file: str, unexpected_files: Path, monkeypatch: pytest.MonkeyPatch,
              mocker: pytest_mock.MockerFixture) -> None:
    """FAIL (the default) used to behave like INCLUDE: the file was copied without any error"""
    set_inputs(monkeypatch, include=[f"src/{file}"], working_directory="solution", **{option: value})
    mocker.patch("prepare_codestripper.main.set_output")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_called_once()


@pytest.mark.parametrize("option, file", [("binary", "A.class"), ("unknown", "data.foo")])
def test_ignore(option: str, file: str, unexpected_files: Path, monkeypatch: pytest.MonkeyPatch,
                mocker: pytest_mock.MockerFixture) -> None:
    """IGNORE used to behave like INCLUDE: the file was copied"""
    set_inputs(monkeypatch, include=["src/A.java", f"src/{file}"], working_directory="solution", **{option: "IGNORE"})
    set_output = mocker.patch("prepare_codestripper.main.set_output")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_not_called()
    assert not (unexpected_files / "out" / "src" / file).exists()
    set_output.assert_any_call("stripped-files", ["src/A.java"])


@pytest.mark.parametrize("option, file", [("binary", "A.class"), ("unknown", "data.foo")])
def test_include(option: str, file: str, unexpected_files: Path, monkeypatch: pytest.MonkeyPatch,
                 mocker: pytest_mock.MockerFixture) -> None:
    set_inputs(monkeypatch, include=[f"src/{file}"], working_directory="solution", **{option: "INCLUDE"})
    mocker.patch("prepare_codestripper.main.set_output")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_not_called()
    source = unexpected_files / "solution" / "src" / file
    assert (unexpected_files / "out" / "src" / file).read_bytes() == source.read_bytes()


@pytest.mark.parametrize("option", ["binary", "unknown"])
def test_invalid_value(option: str, unexpected_files: Path, monkeypatch: pytest.MonkeyPatch,
                       mocker: pytest_mock.MockerFixture) -> None:
    set_inputs(monkeypatch, include=["src/A.java"], working_directory="solution", **{option: "SKIP"})
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_called_once()
    message = str(failed.call_args.args[0])
    assert f"Invalid value 'SKIP' for '{option}'" in message
    assert "FAIL, IGNORE, INCLUDE" in message


def test_comments_for_unknown_extension(project: Path, monkeypatch: pytest.MonkeyPatch,
                                        mocker: pytest_mock.MockerFixture) -> None:
    (project / "solution" / "run.xyz").write_text("keep\nsecret #cs:remove\n")
    set_inputs(monkeypatch, include=["run.xyz"], working_directory="solution", comments=[".xyz:#"])
    mocker.patch("prepare_codestripper.main.set_output")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_not_called()
    assert (project / "out" / "run.xyz").read_text() == "keep\n"


def test_comments_with_open_and_close(project: Path, monkeypatch: pytest.MonkeyPatch,
                                      mocker: pytest_mock.MockerFixture) -> None:
    (project / "solution" / "page.html").write_text("<p>keep</p>\n<p>secret</p> <!--cs:remove-->\n")
    set_inputs(monkeypatch, include=["page.html"], working_directory="solution", comments=[".html:<!--:-->"])
    mocker.patch("prepare_codestripper.main.set_output")
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_not_called()
    assert (project / "out" / "page.html").read_text() == "<p>keep</p>\n"


def test_comments_override_builtin_extension(project: Path, monkeypatch: pytest.MonkeyPatch,
                                             mocker: pytest_mock.MockerFixture) -> None:
    """With '.java:#', '//cs:' is no longer a tag and the file is copied unchanged"""
    set_inputs(monkeypatch, include=["src/A.java"], working_directory="solution", comments=[".java:#"])
    mocker.patch("prepare_codestripper.main.set_output")
    strip()
    assert (project / "out" / "src" / "A.java").read_text() == JAVA


def test_invalid_comments(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockerFixture) -> None:
    set_inputs(monkeypatch, include=["src/A.java"], working_directory="solution", comments=["//"])
    failed = mocker.patch("prepare_codestripper.main.set_failed")
    strip()
    failed.assert_called_once()
    assert "Invalid comment '//'" in str(failed.call_args.args[0])
