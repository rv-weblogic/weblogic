// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
	"phamhi/ret"
)

// Processes the cluster component by creating the cluster and its assigned
// managed servers
func (cluster *Cluster) Process(e *expect.GExpect, root *Root) error {
	if err := cluster.Create(e, root); err != nil {
		return err
	}

	// Goes through the server list and calls its main handler
	for _, server := range cluster.Servers {
		if err := server.Process(e, root); err != nil {
			cluster.ReturnStatus = ret.Failed
			return err
		}
		server.ReturnStatus = ret.Ok
	}
	cluster.ReturnStatus = ret.Ok
	return nil
}

// Creates the WLS cluster
func (cluster *Cluster) Create(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`/edit`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.createCluster('%s')`, cluster.Name),
			},
			Expecteds: []string{
				fmt.Sprintf(`\[MBeanServerInvocationHandler\]com.bea:Name=%s,Type=Cluster`, cluster.Name),
				`weblogic.descriptor.BeanAlreadyExistsException: Bean already exists`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/Clusters/%s')`, cluster.Name),
			},
			Expecteds: []string{
				fmt.Sprintf(`edit/Clusters/%s !>`, cluster.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setClusterMessagingMode('%s')`, cluster.MessagingMode),
				`cmo.getClusterMessagingMode()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, cluster.MessagingMode),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Cluster-Create", e); err != nil {
			cluster.ReturnStatus = ret.Failed
			return err
		}
	}
	return nil
}
