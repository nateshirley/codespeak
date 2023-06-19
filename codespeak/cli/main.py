import argparse
from codespeak import clean


def command_name_handler():
    print("Executing command_name")


def main():
    parser = argparse.ArgumentParser(prog="codespeak")
    subparsers = parser.add_subparsers(dest="command")

    # Add your subcommands here
    parser_command_name = subparsers.add_parser("clean")
    parser_command_name.set_defaults(func=clean.main)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
