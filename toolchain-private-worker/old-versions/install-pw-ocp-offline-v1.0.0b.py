#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Owned
__author__ = "IBM"
__copyright__ = "Copyright 2020, IBM GTS"
__credits__ = ["Frederic Spiers", "-","-"]
__license__ = "----"
__version__ = "1.0.0b"
__date__ = "25/06/2020"
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

def check_regex(string, pattern):
    if pattern.search(string):
        return True
    else:
        print("doesn't seem to be a valid entry for : "+string)

def get_original_img():
    img_to_download = []
    data = open(install_filename, 'r')
    for line in data:
        if 'gcr.io' in line or 'ibmcom' in line:
            if check_regex(line, gcr_img):
                line = re.sub(invisible_char, '', line)
                img_to_download.append(line)
            elif check_regex(line, ibmcom_img):
                line = re.sub(invisible_char, '', line)
                line = re.sub("image:", '', line)
                img_to_download.append(line)
            else:
                pass
    return img_to_download

def fomat_img_list(image_list, pattern_list):
    cleaned_list = []
    formated_list = []
    for img in image_list:
        cleaned_img = re.sub(digest_char, '', img)
        cleaned_list.append(cleaned_img)
        formated_img = cleaned_img
        for k, v in pattern_list.items():
            formated_img = re.sub(k, v, formated_img)
        formated_list.append(formated_img)
    return cleaned_list, formated_list

def OCP_Login(creds):
    print('OC login : https://'+creds.get("OCP_API"))
    os.system('/bin/oc43.sh login --insecure-skip-tls-verify=true https://'+creds.get("OCP_API")+' -u '+creds.get("OCP_user")+' -p '+creds.get("OCP_pwd"))
    token = os.popen('echo $(/bin/oc43.sh whoami -t)').read()
    token = re.sub(invisible_char, '', token)
    return token

def download_locally(img_list):
    for img in img_list:
        short_img = select_img_name(img)

        print('[ SKOPEO PULL ] > COPYING IMAGE FROM [[ docker://'+img+' ]] to [[ dir:/tmp/'+short_img+' ]]')
        os.system('skopeo copy '+'docker://'+img+' '+'dir:/tmp/'+short_img)

def upload_OCP(img_list, target):
    for img in img_list:
        short_img = select_img_name(re.sub(digest_char, '', img))
        token = OCP_Login(target)

        print('[ SKOPEO PUSH ] > COPYING IMAGE FROM [[ dir:/tmp/'+short_img+' ]] to [[ docker://'+img)
        os.system('skopeo copy '+'dir:/tmp/'+short_img+' '+'docker://'+img+' '+'--dest-creds '+target.get("OCP_user")+':'+token+' '+'--dest-tls-verify=false')


def display_downloaded_img():
    print('[[ List of locally dowloaded images ]]\n')
    os.system('ls -1 /tmp')

def print_original_img():
    data = open(install_filename, 'r')
    for line in data:
        if 'gcr.io' in line or 'ibmcom' in line:
            if not '>-' in line:
                if check_regex(line, gcr_img) or check_regex(line, ibmcom_img):
                    print('original image : '+line)

def print_result():
    data = open(install_filename, 'r')
    for line in data:
        if OCP_private_registry in line:
            if not '>-' in line:
                print('new image name : '+line)

def print_list(img_list):
    print('\n NEW LIST :')
    for img in img_list:
        print(img)

############################################################################
################################### Main ###################################
############################################################################

def main():
    # Timer
    start = timer()

    # Set variable
    env = dev6

    env_patterns_list = {
    'gcr.io' : env.get("OCP_registry"),
    'ibmcom' : env.get("OCP_registry")+'/ibmcom',
    '\\/tekton-releases\\/.*\\/' : '/tekton-releases/'
    }

    # Program
    get_pw_yaml()
    print_original_img()
    original_list = get_original_img()

    cleaned_list, formated_list = fomat_img_list(original_list, env_patterns_list)

    download_locally(cleaned_list)
    display_downloaded_img()
    upload_OCP(formated_list, env)
    replace_list_pattern(install_filename, patterns_list)
    #print_result()

    # Timer
    end = timer()
    print('[[ Elaspsed time : '+str(timedelta(seconds=end-start))+' ]]')
    
if __name__ == "__main__":
    main()