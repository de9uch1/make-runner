# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

import platform
import re

SPACE_NORMALZIER = re.compile(r"\s+")


def normalize_option_name(name: str, argument: bool = True) -> str:
    """Normalizes option name.

    Args:
        name (str): An option name.
        argument (bool): If true, outputs the :class:`argparse.ArgumentParser` argument format.
    """
    name = name.lower()
    if argument:
        name = "--" + name.replace("_", "-")
    return name


def normalize_space(line: str) -> str:
    """Normalizes whitespaces.

    Args:
        line (str): The given string.

    Returns:
        str: Normalized string.
    """
    return SPACE_NORMALZIER.sub(" ", line)


def make_command() -> str:
    """Returns make command string.

    Returns:
        str: Make command string determined by the running platform.
    """
    return {
        "darwin": "make",
        "linux": "make",
    }[platform.system().lower()]
