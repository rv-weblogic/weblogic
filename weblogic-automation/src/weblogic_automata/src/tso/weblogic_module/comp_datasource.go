// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
	"phamhi/ret"
)

// Processes the datsource component by creating the datasource and configuring
// its properties
func (ds *DataSource) Process(e *expect.GExpect, root *Root) error {
	if ds.Ignore {
		return nil
	}
	if err := ds.Create(e, root); err != nil {
		return err
	}
	for _, property := range ds.Properties {
		if property.Ignore {
			continue
		}
		if err := property.Create(e, root, ds); err != nil {
			property.ReturnStatus = ret.Failed
			return err
		}
		property.ReturnStatus = ret.Ok
	}
	return nil
}

// Creates the JDBC datasource
func (ds *DataSource) Create(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Inputs: []string{
				`cd("/")`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.createJDBCSystemResource('%s')`, ds.Name),
			},
			Expecteds: []string{
				`\[MBeanServerInvocationHandler\]com.bea:Name=\S+,Type=JDBCSystemResource`,
				`Bean already exists`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s')`, ds.Name),
			},
			Expecteds: []string{
				`wls:/\S+/edit/JDBCSystemResources/\S+/JDBCResource/\S+ !>`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setName('%s')`, ds.Name),
				fmt.Sprintf(`cmo.getName()`),
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, ds.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s/JDBCDataSourceParams/%[1]s')`, ds.Name),
				fmt.Sprintf(`set('JNDINames',jarray.array([String('%s')], String))`, ds.JNDIName),
				`cmo.getJNDINames()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`array\(java.lang.String,\['%s'\]\)`, ds.JNDIName),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setGlobalTransactionsProtocol('%s')`, ds.TwoPhaseCommit),
				fmt.Sprintf(`cmo.getGlobalTransactionsProtocol()`),
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, ds.TwoPhaseCommit),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s/JDBCDriverParams/%[1]s')`, ds.Name),
				fmt.Sprintf(`cmo.setUrl('%s')`, ds.URL),
				fmt.Sprintf(`cmo.getUrl()`),
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, ds.URL),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s/JDBCDriverParams/%[1]s')`, ds.Name),
				fmt.Sprintf(`cmo.setDriverName('%s')`, ds.Driver),
				fmt.Sprintf(`cmo.getDriverName()`),
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, ds.Driver),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s/JDBCDriverParams/%[1]s')`, ds.Name),
				fmt.Sprintf(`set('Password', '%s')`, ds.Password),
			},
			Expecteds: []string{
				``,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s/JDBCConnectionPoolParams/%[1]s')`, ds.Name),
				fmt.Sprintf(`cmo.setTestTableName('%s')`, ds.TestTableName),
				fmt.Sprintf(`cmo.getTestTableName()`),
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, ds.TestTableName),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/SystemResources/%s')`, ds.Name),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.addTarget(getMBean('/Clusters/%s'))`, root.Domain.Cluster.Name),
				fmt.Sprintf(`cmo.getTargets()`),
			},
			Expecteds: []string{
				`array\(weblogic.management.configuration.TargetMBean,\[\[MBeanServerInvocationHandler\]com.bea:Name=\S+,Type=Cluster\]\)`,
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "DataSource-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Configure the datasource's properties that passed to the JDBC driver
func (kv *KeyValue) Create(e *expect.GExpect, root *Root, ds *DataSource) error {
	tasks := []*Task{
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s/JDBCDriverParams/%[1]s/Properties/%[1]s')`, ds.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Properties/%s !>`, ds.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.createProperty('%s')`, kv.Key),
			},
			Expecteds: []string{
				`com.bea:Name=user,Type=weblogic.j2ee.descriptor.wl.JDBCPropertyBean,Parent`,
				`weblogic.descriptor.BeanAlreadyExistsException: Bean already exists`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JDBCSystemResources/%s/JDBCResource/%[1]s/JDBCDriverParams/%[1]s/Properties/%[1]s/Properties/%s')`, ds.Name, kv.Key),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Properties/%s/Properties/%s !>`, ds.Name, kv.Key),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setValue('%s')`, kv.Value),
				`cmo.getValue()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`%s`, kv.Value),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "DataSource-Property-Create", e); err != nil {
			return err
		}
	}
	return nil
}
