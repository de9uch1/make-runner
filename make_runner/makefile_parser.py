# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
import os
import re
import subprocess
import sys
from argparse import Namespace

from make_runner import utils

TASK_PATTERN = re.compile(r"^(?P<name>[a-zA-Z0-9_-]+):.*?##[ \t]*(?P<desc>.*)$")
OPTION_DESC_PATTERN = re.compile(r"^##[ \t]*(?P<desc>.*)$")
OPTION_DEF_PATTERN = re.compile(
    r"^[ \t]*(?P<name>[a-zA-Z0-9_]+)[ \t]*:?=[ \t]*(?P<default>.*?)[ \t]*$"
)


def read_makefile(path: str):
    tasks, options = [], []
    with open(path, mode="r", encoding="utf-8") as f:
        option = {}
        for line in f:
            line = line.strip()

            # task
            match_task = TASK_PATTERN.match(line)
            if match_task is not None:
                tasks.append(match_task.groupdict())

            # option
            match_option_desc = OPTION_DESC_PATTERN.match(line)
            match_option_def = OPTION_DEF_PATTERN.match(line)
            if match_option_desc is not None:
                option["desc"] = match_option_desc.groupdict()["desc"]
                continue

            if len(option) > 0 and match_option_def is not None:
                option.update(match_option_def.groupdict())
                options.append(option)
            option = {}

    return tasks, options


def find_makefile(args: Namespace):
    if getattr(args, "makefile", None) is not None:
        f = args.makefile
        if os.path.exists(f):
            return os.path.abspath(f)
        print("{} not found.".format(f), file=sys.stderr)
        exit(1)

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
    print("Makefile not found.", file=sys.stderr)
    exit(1)


def get_makefile_list(makefile_path):
    makefile_list_pattern = re.compile(r"^MAKEFILE_LIST[\s]*:?=[\s]*.+?$")
    proc = subprocess.run(
        [utils.make_command(), "-p", "-f", makefile_path],
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    for line in proc.stdout.split("\n"):
        line = line.strip()
        if makefile_list_pattern.match(line):
            break
    else:
        raise ValueError

    return utils.normalize_space(line).split()[2:]
