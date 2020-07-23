#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Owned
__author__ = "IBM"
__copyright__ = "Copyright 2020, IBM GTS"
__credits__ = ["Frederic Spiers", "-","-"]
__license__ = "----"
__version__ = "2.0.0"
__date__ = "04/07/2020"
__maintainers__ = ["Frederic Spiers"]
__email__ = "frederic.spiers-isc.france@ibm.com"
__status__ = "Development"

############################################################################
################################## Import ##################################
############################################################################

import os
import sys
import requests
import fileinput
import re
import yaml
from timeit import default_timer as timer
from datetime import timedelta

############################################################################
################################# Variables ################################
############################################################################

#REGISTRY
region="eu-de"
OCP_private_registry="image-registry.openshift-image-registry.svc:5000"
dockerio_mapping_prefix=""
install_filename="updated-private-worker-install-ocp.yaml"

#INT1
int1 =	{
    "OCP_API": "api.ocp4-int1.intibm.local:6443",
    "OCP_registry": "default-route-openshift-image-registry.apps.ocp4-int1.intibm.local",
    "OCP_user": "kubeadmin",
    "OCP_pwd": "fQB6g-CpNPP-mEKw5-9ABXE"
}
#INT2
int2 =	{
    "OCP_API": "api.ocp4-int2.intibm.local:6443",
    "OCP_registry": "default-route-openshift-image-registry.apps.ocp4-int2.intibm.local",
    "OCP_user": "kubeadmin",
    "OCP_pwd": ""
}
#DEV5
dev5 =	{
    "OCP_API": "api.ocp4-dev5.devibm.local:6443",
    "OCP_registry": "default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local",
    "OCP_user": "kubeadmin",
    "OCP_pwd": "tbbxZ-sqE7P-hNqhx-T5TDt"
}

#DEV6
dev6 =	{
    "OCP_API": "api.devibm.local:6443",
    "OCP_registry": "default-route-openshift-image-registry.apps.devibm.local",
    "OCP_user": "",
    "OCP_pwd": ""
}

#REGEX
patterns_list = {
    'gcr.io' : OCP_private_registry,
    'ibmcom' : OCP_private_registry+'/ibmcom',
    '@sha.*' : '',
    '\\/tekton-releases\\/.*\\/' : '/tekton-releases/'
}

gcr_img = re.compile('^([\\s\\t]*gcr.io\\/tekton-releases\\/.*\\:.*@sha.*)$')
ibmcom_img = re.compile('^([\\s\\t]*.*ibmcom\\/.*\\:.*)$')
invisible_char = '[\\s\\t\\n]+'
digest_char = '@sha.*'

############################################################################
################################# Functions ################################
############################################################################

def setEnv():
    if os.environ.get('TARGET') is None:
        print("Error : please set ENV VAR 'TARGET' on your system" )
        exit(1)
    else:
        if os.environ.get('TARGET') in globals():
            env = globals()[os.environ.get('TARGET')]
            return env
        else:
            print('Error : Environment variable '+os.environ.get('TARGET')+' does not exist. Please choose a proper one.')
            exit(1)

def setCreds(env):
    if os.environ.get('OC_USER') is None and os.environ.get('OC_PWD') is None:
        pass
    else:
        env['OCP_user'] = os.environ.get('OC_USER')
        env['OCP_pwd'] = os.environ.get('OC_PWD')

def get_pw_yaml():
    #os.system('curl -o '+install_filename+' https://private-worker-service.'+region+'.devops.cloud.ibm.com/install')
    r = requests.get('https://private-worker-service.'+region+'.devops.cloud.ibm.com/install', allow_redirects=True)
    open(install_filename, 'wb').write(r.content)

def select_img_name(string):
    tab = string.split('/')
    return tab[-1]

def replace_list_pattern(filename, pattern_list):
    file_to_modify = open(filename, 'rt')
    data = file_to_modify.read()
    for k, v in pattern_list.items():
        data = re.sub(k, v, data)
    file_to_modify.close()
    file_to_modify = open(filename, 'wt')
    file_to_modify.write(data)
    file_to_modify.close()

def configure_pw_proxy(filename):
    ro_data = open(filename, 'rt')
    ymls = list(yaml.safe_load_all(ro_data))
    for yml in ymls:
        if yml['kind'] == 'Deployment' and yml['metadata']['name'] == 'private-worker-agent':
            ymlEnv = (yml['spec']['template']['spec']['containers'][0]['env'])
            ymlEnv.append({'name': 'HTTPS_PROXY', 'value': os.environ.get('OC_HTTPS_PROXY')})
            ymlEnv.append({'name': 'NO_PROXY', 'value': '172.30.0.1'})
    ro_data.close()
    rw_data = open(filename, 'wt')
    yaml.dump_all(ymls, rw_data)
    rw_data.close()

def check_regex(string, pattern):
    if pattern.search(string):
        return True
    else:
        pass

def get_original_img():
    img_to_download = []
    data = open(install_filename, 'r')
    for line in data:
        if 'gcr.io' in line or 'ibmcom' in line:
            if check_regex(line, gcr_img):
                line = re.sub(invisible_char, '', re.sub(digest_char, '', line))
                img_to_download.append(line)
            elif check_regex(line, ibmcom_img):
                line = re.sub(invisible_char, '', re.sub(digest_char, '', line))
                line = re.sub("image:", '', line)
                img_to_download.append(line)
            else:
                pass
    return img_to_download

def fomat_img_list(image_list, pattern_list):
    formated_list = []
    for img in image_list:
        formated_img = img
        for k, v in pattern_list.items():
            formated_img = re.sub(k, v, formated_img)
        formated_list.append(formated_img)
    return formated_list

def OCP_Login(creds):
    print('OC login : https://'+creds.get("OCP_API"))
    os.system('/bin/oc43.sh login --insecure-skip-tls-verify=true https://'+creds.get("OCP_API")+' -u '+creds.get("OCP_user")+' -p '+creds.get("OCP_pwd"))
    token = os.popen('echo $(/bin/oc43.sh whoami -t)').read()
    token = re.sub(invisible_char, '', token)
    return token

def download_locally(img_list):
    for img in img_list:
        print('[ SKOPEO PULL ] > COPYING IMAGE FROM [[ docker://'+img+' ]] to [[ dir:/tmp/'+select_img_name(img)+' ]]')
        os.system('skopeo copy '+'docker://'+img+' '+'dir:/tmp/'+select_img_name(img))

def upload_OCP(img_list, target, token):
    for img in img_list:
        print('[ SKOPEO PUSH ] > COPYING IMAGE FROM [[ dir:/tmp/'+select_img_name(img)+' ]] to [[ docker://'+img)
        os.system('skopeo copy '+'dir:/tmp/'+select_img_name(img)+' '+'docker://'+img+' '+'--dest-creds '+target.get("OCP_user")+':'+token+' '+'--dest-tls-verify=false')

def install_pw():
    print('[ OCP ] > INSTALLING PRIVATE WORKER')
    os.system('/bin/oc43.sh apply -f '+install_filename)
    print('[ OCP ] > APPLYING PULL IMAGE POLICY')
    os.system('/bin/oc43.sh policy add-role-to-user system:image-puller system:serviceaccount:tekton-pipelines:tekton-pipelines-controller --namespace=tekton-releases')
    os.system('/bin/oc43.sh policy add-role-to-user system:image-puller system:serviceaccount:tekton-pipelines:private-worker-agent --namespace=tekton-releases')
    print('[ OCP ] > APPLYING SERVICE ACCOUNT POLICY')
    os.system('/bin/oc43.sh adm policy add-scc-to-user anyuid system:serviceaccount:tekton-pipelines:tekton-pipelines-controller')

############################################################################
################################### Main ###################################
############################################################################

def main():
    # Timer
    start = timer()

    # Set variables
    env = setEnv()
    setCreds(env)

    env_patterns_list = {
    'gcr.io' : env.get("OCP_registry"),
    'ibmcom' : env.get("OCP_registry")+'/ibmcom',
    '\\/tekton-releases\\/.*\\/' : '/tekton-releases/'
    }

    # Program
    get_pw_yaml()
    original_list = get_original_img()
    download_locally(original_list)
    formated_list = fomat_img_list(original_list, env_patterns_list)
    token = OCP_Login(env)
    upload_OCP(formated_list, env, token)
    replace_list_pattern(install_filename, patterns_list)
    if os.environ.get('OC_HTTPS_PROXY'):
        configure_pw_proxy(install_filename)
    install_pw()

    # Timer
    end = timer()
    print('[[ Elapsed time : '+str(timedelta(seconds=end-start))+' ]]')
    
if __name__ == "__main__":
    main()