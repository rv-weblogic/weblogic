// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
	"phamhi/ret"
)

// Processes the server component and its parts - managed and admin type - and
// configures its internal behaviour such as serverstart arguments and logging
// format
func (server *Server) Process(e *expect.GExpect, root *Root) error {
	if server.Ignore {
		return nil
	}
	switch server.Type {
	case "managed":
		if err := server.Create(e, root); err != nil {
			return err
		}
		if server.Machine != nil {
			if err := server.Machine.Process(e, root, server); err != nil {
				server.Machine.ReturnStatus = ret.Failed
				return err
			}
			server.Machine.ReturnStatus = ret.Ok
		}
	case "admin":
		// since WLS is admin, skip creating server and machine
		server.Machine.ReturnStatus = ret.Ok
	default:
		return fmt.Errorf("[Server](error) unrecognized server type %q", server.Type)
	}
	if server.ServerStart != nil {
		if err := server.ServerStart.Process(e, root, server); err != nil {
			server.ServerStart.ReturnStatus = ret.Failed
			return err
		}
	}
	if server.Logging != nil {
		if err := server.Logging.Process(e, root, server); err != nil {
			server.Logging.ReturnStatus = ret.Failed
			return err
		}
		server.Logging.ReturnStatus = ret.Ok
	}
	return nil
}

// Creates WLS managed server
func (server *Server) Create(e *expect.GExpect, root *Root) error {
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
				fmt.Sprintf(`cmo.createServer('%s')`, server.Name),
			},
			Expecteds: []string{
				fmt.Sprintf(`\[MBeanServerInvocationHandler\]com.bea:Name=%s,Type=Server`, server.Name),
				`weblogic.descriptor.BeanAlreadyExistsException: Bean already exists`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
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
				fmt.Sprintf(`cmo.setCluster(getMBean('/Clusters/%s'))`, root.Domain.Cluster.Name),
				fmt.Sprintf(`ls('/Clusters/%s/Servers')`, root.Domain.Cluster.Name),
			},
			Expecteds: []string{
				fmt.Sprintf("drw-   %s", server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setListenAddress('%s')`, server.Host),
				`cmo.getListenAddress()`,
			},
			Expecteds: []string{
				fmt.Sprintf("'%s'", server.Host),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setListenPort(%s)`, server.Port),
				`cmo.getListenPort()`,
			},
			Expecteds: []string{
				fmt.Sprintf("%s", server.Port),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Create", e); err != nil {
			return err
		}
	}
	return nil
}
