from connect_to_k8s import connect_to_k8s
from get_pods import get_pods
from get_args import get_args
from check_baseline_security_compliance import check_baseline_security_compliance
from check_restricted_security_compliance import check_restricted_security_compliance 
from check_runtime_compliance import check_runtime_compliance
from check_runtime_usage import check_runtime_usage
from check_resources_compliance import check_resources_compliance
from show_summary import show_summary
from show_findings import show_findings

def main():

    args = get_args()

    findings = []

    v1, metrics_api = connect_to_k8s()

    pods = get_pods(v1,args.namespace)

    for pod in pods.items:

        check_resources_compliance(pod, findings)
        check_runtime_compliance(pod,findings)
        check_runtime_usage(pod,metrics_api,findings)
        check_baseline_security_compliance(pod,findings)
        check_restricted_security_compliance(pod,findings)

    filtered_findings = show_findings(findings, args)

    show_summary(filtered_findings, len(pods.items))




if __name__ == "__main__":
    main()