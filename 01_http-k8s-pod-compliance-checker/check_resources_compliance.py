from models import Finding

def check_resources_compliance(pod,findings):
    if pod.status.phase != "Running":
        return
    
    for container in pod.spec.containers:
        requests = container.resources.requests
        limits = container.resources.limits

        if not requests and not limits:
            finding = Finding(
                pod.metadata.namespace,
                pod.metadata.name,
                container.name,
                "Resources",
                "RES-005",
                "HIGH",
                requests,
                {
                "limits": {"cpu": "CPU_VALUE", "memory": "MEMORY_VALUE"},
                "requests": {"cpu": "CPU_VALUE", "memory": "MEMORY_VALUE"}
                },
                "Requests and limits are missing"
            )
            findings.append(finding)

        else:

            if requests:
                requests_cpu = requests.get("cpu")
                requests_memory = requests.get("memory")

                if not requests_cpu:
                    print("Są requesty bez cpu")
                    finding = Finding(
                        pod.metadata.namespace,
                        pod.metadata.name,
                        container.name,
                        "Resources",
                        "RES-001",
                        "HIGH",
                        requests,
                        "{'cpu': 'CPU_VALUE', 'memory': 'MEMORY_VALUE'}",
                        "CPU Request is missing"
                    )
                    findings.append(finding)
                
                if not requests_memory:
                    finding = Finding(
                        pod.metadata.namespace,
                        pod.metadata.name,
                        container.name,
                        "Resources",
                        "RES-002",
                        "HIGH",
                        requests,
                        "{'cpu': 'CPU_VALUE', 'memory': 'MEMORY_VALUE'}",
                        "Memory Request is missing"
                    )
                    findings.append(finding)

            else:
                finding = Finding(
                    pod.metadata.namespace,
                    pod.metadata.name,
                    container.name,
                    "Resources",
                    "RES-006",
                    "HIGH",
                    requests,
                    "{'cpu': 'CPU_VALUE', 'memory': 'MEMORY_VALUE'}",
                    "Requests are missing"
                )
                findings.append(finding)

            if limits:
                limits_cpu = limits.get("cpu")
                limits_memory = limits.get("memory")

                if not limits_cpu:
                    finding = Finding(
                        pod.metadata.namespace,
                        pod.metadata.name,
                        container.name,
                        "Resources",
                        "RES-004",
                        "LOW",
                        limits,
                      "{'cpu': 'CPU_VALUE', 'memory': 'MEMORY_VALUE'}",
                      "CPU Limits are missing"
                    )
                    findings.append(finding)

                if not limits_memory:
                    finding = Finding(
                        pod.metadata.namespace,
                        pod.metadata.name,
                        container.name,
                        "Resources",
                        "RES-003",
                        "MEDIUM",
                        limits,
                      "{'cpu': 'CPU_VALUE', 'memory': 'MEMORY_VALUE'}",
                      "Memory limits are missing"
                    )
                    findings.append(finding)

            else:
                finding = Finding(
                    pod.metadata.namespace,
                    pod.metadata.name,
                    container.name,
                    "Resources",
                    "RES-007",
                    "HIGH",
                    limits,
                    "{'cpu': 'CPU_VALUE', 'memory': 'MEMORY_VALUE'}",
                    "Limits are missing"
                )
                findings.append(finding)