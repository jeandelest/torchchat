# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import logging
import subprocess
import sys

from cli import (
    add_arguments_for_browser,
    add_arguments_for_chat,
    add_arguments_for_download,
    add_arguments_for_eval,
    add_arguments_for_export,
    add_arguments_for_generate,
    add_arguments_for_list,
    add_arguments_for_remove,
    arg_init,
    check_args,
)

default_device = "cpu"


if __name__ == "__main__":
    # Initialize the top-level parser
    parser = argparse.ArgumentParser(
        prog="torchchat",
        add_help=True,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="The specific command to run",
    )
    subparsers.required = True

    parser_chat = subparsers.add_parser(
        "chat",
        help="Chat interactively with a model",
    )
    add_arguments_for_chat(parser_chat)

    parser_browser = subparsers.add_parser(
        "browser",
        help="Chat interactively in a browser",
    )
    add_arguments_for_browser(parser_browser)

    parser_download = subparsers.add_parser(
        "download",
        help="Download a model from Hugging Face or others",
    )
    add_arguments_for_download(parser_download)

    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate responses from a model given a prompt",
    )
    add_arguments_for_generate(parser_generate)

    parser_eval = subparsers.add_parser(
        "eval",
        help="Evaluate a model given a prompt",
    )
    add_arguments_for_eval(parser_eval)

    parser_export = subparsers.add_parser(
        "export",
        help="Export a model for AOT Inductor or ExecuTorch",
    )
    add_arguments_for_export(parser_export)

    parser_list = subparsers.add_parser(
        "list",
        help="List supported models",
    )
    add_arguments_for_list(parser_list)

    parser_remove = subparsers.add_parser(
        "remove",
        help="Remove downloaded model artifacts",
    )
    add_arguments_for_remove(parser_remove)

    # Now parse the arguments
    args = parser.parse_args()
    args = arg_init(args)
    logging.basicConfig(
        format="%(message)s", level=logging.DEBUG if args.verbose else logging.INFO
    )

    if args.command == "chat":
        # enable "chat"
        args.chat = True
        check_args(args, "chat")
        from generate import main as generate_main

        generate_main(args)
    elif args.command == "browser":
        # enable "chat" and "gui" when entering "browser"
        args.chat = True
        args.gui = True
        check_args(args, "browser")

        # Look for port from cmd args. Default to 5000 if not found.
        port = 5000
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--port":
                if i + 1 < len(sys.argv):
                    # Extract the value and remove '--port' and the value from sys.argv
                    port = sys.argv[i + 1]
                    del sys.argv[i : i + 2]
                    break
            else:
                i += 1

        # Construct arguments for the flask app minus 'browser' command
        # plus '--chat'
        args_plus_chat = ["'{}'".format(s) for s in sys.argv[1:] if s != "browser"] + [
            '"--chat"'
        ]
        formatted_args = ", ".join(args_plus_chat)
        command = [
            "flask",
            "--app",
            "chat_in_browser:create_app(" + formatted_args + ")",
            "run",
            "--port",
            f"{port}",
        ]
        subprocess.run(command)
    elif args.command == "download":
        check_args(args, "download")
        from download import download_main

        download_main(args)
    elif args.command == "generate":
        check_args(args, "generate")
        from generate import main as generate_main

        generate_main(args)
    elif args.command == "eval":
        from eval import main as eval_main

        eval_main(args)
    elif args.command == "export":
        check_args(args, "export")
        from export import main as export_main

        export_main(args)
    elif args.command == "list":
        check_args(args, "list")
        from download import list_main

        list_main(args)
    elif args.command == "remove":
        check_args(args, "remove")
        from download import remove_main

        remove_main(args)
    else:
        parser.print_help()
