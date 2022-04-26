# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

import os
import re
import subprocess
from argparse import Namespace
from typing import Dict, List, Tuple

from make_runner import utils

TASK_PATTERN = re.compile(r"^(?P<name>[a-zA-Z0-9_-]+):.*?##\s*(?P<desc>.*)$")
OPTION_DESC_PATTERN = re.compile(r"^##\s*(?P<flag>%FLAG%)?\s*(?P<desc>.*)$")
OPTION_DEF_PATTERN = re.compile(
    r"^\s*(?P<name>[a-zA-Z0-9_]+)\s*:?=\s*(?P<default>.*?)?\s*$"
)
MAKEFILE_LIST_PATTERN = re.compile(r"^MAKEFILE_LIST[\s]*:?=[\s]*.+?$")


def read_makefile(path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Reads makefile.

    Args:
        path (str): Makefile path.

    Returns:
        - List[Dict[str, str]]: Task list.
        - List[Dict[str, str]]: Option list.
    """
    tasks, options = [], []
    with open(path, mode="r") as f:
        option = {}
        for line in f:
            line = line.strip()

            # Task
            match_task = TASK_PATTERN.match(line)
            if match_task is not None:
                tasks.append(match_task.groupdict())
                continue

            # Option
            match_option_desc = OPTION_DESC_PATTERN.match(line)
            if match_option_desc is not None:
                option.update(match_option_desc.groupdict())
                continue

            match_option_def = OPTION_DEF_PATTERN.match(line)
            if len(option) > 0 and match_option_def is not None:
                option.update(match_option_def.groupdict())
                options.append(option)
                option = {}

    return tasks, options


def find_makefile(args: Namespace) -> str:
    """Finds makefile.

    Args:
        args (argparse.Namespace): Command-line arguments.

    Returns:
        str: Found makefile path.

    Raises:
        FileNotFoundError: If any makefiles are not found.
    """
    if getattr(args, "makefile", None) is not None:
        f = args.makefile
        if os.path.exists(f):
            return os.path.abspath(f)
        raise FileNotFoundError(f"{f}")

    cur = os.path.abspath(os.curdir)
    f = os.path.join(cur, "Makefile")
    if os.path.exists(f):
        return os.path.abspath(f)
    os.chdir(os.pardir)
    while not os.path.samefile(cur, os.curdir):
        cur = os.path.abspath(os.curdir)
        f = os.path.join(cur, "Makefile")
        if os.path.exists(f):
            return os.path.abspath(f)
        os.chdir(os.pardir)
    raise FileNotFoundError("Makefile not found.")


def get_makefile_list(makefile_path: str) -> List[str]:
    """Gets makefile list that are included by main makefile.

    Args:
        makefile_path (str): Main makefile path.

    Returns:
        List[str]: Sub makefile list.

    Raises:
        ValueError: If `MAKEFILE_LIST` variable is not defined by internal.
    """
    proc = subprocess.run(
        [utils.make_command(), "-p", "-f", makefile_path],
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    for line in proc.stdout.split("\n"):
        line = line.strip()
        if MAKEFILE_LIST_PATTERN.match(line) is not None:
            break
    else:
        raise ValueError

    return utils.normalize_space(line).split()[2:]
