from models import Finding

def check_runtime_usage(pod, metrics_api, findings):
    if pod.status.phase != "Running":
        return

    try:
        pod_metrics = metrics_api.get_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=pod.metadata.namespace,
            plural="pods",
            name=pod.metadata.name
        )
    except Exception as e:
        print(e)
        return

    usage_by_container = {c["name"]: c["usage"] for c in pod_metrics["containers"]}

    for container in pod.spec.containers:
        limits = container.resources.limits
        if not limits:
            continue

        usage = usage_by_container.get(container.name)
        if not usage:
            continue

        finding = Finding(
            pod.metadata.namespace,
            pod.metadata.name,
            container.name,
            "Runtime",
            "RT-002",
            "INFO",
            usage,
            limits,
            "Current resource usage vs configured limits"
        )
        findings.append(finding)