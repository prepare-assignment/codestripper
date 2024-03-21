from typing import Any

import pytest
import pytest_mock

from prepare_codestripper.main import strip


def test_inputs(mocker: pytest_mock.MockerFixture) -> None:
    """
    This basically only tests that all params are passed correctly.
    The main work is done by the codestripper itself

    :param mocker: mocker
    :return:
    """
    include = ["a.txt", "b.txt"]
    exclude = ["c.txt"]
    working_directory = "solution"
    allow_outside = False
    output_directory = "out"
    recursive = True
    verbosity = 3
    dry_run = False
    comment = "//"
    matched_files = ["a.txt"]


    def __get_input(key: str, required: bool = False) -> Any:
        if key == "include":
            return include
        elif key == "exclude":
            return exclude
        elif key == "working-directory":
            return working_directory
        elif key == "allow-outside-working-directory":
            return allow_outside
        elif key == "output-directory":
            return output_directory
        elif key == "recursive":
            return recursive
        elif key == "verbosity":
            return verbosity
        elif key == "dry-run":
            return dry_run
        elif key == "comment":
            return comment
        elif key == "fail-on-error":
            return True

    mocker.patch("prepare_codestripper.main.get_input", side_effect=__get_input)
    mocked_matching_files = mocker.patch("prepare_codestripper.main.get_matching_files", return_value=matched_files)
    mocked_strip_files = mocker.patch("prepare_codestripper.main.strip_files")
    mocked_set_output = mocker.patch("prepare_codestripper.main.set_output")

    strip()

    mocked_matching_files.assert_called_once_with(include, exclude, allow_outside_working_dir=allow_outside,
                                                  relative_to=working_directory, recursive=recursive,)
    mocked_strip_files.assert_called_once_with(matched_files, working_directory=working_directory, comment=comment,
                                               output=output_directory, dry_run=dry_run, fail_on_error=True)
    assert mocked_set_output.call_count == 2


def test_no_matches(mocker: pytest_mock.MockerFixture) -> None:
    """
    Test that it fails if no files match

    :param mocker: mocker
    :return:
    """
    include = ["a.txt", "b.txt"]
    exclude = ["c.txt"]
    working_directory = "solution"
    allow_outside = False
    output_directory = "out"
    recursive = True
    verbosity = 3
    dry_run = False
    comment = "//"
    matched_files = []


    def __get_input(key: str, required: bool = False) -> Any:
        if key == "include":
            return include
        elif key == "exclude":
            return exclude
        elif key == "working-directory":
            return working_directory
        elif key == "allow-outside-working-directory":
            return allow_outside
        elif key == "output-directory":
            return output_directory
        elif key == "recursive":
            return recursive
        elif key == "verbosity":
            return verbosity
        elif key == "dry-run":
            return dry_run
        elif key == "comment":
            return comment
        elif key == "fail-on-error":
            return True

    mocker.patch("prepare_codestripper.main.get_input", side_effect=__get_input)
    mocker.patch("prepare_codestripper.main.get_matching_files", return_value=matched_files)
    mocker.patch("prepare_codestripper.main.strip_files")
    mocker.patch("prepare_codestripper.main.set_output")

    with pytest.raises(SystemExit):
        strip()


def test_fail_on_error(mocker: pytest_mock.MockerFixture) -> None:
    """
    Test that it fails if there are strip errors

    :param mocker: mocker
    :return:
    """
    include = ["a.txt", "b.txt"]
    exclude = []
    working_directory = "testproject"
    allow_outside = False
    output_directory = "out"
    recursive = True
    verbosity = 3
    dry_run = False
    comment = "//"

    def __get_input(key: str, required: bool = False) -> Any:
        if key == "include":
            return include
        elif key == "exclude":
            return exclude
        elif key == "working-directory":
            return working_directory
        elif key == "allow-outside-working-directory":
            return allow_outside
        elif key == "output-directory":
            return output_directory
        elif key == "recursive":
            return recursive
        elif key == "verbosity":
            return verbosity
        elif key == "dry-run":
            return dry_run
        elif key == "comment":
            return comment
        elif key == "fail-on-error":
            return True

    mocker.patch("prepare_codestripper.main.get_input", side_effect=__get_input)
    mock = mocker.patch("prepare_codestripper.main.set_failed")

    strip()

    mock.assert_called_once()
