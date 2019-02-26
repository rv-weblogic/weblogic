#!/bin/bash
whoami
PATH_SELF="$(dirname $0)"

chmod 600 "${PATH_SELF}"/touserUID1002key_rsa
ansible-playbook --tag="build_end_to_end" -i "${PATH_SELF}"/../../../../inventory/sdcgisazapmdw34_vm.ini "${PATH_SELF}"/../../../../Apache_WL_App_All_steps.yml  -u "touser" --private-key="${PATH_SELF}"/touserUID1002key_rsa  --become --extra-vars "appname_i=AUDITIntra env_dtup=DEV webservers=webservers_Inter WebLogicCluster=etcdqpvsapwlg01.cihs.gov.on.ca:7120,etcdqpvsapwlg03.cihs.gov.on.ca:7120"
