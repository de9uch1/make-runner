# Copyright (c) 2021 Hiroyuki Deguchi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

import os

from make_runner import command_line, makefile_parser, utils


def main() -> None:
    """Main funtion.

    1. Parses make-runner arguments.
    2. Finds a main makefile and reads tasks and options from the all included makefile.
    3. Parses tasks and options arguments.
    4. Builds the expected command-line.
    5. Executes `make` with the given arguments.
    """
    # 1. Parses make-runner arguments.
    args = command_line.parse_runner_args()

    # 2. Finds a main makefile and reads tasks and options from the all included makefile.
    makefile_path = makefile_parser.find_makefile(args)
    os.chdir(os.path.dirname(makefile_path))
    makefile_list = makefile_parser.get_makefile_list(makefile_path)
    tasks, options = [], []
    for f in makefile_list:
        f_tasks, f_options = makefile_parser.read_makefile(f)
        tasks += f_tasks
        options += f_options

    # 3. Parses tasks and options arguments.
    args = command_line.parse_args(tasks, options)

    # 4. Builds the expected command-line.
    runner = [utils.make_command()]

    for option in ["always_make", "keep_going", "dry_run", "silent", "touch"]:
        if getattr(args, option, False):
            runner.append(utils.normalize_option_name(option))
    for option in ["makefile", "jobs", "load_average"]:
        if getattr(args, option, None) is not None:
            runner.append(utils.normalize_option_name(option))
            if option == "makefile":
                runner.append(makefile_path)
            else:
                runner.append(getattr(args, option))

    runner += args.tasks
    for option in options:
        option_name = option["name"]
        option_value = getattr(
            args, utils.normalize_option_name(option_name, argument=False), None
        )
        if option["flag"] is not None:
            if option_value:
                runner.append("{}=1".format(option_name))
            continue
        if option_value is not None:
            runner.append("{}={}".format(option_name, option_value))
            continue

    # 5. Executes `make` with the given arguments.
    os.execvp(runner[0], runner)


if __name__ == "__main__":
    main()
