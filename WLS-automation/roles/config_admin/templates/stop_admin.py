nmConnect('{{ weblogic_admin_user }}', '{{ weblogic_admin_password }}', '{{ weblogic_servers[server].node_manager_address }}','{{ weblogic_servers[server].node_manager_port }}', '{{ weblogic_domain_name }}')
nmKill('{{ weblogic_servers[server].instance_name }}')
