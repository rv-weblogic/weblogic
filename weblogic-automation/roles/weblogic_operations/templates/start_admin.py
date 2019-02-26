nmConnect('{{ weblogic_admin_user }}', '{{ weblogic_admin_password }}', '{{ weblogic_node_manager_address }}', '{{ weblogic_node_manager_port }}', '{{ weblogic_domain_name }}')
nmStart('{{ weblogic_instance_name }}')
