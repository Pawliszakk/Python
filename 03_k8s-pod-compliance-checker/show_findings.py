import json
import csv

SEVERITY_COLORS = {
    "OK":     "\033[32m",  # green
    "INFO":   "\033[36m",  # cyan
    "LOW":    "\033[34m",  # blue
    "MEDIUM": "\033[33m",  # yellow
    "HIGH":   "\033[31m",  # red
}
RESET = "\033[0m"

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


def show_findings(findings, args):
    filtered = findings

    if not args.include_system and not args.namespace:
        filtered = [f for f in filtered if f.namespace not in SYSTEM_NAMESPACES]

    if args.ok or args.info or args.low or args.medium or args.high:
        allowed_severities = set()
        if args.ok:
            allowed_severities.add("OK")
        if args.info:
            allowed_severities.add("INFO")
        if args.low:
            allowed_severities.add("LOW")
        if args.medium:
            allowed_severities.add("MEDIUM")
        if args.high:
            allowed_severities.add("HIGH")

        filtered = [f for f in filtered if f.severity in allowed_severities]

    if args.baseline or args.restricted or args.resources or args.runtime:
        allowed_standards = set()
        if args.baseline:
            allowed_standards.add("PSS-Baseline")
        if args.restricted:
            allowed_standards.add("PSS-Restricted")
        if args.resources:
            allowed_standards.add("Resources")
        if args.runtime:
            allowed_standards.add("Runtime")

        filtered = [f for f in filtered if f.standard in allowed_standards]

    if args.output == "json":
        print(json.dumps([vars(f) for f in filtered], indent=2))

    elif args.output == "yaml":
        import yaml
        print(yaml.dump([vars(f) for f in filtered], default_flow_style=False))

    elif args.output == "csv":
        if not filtered:
            print("No findings to write.")
            return filtered
        fieldnames = vars(filtered[0]).keys()
        with open(args.csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for finding in filtered:
                writer.writerow(vars(finding))
        print(f"Wrote {len(filtered)} findings to {args.csv_path}")

    else:  # human
        for finding in filtered:
            color = SEVERITY_COLORS.get(finding.severity, "")
            severity = f"{color}{finding.severity}{RESET}"
            container_part = f"Container {finding.container} | " if finding.container else ""
            print(f" Pod {finding.namespace}/{finding.pod} | {container_part}{severity} | {finding.message}")

    return filtered