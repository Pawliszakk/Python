from models import Finding

def check_restricted_security_compliance(pod, findings):
    if pod.status.phase != "Running":
        return

    pod_security_context = pod.spec.security_context

    for container in pod.spec.containers:
        security_context = container.security_context

        # PSS-R-001: runAsNonRoot not true
        run_as_non_root = None
        if security_context and security_context.run_as_non_root is not None:
            run_as_non_root = security_context.run_as_non_root
        elif pod_security_context and pod_security_context.run_as_non_root is not None:
            run_as_non_root = pod_security_context.run_as_non_root

        if run_as_non_root is not True:
            finding = Finding(
                pod.metadata.namespace,
                pod.metadata.name,
                container.name,
                "PSS-Restricted",
                "PSS-R-001",
                "MEDIUM",
                {"runAsNonRoot": run_as_non_root},
                {"runAsNonRoot": True},
                "runAsNonRoot is not set to true"
            )
            findings.append(finding)

        # PSS-R-005: runAsUser explicitly set to 0 (root)
        run_as_user = None
        if security_context and security_context.run_as_user is not None:
            run_as_user = security_context.run_as_user
        elif pod_security_context and pod_security_context.run_as_user is not None:
            run_as_user = pod_security_context.run_as_user

        if run_as_user == 0:
            finding = Finding(
                pod.metadata.namespace,
                pod.metadata.name,
                container.name,
                "PSS-Restricted",
                "PSS-R-005",
                "HIGH",
                {"runAsUser": 0},
                {"runAsUser": "non-zero UID"},
                "Container explicitly runs as root (UID 0)"
            )
            findings.append(finding)

        # PSS-R-002: allowPrivilegeEscalation not false
        allow_priv_escalation = None
        if security_context and security_context.allow_privilege_escalation is not None:
            allow_priv_escalation = security_context.allow_privilege_escalation

        if allow_priv_escalation is not False:
            finding = Finding(
                pod.metadata.namespace,
                pod.metadata.name,
                container.name,
                "PSS-Restricted",
                "PSS-R-002",
                "MEDIUM",
                {"allowPrivilegeEscalation": allow_priv_escalation},
                {"allowPrivilegeEscalation": False},
                "allowPrivilegeEscalation is not set to false"
            )
            findings.append(finding)

        # PSS-R-003: capabilities.drop missing ALL
        dropped_caps = []
        if security_context and security_context.capabilities and security_context.capabilities.drop:
            dropped_caps = security_context.capabilities.drop

        if "ALL" not in dropped_caps:
            finding = Finding(
                pod.metadata.namespace,
                pod.metadata.name,
                container.name,
                "PSS-Restricted",
                "PSS-R-003",
                "MEDIUM",
                {"capabilities.drop": dropped_caps},
                {"capabilities.drop": ["ALL"]},
                "capabilities.drop does not include ALL"
            )
            findings.append(finding)

        # PSS-R-004: seccomp profile not RuntimeDefault
        seccomp_type = None
        if security_context and security_context.seccomp_profile:
            seccomp_type = security_context.seccomp_profile.type
        elif pod_security_context and pod_security_context.seccomp_profile:
            seccomp_type = pod_security_context.seccomp_profile.type

        if seccomp_type not in ("RuntimeDefault", "Localhost"):
            finding = Finding(
                pod.metadata.namespace,
                pod.metadata.name,
                container.name,
                "PSS-Restricted",
                "PSS-R-004",
                "MEDIUM",
                {"seccompProfile.type": seccomp_type},
                {"seccompProfile.type": "RuntimeDefault"},
                "seccomp profile is not RuntimeDefault"
            )
            findings.append(finding)