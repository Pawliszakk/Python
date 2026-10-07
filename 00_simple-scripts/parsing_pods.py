import subprocess
import json


def get_pods():
    command  = ["kubectl","get","pods","-A","-o","json"]
    
    try:
        result = subprocess.run(
        command,
        capture_output=True,
        text=True
        )

        if result.returncode != 0:
            print("Command failed", result.stderr)
            return 
        
        data = json.loads(result.stdout)

        not_running_pods = []

        print("NAMESPACE NAME PHASE")
        for pod in data["items"]:

            namespace = pod["metadata"]["namespace"]
            name = pod["metadata"]["name"]
            phase = pod["status"]["phase"]
            
            print(namespace, name, phase)

            if phase.lower() != "running":
                not_running_pods.append(f'{namespace}/{name}') 
        print("NOT RUNNING PODS:")
        for pod in not_running_pods:
            print(pod)
    except Exception as e:
        print(e)

get_pods()