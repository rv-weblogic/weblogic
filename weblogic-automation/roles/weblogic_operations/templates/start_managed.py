connect('{{ weblogic_admin_user }}', '{{ weblogic_admin_password }}', '{{ weblogic_admin_url}}')
start('{{ weblogic_instance_name }}', type='Server', block='true')
