import argparse

def get_args():
    default_namespace = "kube-system"
    default_labels = "app.kubernetes.io/name=rke2-traefik"
    default_results_number = 10
    epilog_text = """
    Examples:
        Examples:
        # Show everything, pulling live from the cluster
        python main.py --show-all

        # Show top 20 IPs instead of default 10
        python main.py --show-top-ips --results-number 20

        # Analyze a saved log file instead of live cluster
        python main.py --from-file access.log --show-stats

        # Filter to a specific status code and print matching logs
        python main.py --status 500 --show-error-logs

        # Pull more lines and check top requested paths
        python main.py --lines 5000 --show-top-request-paths

        # Check stats for a specific IP address
        python main.py --ip 10.150.13.100 --show-top-ips

        # Custom namespace/labels when pulling from a different cluster setup
        python main.py --namespace default --labels app=my-ingress --show-all

        # Show requests slower than 10 seconds, with path shown
        python main.py --slower-than 10 --slower-than-show-path

        # Show slowest hosts, ranked by average response time
        python main.py --show-slowest

        # Filter by a time window (from a saved log file)
        python main.py --from-file access.log --since "2026-07-14 07:00" --until "2026-07-14 12:00" --show-top-request-addr

        # Export all metrics to CSV instead of printing to terminal
        python main.py --show-all --output-dir ./results

        # Narrow down to a specific host and check its error logs
        python main.py --host helpdesk-k8s.mw-wheels.com --show-error-logs

        # Combine IP and status filters to trace a specific incident
        python main.py --ip 172.20.15.10 --status 500 --show-error-logs

        # Check top error codes (4xx/5xx) with a bigger sample size
        python main.py --lines 20000 --show-top-error-codes
    """

    parser = argparse.ArgumentParser(
        description='Http Proxy log parser CLI tool',
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--from-file', type=str, help='A path to file with logs')
    parser.add_argument('--output-dir', type=str, help='A path to directory where results should be stored')
    parser.add_argument('--namespace', type=str, help='Namespace where pods with http proxy are deployed in', default=default_namespace)
    parser.add_argument('--labels', type=str, help='Labels to pods where you want to get logs from', default=default_labels)
    parser.add_argument('--lines', type=int, help='How much lines from source do you want to parse', default=100)
    parser.add_argument('--show-top-ips', action='store_true', help='Show top source IP addresses')
    parser.add_argument('--show-top-status-codes', action='store_true', help='Show top HTTP status codes')
    parser.add_argument('--show-top-error-codes', action='store_true', help='Show top HTTP error codes (4xx/5xx)')
    parser.add_argument('--show-top-request-addr', action='store_true', help='Show top requested sites')
    parser.add_argument('--show-top-request-paths', action='store_true', help='Show top requested paths')
    parser.add_argument('--show-stats', action='store_true', help='Show aggregated stats (p50/p95/p99)')
    parser.add_argument('--show-error-logs', action='store_true', help='Show logs that caused 5xx error code')
    parser.add_argument('--show-slowest', action='store_true', help='Show slowest endpoints')
    parser.add_argument('--show-all', action='store_true', help='Show all statistics that this tool is capable of...')
    parser.add_argument('--ip', type=str, help='Show statistics for specific ip address')
    parser.add_argument('--status', type=int, help='Show for specific return code status')
    parser.add_argument('--path', type=str, help='Show for specific path')
    parser.add_argument('--host', type=str, help='Show for specific host')
    parser.add_argument('--since', type=str, help='Show since specific date time, YYYY-MM-DD or YYYY-MM-DD HH:MM UTC time')
    parser.add_argument('--until', type=str, help='how until specific date time, YYYY-MM-DD HH:MM UTC time')
    parser.add_argument('--results-number', type=int, help='Show custom results number in show-top commands', default=default_results_number)
    parser.add_argument('--slower-than', type=float, help='Show logs slower than this value, in seconds')
    parser.add_argument('--slower-than-show-path', action='store_true', help='Show path in slower-than mode')

    

    args = parser.parse_args()

    if (args.from_file and args.namespace != default_namespace) or (args.from_file and args.labels != default_labels):
        parser.error("--namespace and --labels cannot be used with --from-file argument.")

    return args