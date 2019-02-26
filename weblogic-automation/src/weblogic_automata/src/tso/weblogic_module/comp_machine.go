// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
	"phamhi/ret"
)

// Processes the machine component by creating the specified machine & node manager
func (machine *Machine) Process(e *expect.GExpect, root *Root, server *Server) error {
	if machine.Ignore {
		return nil
	}
	if err := machine.Create(e, root, server); err != nil {
		return err
	}
	return nil
}

// Creates the machine & node manager
func (machine *Machine) Create(e *expect.GExpect, root *Root, server *Server) error {
	tasks := []*Task{
		{
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`
if '%s' == 'UnixMachine':
	cmo.createUnixMachine('%s')
	print 'XxXsuccessXxX'
elif '%[1]s' == 'Machine':
	cmo.createUnixMachine('%[2]s')
	print 'XxXsuccessXxX'
else:
	print 'XxXfailedXxX'
`, machine.Type, machine.Name),
			},
			Expecteds: []string{
				`XxXsuccessXxX`,
				`weblogic.descriptor.BeanAlreadyExistsException: Bean already exists`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/Machines/%s/NodeManager/%[1]s')`, machine.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'edit:/Machines/%s/NodeManager/%[1]s'`, machine.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setListenAddress('%s')`, machine.Host),
				`cmo.getListenAddress()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, machine.Host),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setListenPort(%s)`, machine.Port),
				`cmo.getListenPort()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`%s`, machine.Port),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setNMType('%s')`, machine.Protocol),
				`cmo.getNMType()`,
			},
			Expecteds: []string{
				fmt.Sprintf("'%s'", machine.Protocol),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/Servers/%s')`, server.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'edit:/Servers/%s'`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setMachine(getMBean('/Machines/%s'))`, machine.Name),
				`cmo.getMachine()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`\[MBeanServerInvocationHandler\]com.bea:Name=%s,Type=%s`, machine.Name, machine.Type),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Machine-Create", e); err != nil {
			server.ReturnStatus = ret.Failed
			return err
		}
	}
	return nil
}
