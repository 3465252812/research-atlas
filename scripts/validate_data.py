"""Validate canonical research data; exit 1 on errors (or warnings with --strict)."""
import argparse
from data_model import read_json, validate, write_json

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input')
    p.add_argument('--report')
    p.add_argument('--strict', action='store_true')
    args = p.parse_args()
    try:
        report = validate(read_json(args.input))
    except (ValueError, OSError, TypeError) as e:
        p.exit(1, str(e) + '\n')
    if args.report:
        write_json(args.report, report)
    print(f"errors={len(report['errors'])} warnings={len(report['warnings'])} counts={report['counts']}")
    for e in report['errors'][:20]:
        print(f"ERROR {e['location']}: {e['message']}")
    raise SystemExit(1 if report['errors'] or (args.strict and report['warnings']) else 0)

if __name__ == '__main__':
    main()
