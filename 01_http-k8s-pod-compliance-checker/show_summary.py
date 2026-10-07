def summarize_counts(findings):
    counts = {"OK": 0, "INFO": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
    return counts


def show_summary(findings, pods_count):
    counts = summarize_counts(findings)

    print("\n")
    print("SUMMARY")
    print("--------------------------")
    print(f"PODS CHECKED: { pods_count }")
    print(f'OK: {counts["OK"]}, INFO: {counts["INFO"]}, LOW: {counts["LOW"]}, MEDIUM: {counts["MEDIUM"]}, HIGH: {counts["HIGH"]}')