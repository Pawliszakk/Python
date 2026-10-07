from models import Finding

BASELINE_ALLOWED_CAPABILITIES = {
    "AUDIT_WRITE", "CHOWN", "DAC_OVERRIDE", "FOWNER", "FSETID",
    "KILL", "MKNOD", "NET_BIND_SERVICE", "SETFCAP", "SETGID",
    "SETPCAP", "SETUID", "SYS_CHROOT"
}


def check_baseline_security_compliance(pod, findings):
    if pod.status.phase != "Running":
        return
    # PSS-B-002: hostNetwork / hostPID / hostIPC
    if pod.spec.host_network or pod.spec.host_pid or pod.spec.host_ipc:
        finding = Finding(
            pod.metadata.namespace,
            pod.metadata.name,
            "",
            "PSS-Baseline",
            "PSS-B-002",
            "HIGH",
            {
                "hostNetwork": pod.spec.host_network,
                "hostPID": pod.spec.host_pid,
                "hostIPC": pod.spec.host_ipc
            },
            {"hostNetwork": False, "hostPID": False, "hostIPC": False},
            "hostNetwork/hostPID/hostIPC is enabled"
        )
        findings.append(finding)

    # PSS-B-004: hostPath volume
    if pod.spec.volumes:
        for volume in pod.spec.volumes:
            if volume.host_path:
                finding = Finding(
                    pod.metadata.namespace,
                    pod.metadata.name,
                    "",
                    "PSS-Baseline",
                    "PSS-B-004",
                    "HIGH",
                    {"volume": volume.name, "hostPath": volume.host_path.path},
                    {"hostPath": None},
                    "hostPath volume is mounted"
                )
                findings.append(finding)

    # Per-container checks
    for container in pod.spec.containers:
        security_context = container.security_context

        # PSS-B-001: privileged
        if security_context and security_context.privileged:
            finding = Finding(
                pod.metadata.namespace,
                pod.metadata.name,
                container.name,
                "PSS-Baseline",
                "PSS-B-001",
                "HIGH",
                {"privileged": True},
                {"privileged": False},
                "Container is running as privileged"
            )
            findings.append(finding)

        # PSS-B-003: capabilities.add outside Baseline set
        if security_context and security_context.capabilities and security_context.capabilities.add:
            added_caps = set(security_context.capabilities.add)
            disallowed_caps = added_caps - BASELINE_ALLOWED_CAPABILITIES

            if disallowed_caps:
                finding = Finding(
                    pod.metadata.namespace,
                    pod.metadata.name,
                    container.name,
                    "PSS-Baseline",
                    "PSS-B-003",
                    "HIGH",
                    {"added_capabilities": list(disallowed_caps)},
                    {"allowed_capabilities": list(BASELINE_ALLOWED_CAPABILITIES)},
                    "Capabilities outside the Baseline set were added"
                )
                findings.append(finding)
