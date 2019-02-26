package main

import (
	"encoding/json"
	"fmt"
	"log"
)

func main() {

	root := Root{
		Internal: &Internal{
			Timeout:     5,
			TimeoutLong: 60,
		},
		WLST: &WLST{
			EnvVars: []string{
				`USER_MEM_ARGS="-Djava.security.egd=file:/dev/./urandom -XX:MaxPermSize=512M"`,
			},
			ScriptPath: "/opt/wl12c/weblogic/wlserver/common/bin/wlst.sh",
			ScriptArgs: []string{
				"-skipWLSModuleScanning",
			},
		},
		Credential: &Credential{
			Username: "audit12",
			Password: "mtogov123",
			Protocol: "t3",
		},
		Edit: &Edit{
			SaveChanges:     false,
			ActivateChanges: false,
		},
		Domain: &Domain{
			Name:                  "audit",
			DomainTemplate:        "/opt/wl12c/weblogic/wlserver/common/templates/wls/wls.jar",
			DomainHome:            "/opt/wl12c/domains/audit",
			JavaHome:              "/opt/wl12c/jdk",
			ProductionModeEnabled: "true",
			ServerStartMode:       "prod",
			AdminServer: &Server{
				Name: "auditAdmin",
				Host: "saedev01",
				Port: "17120",
				Type: "admin",
				Machine: &Machine{
					BuildMode: "offline",
					Name:      "auditHostAdmin",
					Host:      "saedev01",
					Port:      "27120",
					Protocol:  "SSL",
					Type:      "UnixMachine",
				},
				ServerStart: &ServerStart{
					Arguments: []string{
						"-Djava.security.egd=file:/dev/./urandom",
						"-Dweblogic.security.SSL.ignoreHostnameVerification=true",
						"-Dsec.admin.directoryCredentials=rusadmin",
					},
				},
				Logging: &Logging{
					LogFileName:          "logs/auditAdmin.%yyyy%%MM%%dd%-%k%%mm%.log",
					RotationType:         "byTime",
					RotationFileSize:     "5000",
					BeginRotationTime:    "23:59",
					RotationInterval:     "24",
					NumberOfFilesLimited: "true",
					FileCount:            "125",
				},
			},
			Cluster: &Cluster{
				Name:          "auditCluster",
				MessagingMode: "unicast",
				Servers: []*Server{
					{
						Name: "auditAs01",
						Host: "saedev01",
						Port: "7121",
						Type: "managed",
						Machine: &Machine{
							BuildMode: "online",
							Name:      "auditHostAs01",
							Host:      "saedev01",
							Port:      "27121",
							Protocol:  "SSL",
							Type:      "UnixMachine",
						},
						ServerStart: &ServerStart{
							Arguments: []string{
								"-Djava.security.egd=file:/dev/./urandom",
								"-Dweblogic.wsee.useRequestHost=true",
								"-DAPP_ROOT=/opt/wl12c/domains/audit/applications",
								"-DAUDIT_ROOT=/opt/wl12c/domains/audit/applications/audit",
								"-DAWS_ROOT=/opt/wl12c/domains/audit/applications/auditws",
							},
						},
						Logging: &Logging{
							LogFileName:          "logs/auditAs01.%yyyy%%MM%%dd%-%k%%mm%.log",
							RotationType:         "byTime",
							RotationFileSize:     "5000",
							BeginRotationTime:    "23:59",
							RotationInterval:     "24",
							NumberOfFilesLimited: "true",
							FileCount:            "125",
						},
					},
					{
						Name: "auditAs02",
						Host: "saedev02",
						Port: "7122",
						Type: "managed",
						Machine: &Machine{
							BuildMode: "online",
							Name:      "auditHostAs02",
							Host:      "saedev02",
							Port:      "27122",
							Protocol:  "SSL",
							Type:      "UnixMachine",
						},
						ServerStart: &ServerStart{
							Arguments: []string{
								"-Djava.security.egd=file:/dev/./urandom",
								"-Dweblogic.wsee.useRequestHost=true",
								"-DAPP_ROOT=/opt/wl12c/domains/audit/applications",
								"-DAUDIT_ROOT=/opt/wl12c/domains/audit/applications/audit",
								"-DAWS_ROOT=/opt/wl12c/domains/audit/applications/auditws",
							},
						},
						Logging: &Logging{
							LogFileName:          "logs/auditAs02.%yyyy%%MM%%dd%-%k%%mm%.log",
							RotationType:         "byTime",
							RotationFileSize:     "5000",
							BeginRotationTime:    "23:59",
							RotationInterval:     "24",
							NumberOfFilesLimited: "true",
							FileCount:            "125",
						},
					},
				},
			},
		},
		Deployments: []*Deployment{
			{
				Name:      "auditApp",
				Path:      "/opt/wl12c/domains/audit/applications/audit/auditApp.ear",
				StageMode: "nostage",
				Targets:   []string{"auditCluster"},
			},
			{
				Name:      "auditservice",
				Path:      "/opt/wl12c/domains/audit/applications/auditws/auditservice.ear",
				StageMode: "nostage",
				Targets:   []string{"auditCluster"},
			},
		},
		DataSources: []*DataSource{
			{
				Name:           "CommonDataSource",
				JNDIName:       "weblogic.commonDataSource",
				Driver:         "oracle.jdbc.OracleDriver",
				TwoPhaseCommit: "None",
				Username:       "RUSAUDIT",
				Password:       "rusauditd",
				DatabaseName:   "RUSD",
				DatabaseHost:   "10.77.6.15",
				DatabasePort:   "1521",
				URL:            "jdbc:oracle:thin:@10.77.6.15:1521:RUSD",
				TestTableName:  "SQL SELECT 1 FROM DUAL",
				Properties: []*KeyValue{
					{
						Key:   "user",
						Value: "RUSAUDIT",
					},
				},
			},
			{
				Name:           "rusCommonXADatasource",
				JNDIName:       "rusCommonXADatasource",
				Driver:         "oracle.jdbc.xa.client.OracleXADataSource",
				TwoPhaseCommit: "TwoPhaseCommit",
				Username:       "RUSAUDIT",
				Password:       "rusauditd",
				DatabaseName:   "RUSD",
				DatabaseHost:   "10.77.6.15",
				DatabasePort:   "1521",
				URL:            "jdbc:oracle:thin:@10.77.6.15:1521:RUSD",
				TestTableName:  "SQL SELECT 1 FROM DUAL",
				Properties: []*KeyValue{
					{
						Key:   "user",
						Value: "RUSAUDIT",
					},
				},
			},
		},
		SecurityRealms: []*SecurityRealm{
			{
				Name: "myrealm",
				Provider: &SecurityRealmProvider{
					Authentications: []*ProviderAuthentication{
						{
							Mode:        "edit",
							Name:        "DefaultAuthenticator",
							ControlFlag: "SUFFICIENT",
						},
						{
							Name:        "IPlanetAuthenticator",
							Type:        "weblogic.security.providers.authentication.IPlanetAuthenticator",
							ControlFlag: "SUFFICIENT",
							Host:        "10.77.30.50",
							Port:        "3899",
							Principal:   "cn=Directory Manager",
							Password:    "rusadmin",
							UserBaseDN:  "ou=people,dc=mto,dc=gov,dc=on,dc=ca",
							GroupBaseDN: "ou=groups,dc=mto,dc=gov,dc=on,dc=ca",
						},
					},
					Authorizations: []*ProviderAuthorization{
						{
							Name: "DefaultAuthorizer",
							Type: "weblogic.security.providers.authorization.DefaultAuthorizer",
						},
					},
					RoleMappings: []*ProviderRoleMapping{
						{
							Name: "DefaultRoleMapper",
							Type: "weblogic.security.providers.authorization.DefaultRoleMapper",
						},
					},
					Auditings: []*ProviderAuditing{
						{
							Name: "DefaultAuditor",
							Type: "weblogic.security.providers.audit.DefaultAuditor",
						},
					},
					Keystores: []*ProviderKeyStore{
						{
							Name: "DefaultKeyStore",
							Type: "weblogic.security.providers.pk.DefaultKeyStore",
						},
					},
				},
			},
		},
		Messaging: &Messaging{
			JMSModules: []*MessagingJMSModule{
				{
					Name: "auditSystemModule",
					SubDeployments: []*MessagingJMSModuleSubDeployment{
						{
							Name: "auditGroup",
							Targets: []*MBeanTarget{
								{
									Name: "auditAs01JMSServer",
									Type: "JMSServers",
								},
								{
									Name: "auditAs02JMSServer",
									Type: "JMSServers",
								},
							},
						},
					},
					Targets: []*MBeanTarget{
						{
							Name: "auditCluster",
							Type: "Clusters",
						},
					},
					UniformDistributedQueues: []*UniformDistributedQueue{
						{
							Name:              "auditLogQueue",
							JNDIName:          "weblogic.jms.auditLogQueue",
							SubDeploymentName: "auditGroup",
						},
						{
							Name:              "emailQueue",
							JNDIName:          "common.jms.emailQueue",
							SubDeploymentName: "auditGroup",
						},
						{
							Name:              "errorLogQueue",
							JNDIName:          "weblogic.jms.errorLogQueue",
							SubDeploymentName: "auditGroup",
						},
						{
							Name:              "eventLogQueue",
							JNDIName:          "weblogic.jms.eventLogQueue",
							SubDeploymentName: "auditGroup",
						},
					},
					ConnectionFactories: []*ConnectionFactory{
						{
							Name:                 "emailConnectionFactory",
							JNDIName:             "common.jms.emailConnectionFactory",
							DefaultTargetEnabled: "true",
						},
						{
							Name:                 "logConnectionFactory",
							JNDIName:             "weblogic.jms.logConnectionFactory",
							DefaultTargetEnabled: "true",
						},
					},
				},
			},
			JMSServers: []*MessagingJMSServer{
				{
					Name: "auditAs01JMSServer",
					PersistentStore: &MBeanTarget{
						Name: "auditAs01FileStore",
						Type: "FileStores",
					},
					Target: &MBeanTarget{
						Name: "auditAs01",
						Type: "Servers",
					},
				},
				{
					Name: "auditAs02JMSServer",
					PersistentStore: &MBeanTarget{
						Name: "auditAs02FileStore",
						Type: "FileStores",
					},
					Target: &MBeanTarget{
						Name: "auditAs02",
						Type: "Servers",
					},
				},
			},
		},
		PersistentStores: []*PersistentStore{
			{
				Name:      "auditAs01FileStore",
				Directory: "/tmp",
				Target: &MBeanTarget{
					Name: "auditAs01",
					Type: "Servers",
				},
			},
			{
				Name:      "auditAs02FileStore",
				Directory: "/tmp",
				Target: &MBeanTarget{
					Name: "auditAs02",
					Type: "Servers",
				},
			},
		},
	}
	data, err := json.MarshalIndent(root, "", "   ")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%s\n", data)
}
