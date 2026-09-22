from typing import List, Optional

from codestripper.utils import set_logger_level  # type: ignore
from codestripper.code_stripper import strip_files  # type: ignore
from codestripper.utils.enums import UnexpectedInputOptions # type: ignore
from prepare_toolbox.core import get_input, set_output, set_failed, debug, info
from prepare_toolbox.file import get_matching_files


def __unexpected_input_option(name: str) -> UnexpectedInputOptions:
    """
    Convert the input (e.g. 'FAIL' or 'fail') to the codestripper option. The library compares with the enum,
    passing the string meant that every value behaved like INCLUDE.
    """
    value = get_input(name)
    try:
        return UnexpectedInputOptions(str(value).lower())
    except ValueError:
        options = ", ".join(option.name for option in UnexpectedInputOptions)
        raise ValueError(f"Invalid value '{value}' for '{name}', expected one of: {options}")


def strip() -> None:
    try:
        include: List[str] = get_input("include", required=True)
        debug(f"include: {include}")
        exclude: Optional[List[str]] = get_input("exclude")
        debug(f"exclude:  {exclude}")
        cwd: str = get_input("working-directory")
        allow_outside: bool = get_input("allow-outside-working-directory")
        out: str = get_input("output-directory")
        comments: Optional[List[str]] = get_input("comments")
        recursive: bool = get_input("recursive")
        verbosity: int = get_input("verbosity")
        dry_run: bool = get_input("dry-run")
        fail_on_error: bool = get_input("fail-on-error")
        unknown_extension = __unexpected_input_option("unknown")
        binary = __unexpected_input_option("binary")

        files = get_matching_files(include, exclude, allow_outside_working_dir=allow_outside,
                                   relative_to=cwd, recursive=recursive)

        if files is None or len(files) == 0:
            info("No files matched")
            return
        info(f"Matched files: {files}")
        set_logger_level("codestripper", verbosity)
        stripped = strip_files(files, working_directory=cwd, comments=comments, output=out,
                               dry_run=dry_run, fail_on_error=fail_on_error, unknown_extension=unknown_extension,
                               binary=binary)
        set_output("matched-files", files)
        set_output("stripped-files", stripped)
    except Exception as e:
        set_failed(e)


if __name__ == "__main__":
    strip()
