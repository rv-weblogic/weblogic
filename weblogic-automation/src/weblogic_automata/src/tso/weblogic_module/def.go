// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

// Main program definition of the domain template

package main

type Root struct {
	Internal         *Internal          `json:"internal,omitempty"`
	WLST             *WLST              `json:"wlst"`
	Credential       *Credential        `json:"credential"`
	Edit             *Edit              `json:"edit"`
	Domain           *Domain            `json:"domain"`
	Deployments      []*Deployment      `json:"deployments"`
	DataSources      []*DataSource      `json:"data_sources"`
	SecurityRealms   []*SecurityRealm   `json:"security_realms"`
	PersistentStores []*PersistentStore `json:"persistent_stores"`
	Messaging        *Messaging         `json:"messaging"`
	ReturnStatus     string             `json:"return_status,omitempty"`
}

type Internal struct {
	Timeout     int `json:"timeout,omitempty"`
	TimeoutLong int `json:"timeout_long,omitempty"`
}

type WLST struct {
	EnvVars      []string `json:"env_vars"`
	ScriptPath   string   `json:"script_path"`
	ScriptArgs   []string `json:"script_args"`
	ReturnStatus string   `json:"return_status,omitempty"`
}

type Credential struct {
	Username     string `json:"username"`
	Password     string `json:"password"`
	Protocol     string `json:"protocol"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type Edit struct {
	SaveChanges     bool   `json:"save_changes"`
	ActivateChanges bool   `json:"activate_changes"`
	ReturnStatus    string `json:"return_status,omitempty"`
}

type Domain struct {
	Ignore                bool     `json:"ignore,omitempty"`
	Name                  string   `json:"name"`
	DomainTemplate        string   `json:"domain_template"`
	DomainHome            string   `json:"domain_home"`
	JavaHome              string   `json:"java_home"`
	ProductionModeEnabled string   `json:"production_mode_enabled"`
	ServerStartMode       string   `json:"server_start_mode"`
	AdminServer           *Server  `json:"admin_server"`
	Cluster               *Cluster `json:"cluster"`
	ReturnStatus          string   `json:"return_status,omitempty"`
}

type Cluster struct {
	Ignore        bool      `json:"ignore,omitempty"`
	Name          string    `json:"name"`
	MessagingMode string    `json:"messaging_mode"`
	Servers       []*Server `json:"servers"`
	ReturnStatus  string    `json:"return_status,omitempty"`
}

type Server struct {
	Ignore       bool         `json:"ignore,omitempty"`
	Name         string       `json:"name"`
	Host         string       `json:"host"`
	Port         string       `json:"port"`
	Type         string       `json:"type"`
	Machine      *Machine     `json:"machine"`
	ServerStart  *ServerStart `json:"server_start"`
	Logging      *Logging     `json:"logging"`
	ReturnStatus string       `json:"return_status,omitempty"`
}

type Machine struct {
	Ignore       bool   `json:"ignore,omitempty"`
	BuildMode    string `json:"build_mode"`
	Name         string `json:"name"`
	Host         string `json:"host"`
	Port         string `json:"port"`
	Protocol     string `json:"protocol"`
	Type         string `json:"type"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type ServerStart struct {
	Ignore       bool     `json:"ignore,omitempty"`
	Arguments    []string `json:"arguments"`
	ReturnStatus string   `json:"return_status,omitempty"`
}

type Logging struct {
	Ignore               bool   `json:"ignore,omitempty"`
	LogFileName          string `json:"log_file_name"`
	RotationType         string `json:"rotation_type"`
	RotationFileSize     string `json:"rotation_file_size"`
	BeginRotationTime    string `json:"begin_rotation_time"`
	RotationInterval     string `json:"rotation_interval"`
	NumberOfFilesLimited string `json:"number_of_files_limited"`
	FileCount            string `json:"file_count"`
	ReturnStatus         string `json:"return_status,omitempty"`
}

type Deployment struct {
	Ignore       bool     `json:"ignore,omitempty"`
	Name         string   `json:"name"`
	Path         string   `json:"path"`
	StageMode    string   `json:"stage_mode"`
	Targets      []string `json:"targets"`
	ReturnStatus string   `json:"return_status,omitempty"`
}

type DataSource struct {
	Ignore         bool        `json:"ignore,omitempty"`
	Name           string      `json:"jdbc_name"`
	JNDIName       string      `json:"jndi_name"`
	Driver         string      `json:"driver"`
	TwoPhaseCommit string      `json:"two_phase_commit"`
	Username       string      `json:"username"`
	Password       string      `json:"password"`
	DatabaseName   string      `json:"database_name"`
	DatabaseHost   string      `json:"database_host"`
	DatabasePort   string      `json:"database_port"`
	URL            string      `json:"url"`
	TestTableName  string      `json:"test_table_name"`
	Properties     []*KeyValue `json:"properties"`
	ReturnStatus   string      `json:"return_status,omitempty"`
}

type KeyValue struct {
	Ignore       bool   `json:"ignore,omitempty"`
	Key          string `json:"key"`
	Value        string `json:"value"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type SecurityRealm struct {
	Ignore       bool                   `json:"ignore,omitempty"`
	Name         string                 `json:"name"`
	Provider     *SecurityRealmProvider `json:"provider"`
	ReturnStatus string                 `json:"return_status,omitempty"`
}

type SecurityRealmProvider struct {
	Ignore          bool                      `json:"ignore,omitempty"`
	Authentications []*ProviderAuthentication `json:"authentications"`
	Authorizations  []*ProviderAuthorization  `json:"authorizations"`
	RoleMappings    []*ProviderRoleMapping    `json:"role_mappings"`
	Auditings       []*ProviderAuditing       `json:"auditings"`
	Keystores       []*ProviderKeyStore       `json:"keystores"`
}

type ProviderAuthentication struct {
	Ignore       bool   `json:"ignore,omitempty"`
	Mode         string `json:"mode,omitempty"`
	Name         string `json:"name"`
	Type         string `json:"type,omitempty"`
	ControlFlag  string `json:"control_flag"`
	Host         string `json:"host,omitempty"`
	Port         string `json:"port,omitempty"`
	Principal    string `json:"principal,omitempty"`
	Password     string `json:"password,omitempty"`
	UserBaseDN   string `json:"user_base_dn,omitempty"`
	GroupBaseDN  string `json:"group_base_dn,omitempty"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type ProviderAuthorization struct {
	Ignore       bool   `json:"ignore,omitempty"`
	Mode         string `json:"mode,omitempty"`
	Name         string `json:"name"`
	Type         string `json:"type"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type ProviderRoleMapping struct {
	Ignore       bool   `json:"ignore,omitempty"`
	Mode         string `json:"mode,omitempty"`
	Name         string `json:"name"`
	Type         string `json:"type"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type ProviderAuditing struct {
	Ignore       bool   `json:"ignore,omitempty"`
	Mode         string `json:"mode,omitempty"`
	Name         string `json:"name"`
	Type         string `json:"type"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type ProviderKeyStore struct {
	Ignore       bool   `json:"ignore,omitempty"`
	Mode         string `json:"mode,omitempty"`
	Name         string `json:"name"`
	Type         string `json:"type"`
	ReturnStatus string `json:"return_status,omitempty"`
}

type Messaging struct {
	Ignore       bool                  `json:"ignore,omitempty"`
	JMSServers   []*MessagingJMSServer `json:"jms_servers"`
	JMSModules   []*MessagingJMSModule `json:"jms_modules"`
	ReturnStatus string                `json:"return_status,omitempty"`
}

type MessagingJMSModule struct {
	Ignore                   bool                               `json:"ignore,omitempty"`
	Mode                     string                             `json:"mode,omitempty"`
	Name                     string                             `json:"name"`
	SubDeployments           []*MessagingJMSModuleSubDeployment `json:"sub_deployments"`
	Targets                  []*MBeanTarget                     `json:"targets"`
	UniformDistributedQueues []*UniformDistributedQueue         `json:"uniform_distribute_queues,omitempty"`
	ConnectionFactories      []*ConnectionFactory               `json:"connection_factories,omitempty"`
	ReturnStatus             string                             `json:"return_status,omitempty"`
}

type MessagingJMSModuleSubDeployment struct {
	Ignore       bool           `json:"ignore,omitempty"`
	Name         string         `json:"name"`
	Targets      []*MBeanTarget `json:"targets"`
	ReturnStatus string         `json:"return_status,omitempty"`
}

type MBeanTarget struct {
	Name string `json:"name"`
	Type string `json:"type"`
}

type UniformDistributedQueue struct {
	Ignore            bool   `json:"ignore,omitempty"`
	Name              string `json:"name"`
	JNDIName          string `json:"jndi_name"`
	SubDeploymentName string `json:"sub_deployment_name"`
	ReturnStatus      string `json:"return_status,omitempty"`
}

type ConnectionFactory struct {
	Ignore               bool   `json:"ignore,omitempty"`
	Name                 string `json:"name"`
	JNDIName             string `json:"jndi_name"`
	DefaultTargetEnabled string `json:"default_target_enabled"`
	ReturnStatus         string `json:"return_status,omitempty"`
}

type PersistentStore struct {
	Ignore       bool         `json:"ignore,omitempty"`
	Name         string       `json:"name"`
	Directory    string       `json:"directory"`
	Target       *MBeanTarget `json:"target"`
	ReturnStatus string       `json:"return_status,omitempty"`
}

type MessagingJMSServer struct {
	Ignore          bool         `json:"ignore,omitempty"`
	Name            string       `json:"name"`
	PersistentStore *MBeanTarget `json:"persistent_store"`
	Target          *MBeanTarget `json:"target"`
	ReturnStatus    string       `json:"return_status,omitempty"`
}
