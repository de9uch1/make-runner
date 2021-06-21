# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
import shutil
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from make_runner import utils


def add_runner_args(parser: ArgumentParser):
    parser.add_argument(
        "-B", "--always-make", action="store_true", help="unconditionally run all tasks"
    )
    parser.add_argument(
        "-f", "--makefile", metavar="FILE", help="read FILE as a makefile"
    )
    parser.add_argument(
        "-j",
        "--jobs",
        metavar="N",
        nargs="?",
        const="",
        help="allow N jobs at once; infinite jobs with no argument",
    )
    parser.add_argument(
        "-k",
        "--keep-going",
        action="store_true",
        help="keep going when some tasks are failed",
    )
    parser.add_argument(
        "-l",
        "--load-average",
        metavar="N",
        nargs="?",
        const="",
        help="don't start multiple jobs unless load is below N",
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="don't actually run any tasks"
    )
    parser.add_argument("-s", "--silent", action="store_true", help="don't echo tasks")
    parser.add_argument(
        "-t",
        "--touch",
        action="store_true",
        help="touch targets instead of remaking them",
    )


def parse_runner_args():
    parser = ArgumentParser(add_help=False)
    add_runner_args(parser)
    args, _ = parser.parse_known_args()
    return args


def chunk_line(line, width, deliminators, indent_str):
    def _chunk(token, cur_line_len=0):
        for d in deliminators:
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


def parse_args(tasks: list, options: list):
    indent = 2
    width = shutil.get_terminal_size().columns
    content_indent = 24
    content_indent_str = " " * content_indent
    content_width = width - content_indent
    deliminators = [" ", "-", "&", "+", "_", "="]

    tasks.append({"name": "help", "desc": "show this help message"})

    task_names = [task["name"] for task in tasks]
    task_descriptions = "available tasks:\n"
    for task in tasks:
        task_name = task["name"]
        task_name_len = len(task_name)
        task_descriptions += "  \033[36m{}\033[0m".format(task["name"])

        if task_name_len > content_indent - 4:
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

    task_parser = parser.add_argument_group(title="task options")
    for option in options:
        argument = utils.normalize_option_name(option["name"])
        help = "{}".format(option["desc"])
        default = option["default"]
        if default is not None and len(default) > 0:
            help += " (default: {})".format(default)
            task_parser.add_argument(argument, default=option["default"], help=help)
        else:
            task_parser.add_argument(argument, help=help)
    parser.add_argument(
        "tasks",
        nargs="*",
        choices=task_names,
        metavar="TASK",
        default="help",
        help="{{{}}}".format(", ".join(task_names)),
    )

    args, rest = parser.parse_known_args()
    if args.tasks is None or len(args.tasks) == 0 or "help" in args.tasks:
        return parser.parse_args(["-h"])
    return parser.parse_args()
