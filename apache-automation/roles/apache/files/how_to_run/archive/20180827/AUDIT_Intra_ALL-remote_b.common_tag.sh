ansible-playbook --tag="remove_app_home" -i ../../../../inventory/apache_server_list.ini ../../../../Apache_WL_App_All_steps.yml  -u touser --become --extra-vars "appname_i=AUDITIntra env_dtup=DEV webservers=webservers_Inter"
