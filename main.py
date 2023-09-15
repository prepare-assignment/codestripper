from typing import List, Optional

from codestripper.utils import set_logger_level
from prepare_toolbox.core import get_input
from prepare_toolbox.file import get_matching_files
from codestripper.code_stripper import strip_files


def main() -> None:
    include: List[str] = get_input("include")
    exclude: Optional[List[str]] = get_input("exclude")
    cwd: str = get_input("working-directory")
    out: str = get_input("output")
    comment: str = get_input("comment")
    recursive: bool = get_input("recursive")
    verbosity: int = get_input("verbosity")
    dry_run: bool = get_input("dry-run")

    files = get_matching_files(include, exclude, relative_to=cwd, recursive=recursive)
    set_logger_level("codestripper", verbosity)
    strip_files(files, working_directory=cwd, comment=comment, output=out, dry_run=dry_run)


main()
