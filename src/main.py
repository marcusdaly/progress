"""
Main entrypoint for progress app.
"""

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="Increase output verbosity.", action="store_true"
    )

    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)

    parser_info = subparsers.add_parser(
        "info", help="Get detailed info on a single strategy."
    )