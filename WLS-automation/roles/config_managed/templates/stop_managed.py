connect('{{ weblogic_admin_user }}', '{{ weblogic_admin_password }}', '{{ weblogic_admin_url}}')
shutdown('{{ weblogic_servers[server].instance_name }}', entityType='Server', ignoreSessions='true', force='true', block='false')
