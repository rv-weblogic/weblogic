ansible-playbook -i inventory/apache_server_list.ini oneplay.yml  -u touser --become --extra-vars "appname_i=AUDITIntra env_dtup=DEV webservers=webservers_Inter"
