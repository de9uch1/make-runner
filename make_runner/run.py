# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
import os
import subprocess
import sys
from itertools import chain

from make_runner import command_line, makefile_parser, utils


def main():
    args = command_line.parse_runner_args()
    makefile_path = makefile_parser.find_makefile(args)
    os.chdir(os.path.dirname(makefile_path))
    makefile_list = makefile_parser.get_makefile_list(makefile_path)
    tasks, options = [], []
    for f in makefile_list:
        tasks_i, options_i = makefile_parser.read_makefile(f)
        tasks.append(tasks_i)
        options.append(options_i)
    tasks, options = list(chain.from_iterable(tasks)), list(
        chain.from_iterable(options)
    )

    args = command_line.parse_args(tasks, options)

    runner = [utils.make_command()]

    for option in ["always_make", "keep_going", "dry_run", "silent", "touch"]:
        if getattr(args, option, False):
            runner.append(utils.normalize_option_name(option))
    for option in ["makefile", "jobs", "load_average"]:
        if getattr(args, option, None) is not None:
            runner.append(utils.normalize_option_name(option))
            runner.append(args.option)

    runner += args.tasks
    for option in options:
        option_name = option["name"]
        option_value = getattr(
            args, utils.normalize_option_name(option_name, argument=False), None
        )
        if option_value is not None:
            runner.append("{}={}".format(option_name, option_value))

    subprocess.run(runner)


if __name__ == "__main__":
    main()
