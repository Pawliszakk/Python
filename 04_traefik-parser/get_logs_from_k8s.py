from connect_to_k8s import connect_to_k8s

def get_logs_from_k8s(ingress_namespace, ingress_labels, logs_number):

    v1 = connect_to_k8s(ingress_namespace, ingress_labels)

    pods = v1.list_namespaced_pod(
        namespace=ingress_namespace, 
        label_selector=ingress_labels)

    all_logs = []
    if len(pods.items) > 0:
        number_of_lines_to_get_from_pod = int(logs_number/len(pods.items))
    else:
        print("We did not find any pods that match given criteria.")
        raise ValueError("No pods found.")
    for pod in pods.items:
        pod_name = pod.metadata.name
        
        for container in pod.spec.containers:
            container_name = container.name
            try:
                logs = v1.read_namespaced_pod_log(
                    name=pod_name, 
                    namespace=ingress_namespace, 
                    container=container_name, 
                    tail_lines=number_of_lines_to_get_from_pod)

                container_logs = logs.strip("b'\"").encode().decode("unicode_escape").splitlines()
                all_logs.extend(container_logs)

            except Exception as e:
                print(f"Error getting logs for pod {pod_name}, container {container_name}: {e}")
    return all_logs

