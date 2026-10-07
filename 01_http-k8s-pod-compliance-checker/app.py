from types import SimpleNamespace

from flask import Flask, render_template, request

from connect_to_k8s import connect_to_k8s
from get_pods import get_pods
from check_baseline_security_compliance import check_baseline_security_compliance
from check_restricted_security_compliance import check_restricted_security_compliance
from check_runtime_compliance import check_runtime_compliance
from check_runtime_usage import check_runtime_usage
from check_resources_compliance import check_resources_compliance
from show_findings import filter_findings
from show_summary import summarize_counts

app = Flask(__name__)

SEVERITIES = ["ok", "info", "low", "medium", "high"]
STANDARDS = ["baseline", "restricted", "resources", "runtime"]


def build_filter_args(form):
    return SimpleNamespace(
        namespace=form.get("namespace") or None,
        include_system=form.get("include_system") == "on",
        ok="ok" in form.getlist("severity"),
        info="info" in form.getlist("severity"),
        low="low" in form.getlist("severity"),
        medium="medium" in form.getlist("severity"),
        high="high" in form.getlist("severity"),
        baseline="baseline" in form.getlist("standard"),
        restricted="restricted" in form.getlist("standard"),
        resources="resources" in form.getlist("standard"),
        runtime="runtime" in form.getlist("standard"),
    )


def run_checks(namespace):
    v1, metrics_api = connect_to_k8s()
    if v1 is None:
        raise RuntimeError("Could not connect to the Kubernetes cluster (check your kubeconfig).")

    pods = get_pods(v1, namespace)

    findings = []
    for pod in pods.items:
        check_resources_compliance(pod, findings)
        check_runtime_compliance(pod, findings)
        check_runtime_usage(pod, metrics_api, findings)
        check_baseline_security_compliance(pod, findings)
        check_restricted_security_compliance(pod, findings)

    return findings, len(pods.items)


@app.route("/", methods=["GET"])
def index():
    args = build_filter_args(request.args)

    findings = None
    counts = None
    pods_count = None
    error = None

    if request.args:
        try:
            all_findings, pods_count = run_checks(args.namespace)
            findings = filter_findings(all_findings, args)
            counts = summarize_counts(findings)
        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        severities=SEVERITIES,
        standards=STANDARDS,
        selected_severities=request.args.getlist("severity"),
        selected_standards=request.args.getlist("standard"),
        namespace=args.namespace or "",
        include_system=args.include_system,
        findings=findings,
        counts=counts,
        pods_count=pods_count,
        error=error,
        submitted=bool(request.args),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
