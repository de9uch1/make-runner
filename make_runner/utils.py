# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
import platform
import re

SPACE_NORMALZIER = re.compile(r"\s+")


def normalize_option_name(name: str, argument=True):
    name = name.lower()
    if argument:
        name = "--" + name.replace("_", "-")
    return name


def normalize_space(line):
    return SPACE_NORMALZIER.sub(" ", line)


def make_command():
    return {
        "darwin": "make",
        "linux": "make",
    }[platform.system().lower()]
