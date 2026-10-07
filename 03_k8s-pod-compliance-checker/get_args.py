import argparse

EPILOG = """\
examples:
  python main.py                                  scan the whole cluster (system namespaces excluded)
  python main.py -n gitea                         scan a single namespace
  python main.py --high                           only findings that need attention
  python main.py --high --medium                  severity filters are additive
  python main.py --resources --high               combine severity and standard filters
  python main.py --include-system --high          include kube-system / cattle-* findings
  python main.py -o json | jq -r '.[].rule_id' | sort | uniq -c | sort -rn
                                                  count violations by rule
  python main.py -o csv --csv-path findings.csv   export for a spreadsheet

standards:
  --baseline    PSS-Baseline    privileged, host namespaces, capabilities, hostPath
  --restricted  PSS-Restricted  runAsNonRoot, privilege escalation, seccomp
  --resources   Resources       missing requests / limits
  --runtime     Runtime         OOMKilled history, usage vs limits

Filters within a group are OR'ed, groups are AND'ed. No filter means show everything.
"""


def get_args():

    parser = argparse.ArgumentParser(
        description='Kube Compliance Checker - CLI Tool to check compliance of k8s cluster pods',
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-n', '--namespace', type=str, help='Namespace of pods to check', default=None)
    parser.add_argument('--ok', action='store_true', help='Show only ok severity findings')
    parser.add_argument('--info', action='store_true', help='Show only info severity findings')
    parser.add_argument('--low', action='store_true', help='Show only low severity findings')
    parser.add_argument('--medium', action='store_true', help='Show only medium severity findings')
    parser.add_argument('--high', action='store_true', help='Show only high severity findings')
    parser.add_argument('--baseline', action='store_true', help='Show only PSS-Baseline findings')
    parser.add_argument('--restricted', action='store_true', help='Show only PSS-Restricted findings')
    parser.add_argument('--resources', action='store_true', help='Show only Resources findings')
    parser.add_argument('--runtime', action='store_true', help='Show only Runtime findings')
    parser.add_argument(
        '-o', '--output',
        choices=['human', 'json', 'yaml', 'csv'],
        default='human',
        help='Output format: human, json, yaml, or csv'
    )
    parser.add_argument(
        '--csv-path',
        type=str,
        default=None,
        help='Path to output CSV file (required when --output csv)'
    )
    parser.add_argument(
        '--include-system',
        action='store_true',
        help='Include system namespaces (kube-system, cattle-*) — excluded by default'
    )

    args = parser.parse_args()

    if args.output == "csv" and not args.csv_path:
        parser.error("--csv-path is required when --output csv")

    return args