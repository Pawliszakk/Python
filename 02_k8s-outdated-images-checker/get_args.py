import argparse


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan k8s pods for outdated container images."
    )
    parser.add_argument(
        "-n", "--namespace",
        default=None,
        help="Only check pods in this namespace (default: all namespaces)",
    )
    return parser.parse_args()
