ansible-playbook --tag="build_end_to_end" -i ../../../../inventory/apache_server_list_vm.ini ../../../../Apache_WL_App_All_steps.yml  -u "srv.mto.tsoadm.qa@CIHS.AD.GOV.ON.CA"  --become --extra-vars "appname_i=AUDITIntra env_dtup=DEV webservers=webservers_Inter"
