from typing import List, Optional

from codestripper.utils import set_logger_level  # type: ignore
from codestripper.code_stripper import strip_files  # type: ignore
from prepare_toolbox.core import get_input, set_output, set_failed, debug, info
from prepare_toolbox.file import get_matching_files


def strip() -> None:
    try:
        include: List[str] = get_input("include", required=True)
        debug(f"include: {include}")
        exclude: Optional[List[str]] = get_input("exclude")
        debug(f"exclude:  {exclude}")
        cwd: str = get_input("working-directory")
        allow_outside: bool = get_input("allow-outside-working-directory")
        out: str = get_input("output-directory")
        comment: str = get_input("comment")
        recursive: bool = get_input("recursive")
        verbosity: int = get_input("verbosity")
        dry_run: bool = get_input("dry-run")

        files = get_matching_files(include, exclude, allow_outside_working_dir=allow_outside,
                                   relative_to=cwd, recursive=recursive)

        if files is None or len(files) == 0:
            set_failed(f"No files matched")
        info(f"Matched files: {files}")
        set_logger_level("prepare_codestripper", verbosity)
        stripped = strip_files(files, working_directory=cwd, comment=comment, output=out, dry_run=dry_run)
        set_output("matched-files", files)
        set_output("stripped-files", stripped)
    except Exception as e:
        set_failed(e)


if __name__ == "__main__":
    strip()
