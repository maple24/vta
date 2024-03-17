# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Make sure that all files in the project have the correct license header.
"""

# Note: This script should use only standard library tooling as it should work
# without/indepedet of the virtual environment.

import argparse
import re
from pathlib import Path
from typing import List, NamedTuple
from loguru import logger

HEADER = """# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================"""


SHEBANG_RE = re.compile(r"^#!.*\n")


# API -------------------------------------------------------------------------


def is_license_header_correct(file: Path) -> bool:
    content = file.read_text()
    if content.startswith("#!"):
        content = SHEBANG_RE.sub("", content)
    return content.startswith(HEADER)


def ensure_file_has_license_header(file: Path) -> None:
    if is_license_header_correct(file):
        return
    content_with_header = HEADER + "\n\n" + file.read_text()
    file.write_text(content_with_header)


def is_relevant_file(path: Path) -> bool:
    if path.name == "__init__.py":
        return False
    if path.suffix == ".py":
        return True
    return False


def find_relevant_files(root_dir: Path) -> List[Path]:
    return [f for f in root_dir.glob("**/*.py") if is_relevant_file(f)]


# cli -------------------------------------------------------------------------


class _Args(NamedTuple):
    check: bool


def _parse_args() -> _Args:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not add headers just check whether they are present."
        " Exit status will indicate whether all files have the correct header"
        " (exit 0 means all files have the correct header).",
    )
    args = parser.parse_args()
    return _Args(check=args.check)


def main():
    args = _parse_args()
    relevant_files = [
        *find_relevant_files(Path(__file__).parent / "vta"),
        *find_relevant_files(Path(__file__).parent / "tests"),
        *find_relevant_files(Path(__file__).parent / "scripts"),
    ]
    files_without_correct_license_header: List[Path] = [
        file for file in relevant_files if not is_license_header_correct(file)
    ]
    if args.check:
        if len(files_without_correct_license_header) == 0:
            logger.info(
                f"All {len(relevant_files)} relevant files have the correct license header."
            )
            raise SystemExit(0)
        else:
            logger.info(
                f"{len(files_without_correct_license_header)} files do not have the correct license header:"
            )
            logger.info("\n".join(str(f) for f in files_without_correct_license_header))
            raise SystemExit(1)
    else:
        for file in files_without_correct_license_header:
            logger.info(f"Adding license header to {file}.")
            ensure_file_has_license_header(file)


if __name__ == "__main__":
    main()
