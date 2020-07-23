__version__ = '1.1.0b'
#!/usr/local/bin/python3
from kubernetes import client, config
from openshift.dynamic import DynamicClient
import sys
import urllib3
from tabulate import tabulate
import argparse

##########################################################################
################################ VARIABLES ###############################
##########################################################################

data = []

##########################################################################
##########################################################################
##########################################################################

#config.load_kube_config()

def parse():
    parser = argparse.ArgumentParser(description='Auto annotate your pods for Velero Restic PVC backup. Annotation is done at Deployment level.')
    parser.add_argument('namespace', metavar='namespace-to-tag', type=str, help='the namespace you want to inspect for velero backup tagging')
    parser.add_argument('--version', action='version', version='%(prog)s '+__version__)
    args = parser.parse_args()
    return args

def setup_config():
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    return dyn_client

def load_table(namespace, dyn_client):
    #dyn_client = setup_config()

    ocp_pod = dyn_client.resources.get(api_version='v1', kind='Pod')
    pods = ocp_pod.get(namespace=namespace)

    for pod in pods.items:
        for volume in pod.spec.volumes:
            if volume.get('persistentVolumeClaim'):
                volName = volume.get('name')
                pvcName = volume.get('persistentVolumeClaim').get('claimName')
                print(pod.metadata.name+" has a volume "+volName+" with PVC "+pvcName+" to backup")
                for controllerInfo in pod.metadata.ownerReferences:
                    if controllerInfo.get('kind') == "StatefulSet":
                        print("we have a statefulset")
                        fill_data(namespace,pod.metadata.name,volName,pvcName,controllerInfo.get('name'),controllerInfo.get('kind'),controllerInfo.get('name'),controllerInfo.get('kind'))
                    else:
                        ocp_controller = dyn_client.resources.get(api_version='v1', kind=controllerInfo.get('kind'))
                        controller = ocp_controller.get(name=controllerInfo.get('name'),namespace=namespace)
                        for deployerInfo in controller.metadata.ownerReferences:
                            fill_data(namespace,pod.metadata.name,volName,pvcName,controllerInfo.get('name'),controllerInfo.get('kind'),deployerInfo.get('name'),deployerInfo.get('kind'))
    print(tabulate(data, headers=['Namespace', 'Pod', 'Volume-name', 'PVC', 'Controller', 'Controller-kind', 'Deployer', 'Deploy-kind'], tablefmt="fancy_grid"))

def fill_data(namespace, podName, volName, pvcName, controllerName, controllerKind, deployerName, deployerKind):
    if not data:
        data.append([namespace, podName, volName, pvcName, controllerName, controllerKind, deployerName, deployerKind])
    else:
        i = 0
        for row in data:
            i += 1
            if row[1] == podName:
                row[2] = row[2] +","+ volName
                break
            elif i == len(data):
                data.append([namespace, podName, volName, pvcName, controllerName, controllerKind, deployerName, deployerKind])
                break

def proceed_tag(dyn_client):
    confirm = input('proceed ? [Y/n]:')
    if confirm != 'Y':
        exit(0)

    for row in data:
        namespace = row[0]
        name = row[6]
        kind = row[7]
        volumes = row[2]

        body = {
            'kind': kind,
            'apiVersion': 'v1',
            'metadata': {'name': name},
            'spec': {
                'template': {'metadata': {'annotations': {'backup.velero.io/backup-volumes': volumes}}},
            }
        }
        print(body)
        deploy = dyn_client.resources.get(api_version='v1', kind=kind)
        deploy.patch(body=body, namespace=namespace)


def main():
    #Disabling warning messages
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #Parsing terminal arguments
    args = parse()
    #Execute program
    dyn_client = setup_config()
    load_table(args.namespace, dyn_client)
    proceed_tag(dyn_client)

if __name__ == "__main__":
    main()
