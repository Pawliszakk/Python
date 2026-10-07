import requests
from kubernetes import client, config
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_sites():
    ingress_hosts = []    

    try:
        print("Getting available hosts data from kubernetes api...")
        config.load_kube_config()
        configuration = client.Configuration.get_default_copy()
        configuration.verify_ssl = False
        client.Configuration.set_default(configuration)
        networking_v1 = client.NetworkingV1Api()
        ingresses = networking_v1.list_ingress_for_all_namespaces()

        for ingress in ingresses.items:
            for rule in ingress.spec.rules:
                ingress_hosts.append(rule.host)

    except Exception as e:
        print("Something went wrong with getting hosts data from kubernetes api.")
        print(e)
        return
    
    print(f'Fetched {len(ingress_hosts)} hosts from kubernetes...')
    check_sites(ingress_hosts)

def check_sites(ingress_hosts):
    ok_sites = []
    bad_sites = []

    print("Starting testing...")
    for host in ingress_hosts:
        try:
            url = f'https://{host}'
            res = requests.get(url, verify=False, timeout=5)
            
            print(f"CHECKING {host} --> {res.status_code}")

            if res.status_code != 200:
                bad_sites.append(host)
            else:
                ok_sites.append(host)

        except Exception as e:
            print(f"Something went wrong with {host}")
            bad_sites.append(host)
            print(e)

    print(f"OK_SITES: {len(ok_sites)}")
    print(f"BAD_SITES: {len(bad_sites)}")

    if len(bad_sites) > 0:
        print("PRINTING BAD SITES")
        for bad_site in bad_sites:
            print(bad_site)
get_sites()