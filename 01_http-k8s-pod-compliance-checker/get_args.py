import argparse

def get_args():
    SYSTEM_NAMESPACES = {
        "kube-system",
        "kube-public",
        "kube-node-lease",
        "cattle-system",
        "cattle-fleet-system",
        "cattle-fleet-local-system",
        "cattle-capi-system",
        "cattle-impersonation-system",
    }

    parser = argparse.ArgumentParser(description='Kube Compliance Checker - CLI Tool to check compliance of k8s cluster pods')

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