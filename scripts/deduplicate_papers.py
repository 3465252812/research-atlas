"""Report duplicate candidates; only apply an explicit reviewed ID merge plan."""
import argparse
from data_model import read_json, write_json, duplicate_candidates, merge_papers, validate

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input')
    p.add_argument('--report', required=True)
    p.add_argument('--plan', help='JSON object mapping removed paper IDs to retained paper IDs')
    p.add_argument('--output')
    a = p.parse_args()
    data = read_json(a.input)
    write_json(a.report, dict(candidates=duplicate_candidates(data), mode='review_required'))
    if a.plan:
        if not a.output:
            p.error('--plan requires --output')
        try:
            merged = merge_papers(data, read_json(a.plan))
        except ValueError as e:
            p.exit(1, str(e) + '\n')
        report = validate(merged)
        if report['errors']:
            p.exit(1, '合并后校验失败，未写出: ' + str(report['errors'][:3]) + '\n')
        write_json(a.output, merged)
    print('Duplicate report saved; no automatic identity decisions.')

if __name__ == '__main__':
    main()
