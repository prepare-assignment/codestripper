from typing import List, Optional

from codestripper.utils import set_logger_level
from prepare_toolbox.core import get_input, debug
from prepare_toolbox.file import get_matching_files
from codestripper.code_stripper import strip_files


def main() -> None:
    include: List[str] = get_input("include")
    debug(f"include: {include}")
    exclude: Optional[List[str]] = get_input("exclude")
    debug(f"exclude: {exclude}")
    cwd: str = get_input("working-directory")
    debug(f"cwd: {cwd}")
    out: str = get_input("output")
    debug(f"out: {out}")
    comment: str = get_input("comment")
    debug(f"comment: {comment}")
    recursive: bool = get_input("recursive")
    debug(f"recursive: {recursive}")
    verbosity: int = get_input("verbosity")
    debug(f"verbosity: {verbosity}")
    dry_run: bool = get_input("dry-run")
    debug(f"dry_run: {dry_run}")

    files = get_matching_files(include, exclude, relative_to=cwd, recursive=recursive)
    set_logger_level("codestripper", verbosity)
    strip_files(files, working_directory=cwd, comment=comment, output=out, dry_run=dry_run)


main()
