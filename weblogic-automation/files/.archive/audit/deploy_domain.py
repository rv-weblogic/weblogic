connect('{{ weblogic_admin_user }}', '{{ weblogic_admin_password }}', 't3://{{ weblogic_instance_admin_address }}:{{ weblogic_instance_admin_port }}')

#edit()
#startEdit()
#cd('/Servers/auditAs01/ServerStart/auditAs01')
#cmo.setArguments('-Djava.security.egd=file:/dev/./urandom -DAPP_ROOT=/opt/wl12c/domains/audit/applications -DAUDIT_ROOT=/opt/wl12c/domains/audit/applications/audit -DAWS_ROOT=/opt/wl12c/domains/audit/applications/auditws -Dsec.admin.directoryCredentials=rusadmin -Dweblogic.security.SSL.ignoreHostnameVerification=true -Dweblogic.wsee.useRequestHost=true')
#cd('/Servers/auditAs02/ServerStart/auditAs02')
#cmo.setArguments('-Djava.security.egd=file:/dev/./urandom -DAPP_ROOT=/opt/wl12c/domains/audit/applications -DAUDIT_ROOT=/opt/wl12c/domains/audit/applications/audit -DAWS_ROOT=/opt/wl12c/domains/audit/applications/auditws -Dsec.admin.directoryCredentials=rusadmin -Dweblogic.security.SSL.ignoreHostnameVerification=true -Dweblogic.wsee.useRequestHost=true')
#activate()

deploy(appName="auditApp", path="/opt/wl12c/domains/audit/applications/audit/auditApp.ear", targets="auditCluster", stageMode="nostage")
deploy(appName="auditservice", path="/opt/wl12c/domains/audit/applications/auditws/auditservice.ear", targets="auditCluster", stageMode="nostage")
