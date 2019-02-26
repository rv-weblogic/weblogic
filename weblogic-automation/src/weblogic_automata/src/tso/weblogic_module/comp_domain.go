// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"

	"phamhi/expect"
	"phamhi/ret"
)

// Once built, configure the WLS domain (requires to be "online")
func (domain *Domain) Config(e *expect.GExpect, root *Root) error {
	if err := domain.AdminServer.Process(e, root); err != nil {
		domain.AdminServer.ReturnStatus = ret.Failed
		return err
	}
	domain.AdminServer.ReturnStatus = ret.Ok

	if domain.Cluster != nil {
		if err := domain.Cluster.Process(e, root); err != nil {
			domain.Cluster.ReturnStatus = ret.Failed
			return err
		}
		domain.Cluster.ReturnStatus = ret.Ok
	}
	return nil
}

// Build the WLS domain from scratch in offline mode
func (domain *Domain) Build(e *expect.GExpect, root *Root) error {
	if err := domain.ReadTemplate(e, root); err != nil {
		return err
	}

	if err := domain.CreateAdminMachineNodeManager(e, root); err != nil {
		return err
	}

	if err := domain.CreateDomain(e, root); err != nil {
		return err
	}

	if domain.ProductionModeEnabled == "true" {
		if err := domain.CreateBootProperties(e, root); err != nil {
			return err
		}
	}
	return nil
}

// Reads the specified template in the beginning
func (domain *Domain) ReadTemplate(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Requireds: []string{`wls:/offline>`},
			Inputs: []string{
				fmt.Sprintf(`readTemplate('%s')`, domain.DomainTemplate),
			},
			Expecteds: []string{
				`wls:/offline/base_domain>`,
			},
			Timeout: root.Internal.TimeoutLong,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Domain-Build-ReadTemplate", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the Admin machine and node manager
func (domain *Domain) CreateAdminMachineNodeManager(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Inputs: []string{
				`cd('/NMProperties')`,
				`pwd()`,
			},
			Expecteds: []string{
				`'/base_domain/NMProperties'`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('ListenAddress', '%s')`, domain.AdminServer.Machine.Host),
				`get('ListenAddress')`,
			},
			Expecteds: []string{
				fmt.Sprintf(`NMProperties>'%s'`, domain.AdminServer.Machine.Host),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('ListenPort', %s)`, domain.AdminServer.Machine.Port),
				`get('ListenPort')`,
			},
			Expecteds: []string{
				fmt.Sprintf(`NMProperties>%s`, domain.AdminServer.Machine.Port),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				`cd('/SecurityConfiguration/base_domain')`,
				`pwd()`,
			},
			Expecteds: []string{
				`wls:/offline/base_domain/SecurityConfiguration/base_domain>`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('NodeManagerUsername', '%s')`, root.Credential.Username),
				`get('NodeManagerUsername')`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, root.Credential.Username),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('NodeManagerPasswordEncrypted', '%s')`, root.Credential.Password),
				`get('NodeManagerPasswordEncrypted')`,
			},
			Expecteds: []string{
				`array`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`'/base_domain'`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`create('%s', '%s')`,
					domain.AdminServer.Machine.Name,
					domain.AdminServer.Machine.Type),
			},
			Expecteds: []string{
				fmt.Sprintf(`Proxy for %s: Name=%[1]s, Type=Machine`, domain.AdminServer.Machine.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/Machines/%s')`, domain.AdminServer.Machine.Name),
			},
			Expecteds: []string{
				fmt.Sprintf(`offline/base_domain/Machine/%s>`, domain.AdminServer.Machine.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`create('%s', 'NodeManager')`, domain.AdminServer.Machine.Name),
			},
			Expecteds: []string{
				fmt.Sprintf(`Proxy for %s: Name=%[1]s, Type=NodeManager`, domain.AdminServer.Machine.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('NodeManager/%s')`, domain.AdminServer.Machine.Name),
			},
			Expecteds: []string{
				fmt.Sprintf(`offline/base_domain/Machine/%s/NodeManager/%[1]s>`, domain.AdminServer.Machine.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('ListenAddress', '%s')`, domain.AdminServer.Machine.Host),
				`get("ListenAddress")`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, domain.AdminServer.Machine.Host),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('ListenPort', %s)`, domain.AdminServer.Machine.Port),
				`get("ListenPort")`,
			},
			Expecteds: []string{
				fmt.Sprintf(`%s`, domain.AdminServer.Machine.Port),
			},
			Timeout: 5,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Domain-Build-CreateAdminMachineNodeManager", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the WLS domain in offline mode
func (domain *Domain) CreateDomain(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`'/base_domain'`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('Name', '%s')`, domain.Name),
				`get('Name')`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, domain.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('ProductionModeEnabled', '%s')`, domain.ProductionModeEnabled),
				`
if get('ProductionModeEnabled'):
    print 'XxXtrueXxX'
else:
    print 'XxXfalseXxX'
`,
			},
			Expecteds: []string{
				fmt.Sprintf(`XxX%sXxX`, domain.ProductionModeEnabled),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`setOption('DomainName', '%s')`, domain.Name),
				`print 'xXx'`,
			},
			Expecteds: []string{
				`xXx\nwls:/offline/base_domain>`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`setOption('JavaHome', '%s')`, domain.JavaHome),
				`print 'xXx'`,
			},
			Expecteds: []string{
				`xXx\nwls:/offline/base_domain>`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`setOption('ServerStartMode', '%s')`, domain.ServerStartMode),
				`print 'xXx'`,
			},
			Expecteds: []string{
				`xXx\nwls:/offline/base_domain>`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				`cd('/Servers/AdminServer')`,
				`pwd()`,
			},
			Expecteds: []string{
				`'/base_domain/Server/AdminServer'`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setName('%s')`, domain.AdminServer.Name),
				`cmo.getName()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, domain.AdminServer.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('ListenAddress', '%s')`, domain.AdminServer.Host),
				`get("ListenAddress")`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, domain.AdminServer.Host),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('ListenPort', %s)`, domain.AdminServer.Port),
				`get('ListenPort')`,
			},
			Expecteds: []string{
				fmt.Sprintf(`%s`, domain.AdminServer.Port),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`set('Machine', '%s')`, domain.AdminServer.Machine.Name),
				`get("Machine")`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Proxy for %s: Name=%[1]s, Type=Machine`, domain.AdminServer.Machine.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/Security/%s/User/weblogic')`, domain.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'/base_domain/Security/%s/User/weblogic'`, domain.Name),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setName('%s')`, root.Credential.Username),
				`cmo.getName()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, root.Credential.Username),
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setPassword('%s')`, root.Credential.Password),
				`cmo.getPassword()`,
			},
			Expecteds: []string{
				`''`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`'/base_domain'`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				`setOption('OverwriteDomain', 'true')`,
				`print 'xXx'`,
			},
			Expecteds: []string{
				`xXx\nwls:/offline/base_domain>`,
			},
			Timeout: 5,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`writeDomain('%s')`, domain.DomainHome),
				`print 'xXx'`,
			},
			Expecteds: []string{
				fmt.Sprintf(`wls:/offline/%s>xXx`, domain.Name),
			},
			Timeout: 60,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Domain-Build-CreateDomain", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the WLS boot.properties file required when in Production mode
func (domain *Domain) CreateBootProperties(e *expect.GExpect, root *Root) error {
	log.Printf("--------------------------------------------------")

	dir := filepath.Join(domain.DomainHome, "servers", domain.AdminServer.Name, "security")
	bootFile := filepath.Join(dir, "boot.properties")

	task := "Domain-Build-CreateBootProperties"
	log.Printf("[%s](info) creating security directory: %q", task, dir)

	if err := os.MkdirAll(dir, 0750); err != nil {
		return fmt.Errorf("[%s](error) failed to create security directory: %s", task, err)
	}

	log.Printf("[%s](info) creating boot.properties file: %q", task, bootFile)
	content := []byte(fmt.Sprintf("username=%s\npassword=%s\n", root.Credential.Username, root.Credential.Password))

	if err := ioutil.WriteFile(bootFile, content, 0640); err != nil {
		return fmt.Errorf("[%s](error) failed to create boot.roperties: %s", task, err)
	}
	return nil
}
