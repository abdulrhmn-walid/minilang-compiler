"""Command-line interface.

    python main.py program.txt                 everything
    python main.py program.txt --show errors   only the messages
    python main.py --grammar                   FIRST/FOLLOW and the LL(1) table (no file needed)

Exit code: 0 = compiled without errors, 1 = errors found, 2 = could not read the file.
"""
import argparse
import sys

import report
from pipeline import compile_source

SECTIONS = ("tokens", "symbols", "first-follow", "table", "tree", "errors")


def read_source(path):
    # utf-8-sig drops the invisible BOM that Windows Notepad may add at the start of a file
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def print_section(title, text):
    print(f"\n===== {title} =====")
    print(text)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="main.py", description="MiniLang compiler front-end")
    ap.add_argument("file", nargs="?", help="MiniLang source file (e.g. tests/valid.txt)")
    ap.add_argument("--show", nargs="+", choices=SECTIONS, default=list(SECTIONS),
                    metavar="SECTION", help="sections to print: " + ", ".join(SECTIONS))
    ap.add_argument("--grammar", action="store_true",
                    help="print only FIRST/FOLLOW and the LL(1) table")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):          # make sure ε, → and box lines print everywhere
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.grammar:
        print_section("FIRST / FOLLOW", report.first_follow_text())
        print_section("LL(1) table", report.ll1_text())
        return 0
    if not args.file:
        ap.error("give a source file, or use --grammar")

    try:
        source = read_source(args.file)
    except (OSError, UnicodeDecodeError) as e:
        print(f"Cannot read '{args.file}': {e}", file=sys.stderr)
        return 2

    result = compile_source(source)
    shown = set(args.show)
    if "tokens" in shown:
        print_section("Tokens", report.tokens_text(result.tokens))
    if "symbols" in shown:
        print_section("Symbol Table", report.symbols_section(result))
    if "first-follow" in shown:
        print_section("FIRST / FOLLOW", report.first_follow_text())
    if "table" in shown:
        print_section("LL(1) table", report.ll1_text())
    if "tree" in shown:
        print_section("Parse Tree", report.tree_section(result))
    if "errors" in shown:
        print_section("Messages", report.diagnostics_text(result.diagnostics))
    print("\n" + report.summary(result))
    return 1 if result.diagnostics.has_errors() else 0


if __name__ == "__main__":
    sys.exit(main())
