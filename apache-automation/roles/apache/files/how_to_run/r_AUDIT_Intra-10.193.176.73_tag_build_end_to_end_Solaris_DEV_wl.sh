#!/bin/bash
whoami
PATH_SELF="$(dirname $0)"

chmod 600 "${PATH_SELF}"/touserUID1002key_rsa
ansible-playbook --tag="build_end_to_end" -i "${PATH_SELF}"/../../../../inventory/sdcgisazapmdw34_vm.ini "${PATH_SELF}"/../../../../Apache_WL_App_All_steps.yml  -u "touser" --private-key="${PATH_SELF}"/touserUID1002key_rsa  --become --extra-vars "appname_i=AUDITIntra env_dtup=DEV webservers=webservers_Inter wl_server1_port=7120 wl_server2_port=7120 wl_server1_host_line_in_hosts_file='10.77.6.13 etcdqpvsapwlg01 etcdqpvsapwlg01.cihs.gov.on.ca saedev01' wl_server2_host_line_in_hosts_file='10.77.6.23 etcdqpvsapwlg03 etcdqpvsapwlg03.cihs.gov.on.ca saedev02'"
