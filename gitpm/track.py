"""
Add new git repositories for gitpm to track.
"""

# Copyright (c) Brandon Pacewic
# SPDX-License-Identifier: MIT

import sys
import configparser
import os

from optparse import Values
from typing import Any

from gitpm.command import Command
from gitpm.logging import Colors, get_logger
from gitpm.util import is_git_repository, cache_repo_data

logger = get_logger(__name__)


class TrackCommand(Command):
    def add_options(self) -> None:
        self.cmd_options.add_option(
            "-a",
            "--add-all",
            action="store_true",
            dest="add_all",
            default=False,
            help="Add all git repositories in child directories."
        )

    def run(self, options: Values, args: list[str]) -> None:
        if len(args) == 0:
            self.parser.print_help()
            sys.exit(1)

        if options.add_all:
            for arg in args:
                for x in os.listdir(arg):
                    if os.path.isdir(x) and is_git_repository(x):
                        logger.debug(f"Caching {os.path.abspath(x)}...")
                        self.make_and_cache_data(x)
        else:
            for arg in args:
                arg = os.path.abspath(arg)

                if not os.path.isdir(arg):
                    logger.colored_critical(
                        Colors.BOLD_RED, f"{arg} is not a valid directory.")
                    sys.exit(1)
                elif not is_git_repository(arg):
                    logger.colored_critical(
                        Colors.BOLD_RED, f"{arg} is not a valid git repository.")
                    sys.exit(1)

                self.make_and_cache_data(arg)

    @staticmethod
    def make_and_cache_data(dir: str) -> None:
        repo_dir = os.path.abspath(dir)
        data = extract_repository_data(repo_dir)
        cache_repo_data(**data)


def extract_repository_data(repo_dir: str) -> dict[str, Any]:
    git_config = configparser.ConfigParser()
    git_config.read(f"{repo_dir}/.git/config")
    url = git_config.get('remote "origin"', "url")
    data = {
        "name": repo_dir.split("/")[-1],
        "author": url.split(":")[-1].split("/")[0],
        "url": url,
        "path": repo_dir
    }

    return data