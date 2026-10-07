from kubernetes import config, client
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connect_to_k8s():
  try:
    config.load_kube_config()
    configuration = client.Configuration.get_default_copy()
    configuration.verify_ssl = False
    client.Configuration.set_default(configuration)

    v1 = client.CoreV1Api()
    metrics_api = client.CustomObjectsApi()

    return v1, metrics_api
  except Exception as e:
    print(e)