# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

import shutil
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from typing import Dict, List, Set, Tuple

from make_runner import utils


def add_runner_args(parser: ArgumentParser):
    """Adds runner arguments to an argument parser.

    Args:
        ArgumentParser: The given argument parser.
    """
    # fmt: off
    parser.add_argument("-B", "--always-make", action="store_true",
                        help="unconditionally run all tasks")
    parser.add_argument("-f", "--makefile", metavar="FILE",
                        help="read FILE as a makefile")
    parser.add_argument("-j", "--jobs", metavar="N", nargs="?", const="",
                        help="allow N jobs at once; infinite jobs with no argument")
    parser.add_argument("-k", "--keep-going", action="store_true",
                        help="keep going when some tasks are failed")
    parser.add_argument("-l", "--load-average", metavar="N", nargs="?", const="",
                        help="don't start multiple jobs unless load is below N")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="don't actually run any tasks")
    parser.add_argument("-s", "--silent", action="store_true",
                        help="don't echo tasks")
    parser.add_argument("-t", "--touch", action="store_true",
                        help="touch targets instead of remaking them")
    # fmt: on


def chunk_line(line: str, width: int, delimiters: Set[str], indent_str: str) -> str:
    """Chunks the given line by the specified width.

    Args:
        line (str): The given line.
        width (int): Chunking width.
        delimiters (Set[str]): Chunking delimiters.
        indent_str (str): The prefix string added to each line.

    Returns:
        str: A chunked line.

    Todo:
        Clean up.
    """

    def _chunk(token: str, cur_line_len: int = 0) -> Tuple[str, int]:
        """Helper function for chunking a line.

        Args:
            token (str): Chunked text.
            cur_line_len (int): Current chunked line length.

        Returns:
            - str: Newline-chuncked line.
            - int: Current chunked line length.
        """
        for d in delimiters:
            if d in token:
                subtokens = []
                for subtoken in token.split(d):
                    chunked_line, cur_line_len = _chunk(subtoken, cur_line_len)
                    subtokens.append(chunked_line)
                return d.join(subtokens), cur_line_len

        token_len = len(token)
        next_line_len = cur_line_len + token_len + 1
        if next_line_len < width:
            return token, next_line_len
        elif token_len < width:
            return "\n" + indent_str + token, token_len

        chunked_line = ""
        for char in token:
            next_line_len = cur_line_len + 1
            if next_line_len >= width:
                chunked_line += "\n" + indent_str
                next_line_len = 0
            chunked_line += char
            cur_line_len = next_line_len
        return chunked_line, cur_line_len

    return _chunk(utils.normalize_space(line))[0]


def colorize(s: str) -> str:
    """Colorize a text.

    Args:
        s (str): A text.

    Returns:
        str: Colorized text.
    """
    return "\033[36m{}\033[0m".format(s)


def parse_runner_args() -> Namespace:
    """Parses make-runner arguments.

    Returns:
        Namespace: make-runner arguments.
    """
    parser = ArgumentParser(add_help=False)
    add_runner_args(parser)
    args, _ = parser.parse_known_args()
    return args


def parse_args(
    tasks: List[Dict[str, str]],
    options: List[Dict[str, str]],
    indent: int = 2,
    content_indent: int = 24,
    max_task_name_len: int = 20,
) -> Namespace:
    """Parses command-line arguments.

    1. Firstly, parses the make-runner arguments.
    2. Then, parses the tasks and options arguments read from makefile.

    Args:
        tasks (List[Dict[str, str]]): Task list.
        options (List[Dict[str, str]]): Option list.
        indent (int): Indent size.
        content_indent (int): Content indent size.
        max_task_name_len (int): Maximum task name length.

    Todo:
        Clean up.
    """
    width = shutil.get_terminal_size().columns
    content_indent_str = " " * content_indent
    content_width = width - content_indent
    deliminators = {" ", "-", "&", "+", "_", "="}

    tasks.append({"name": "help", "desc": "Show this help message."})

    task_names = [task["name"] for task in tasks]
    task_descriptions = "Available tasks:"
    task_descriptions += "\n"
    for task in tasks:
        task_name = task["name"]
        task_name_len = len(task_name)
        task_descriptions += "  {}".format(colorize(task["name"]))

        if task_name_len > max_task_name_len:
            task_descriptions += "\n" + content_indent_str
        else:
            task_descriptions += content_indent_str[indent + task_name_len :]

        task_descriptions += chunk_line(
            task["desc"], content_width, deliminators, content_indent_str
        )
        task_descriptions += "\n"

    parser = ArgumentParser(
        description=task_descriptions,
        formatter_class=RawDescriptionHelpFormatter,
    )
    add_runner_args(parser)

    task_parser = parser.add_argument_group(title="Task options")
    for option in options:
        argument = utils.normalize_option_name(option["name"])
        help = "{}".format(option["desc"])
        default = option["default"]
        if default is not None and len(default) > 0:
            help += " (default: {})".format(default)
            task_parser.add_argument(argument, default=option["default"], help=help)
        elif option["flag"] is not None:
            task_parser.add_argument(argument, help=help, action="store_true")
        else:
            task_parser.add_argument(argument, help=help)

    # fmt: off
    parser.add_argument("tasks", nargs="*", choices=task_names, metavar="TASK", default="help",
                        help="{{{}}}".format(", ".join(task_names)))
    # fmt: on

    args, _ = parser.parse_known_args()
    if args.tasks is None or len(args.tasks) == 0 or "help" in args.tasks:
        return parser.parse_args(["-h"])
    return parser.parse_args()
