def show_summary(findings, pods_count):
    ok_counter = 0
    info_counter = 0
    low_counter = 0
    medium_counter = 0
    high_counter = 0

    for finding in findings:
        severity = finding.severity
        isOk = severity == "OK"
        isInfo = severity == "INFO"
        isLow = severity == "LOW"
        isMedium = severity == "MEDIUM"
        isHigh = severity == "HIGH"

        if isOk:
            ok_counter += 1
        elif isInfo:
            info_counter += 1
        elif isLow:
            low_counter += 1
        elif isMedium:
            medium_counter += 1
        elif isHigh:
            high_counter += 1

    print("\n")
    print("SUMMARY")
    print("--------------------------")
    print(f"PODS CHECKED: { pods_count }")
    print(f'OK: {ok_counter}, INFO: {info_counter}, LOW: {low_counter}, MEDIUM: {medium_counter}, HIGH: {high_counter}')