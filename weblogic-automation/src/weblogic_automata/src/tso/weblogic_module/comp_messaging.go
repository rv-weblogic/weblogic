// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
	"phamhi/ret"
)

// Processes the JMS messaging component: JMS servers, modules and subdeployments
func (msg *Messaging) Process(e *expect.GExpect, root *Root) error {
	if msg.Ignore {
		return nil
	}
	// JMSServers
	for _, server := range msg.JMSServers {
		if server.Ignore {
			continue
		}
		if err := server.Create(e, root); err != nil {
			server.ReturnStatus = ret.Failed
			return err
		}
		server.ReturnStatus = ret.Ok
	}
	// JMSModules
	for _, mod := range msg.JMSModules {
		if mod.Ignore {
			continue
		}
		if mod.Mode == "add" || mod.Mode == "" {
			if err := mod.Create(e, root); err != nil {
				mod.ReturnStatus = ret.Failed
				return err
			}
		}
		// SubDeployments
		for _, sub := range mod.SubDeployments {
			if sub.Ignore {
				continue
			}
			if err := sub.Create(e, root, mod); err != nil {
				sub.ReturnStatus = ret.Failed
				return err
			}
			sub.ReturnStatus = ret.Ok
		}
		// Configurations
		for _, res := range mod.UniformDistributedQueues {
			if res.Ignore {
				continue
			}
			if err := res.Create(e, root, mod); err != nil {
				res.ReturnStatus = ret.Failed
				return err
			}
			res.ReturnStatus = ret.Ok
		}
		for _, res := range mod.ConnectionFactories {
			if res.Ignore {
				continue
			}
			if err := res.Create(e, root, mod); err != nil {
				res.ReturnStatus = ret.Failed
				return err
			}
			res.ReturnStatus = ret.Ok
		}
		mod.ReturnStatus = ret.Ok
	}
	return nil
}

// Creates the JMS server
func (j *MessagingJMSServer) Create(e *expect.GExpect, root *Root) error {
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
				fmt.Sprintf(`cmo.createJMSServer('%s')`, j.Name),
			},
			Expecteds: []string{
				` !>`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getJMSServers()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s,Type=JMSServer`, j.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/JMSServers/%s')`, j.Name),
			},
			Expecteds: []string{
				` !>`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`/JMSServers/%s !>`, j.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setPersistentStore(getMBean('/%s/%s'))`, j.PersistentStore.Type, j.PersistentStore.Name),
			},
			Expecteds: []string{
				` !>`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getPersistentStore()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s,Type=`, j.PersistentStore.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.addTarget(getMBean('/%s/%s'))`, j.Target.Type, j.Target.Name),
			},
			Expecteds: []string{
				` !>`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getTargets()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s,Type=`, j.Target.Name),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Messaging-JMSServer-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the JMS connection factory
func (c *ConnectionFactory) Create(e *expect.GExpect, root *Root, jms *MessagingJMSModule) error {
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
				fmt.Sprintf(`cd('/JMSSystemResources/%s/JMSResource/%[1]s')`, jms.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`JMSResource/%s !>`, jms.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.createConnectionFactory('%s')`, c.Name),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getConnectionFactories()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s`, c.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JMSSystemResources/%s/JMSResource/%[1]s/ConnectionFactories/%s')`, jms.Name, c.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`ConnectionFactories/%s !>`, c.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setJNDIName('%s')`, c.JNDIName),
				`cmo.getJNDIName()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, c.JNDIName),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`
if '%s':
	cmo.setDefaultTargetingEnabled(%[1]s)
	print 'XxXsuccessXxX'
else:
	print 'XxXskippedXxX'
`, c.DefaultTargetEnabled),
			},
			Expecteds: []string{
				`XxX\w+XxX`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`
if get('DefaultTargetingEnabled'):
    print 'XxXtrueXxX'
else:
    print 'XxXfalseXxX'
`,
			},
			Expecteds: []string{
				fmt.Sprintf(`XxX%sXxX`, c.DefaultTargetEnabled),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Messaging-JMSModule-ConnectionFactory-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the JMS uniform distribute queue
func (c *UniformDistributedQueue) Create(e *expect.GExpect, root *Root, jms *MessagingJMSModule) error {
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
				fmt.Sprintf(`cd('/JMSSystemResources/%s/JMSResource/%[1]s')`, jms.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`JMSResource/%s !>`, jms.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.createUniformDistributedQueue('%s')`, c.Name),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getUniformDistributedQueues()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s`, c.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/JMSSystemResources/%s/JMSResource/%[1]s/UniformDistributedQueues/%s')`, jms.Name, c.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`UniformDistributedQueues/%s !>`, c.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setJNDIName('%s')`, c.JNDIName),
				`cmo.getJNDIName()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, c.JNDIName),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setSubDeploymentName('%s')`, c.SubDeploymentName),
				`cmo.getSubDeploymentName()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, c.SubDeploymentName),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Messaging-JMSModule-UniformDistributedQueue-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the JMS module and adds its targets
func (mod *MessagingJMSModule) Create(e *expect.GExpect, root *Root) error {
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
				fmt.Sprintf(`cmo.createJMSSystemResource('%s')`, mod.Name),
				`cmo.getJMSSystemResources()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`com.bea:Name=%s,Type=JMSSystemResource`, mod.Name),
				`Bean already exists`,
			},
			Timeout: root.Internal.Timeout,
		},
	}

	for _, task := range tasks {
		if err := RunTask(task, "Messaging-JMSModule-Create", e); err != nil {
			// mod.ReturnStatus = ret.Failed
			return err
		}
	}

	// Add targets
	for _, target := range mod.Targets {
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
					fmt.Sprintf(`cd('/JMSSystemResources/%s')`, mod.Name),
					`pwd()`,
				},
				Expecteds: []string{
					fmt.Sprintf(`/JMSSystemResources/%s !>`, mod.Name),
				},
				Timeout: root.Internal.Timeout,
			},
			{
				Inputs: []string{
					fmt.Sprintf(`cmo.addTarget(getMBean("/%s/%s"))`, target.Type, target.Name),
				},
				Expecteds: []string{
					` !>`,
				},
				Timeout: root.Internal.Timeout,
			},
			{
				Inputs: []string{
					`cmo.getTargets()`,
				},
				Expecteds: []string{
					fmt.Sprintf(`Name=%s,Type=`, target.Name),
				},
				Timeout: root.Internal.Timeout,
			},
		}
		for _, task := range tasks {
			if err := RunTask(task, "Messaging-JMSModule-Target", e); err != nil {
				return err
			}
		}
	}
	return nil
}

// Creates the JMS module subdeployment and adds its targets
func (sub *MessagingJMSModuleSubDeployment) Create(e *expect.GExpect, root *Root, jms *MessagingJMSModule) error {
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
				fmt.Sprintf(`cd('/JMSSystemResources/%s')`, jms.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`/JMSSystemResources/%s !>`, jms.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.createSubDeployment('%s')`, sub.Name),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getSubDeployments()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s`, sub.Name),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Messaging-JMSModuleSubDeployment-Create", e); err != nil {
			return err
		}
	}

	// Add targets
	for _, target := range sub.Targets {
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
					fmt.Sprintf(`cd('/JMSSystemResources/%s/SubDeployments/%s')`, jms.Name, sub.Name),
					`pwd()`,
				},
				Expecteds: []string{
					fmt.Sprintf(`/JMSSystemResources/%s/SubDeployments/%s !>`, jms.Name, sub.Name),
				},
				Timeout: root.Internal.Timeout,
			},
			{
				Inputs: []string{
					fmt.Sprintf(`cmo.addTarget(getMBean('/%s/%s'))`, target.Type, target.Name),
				},
				Expecteds: []string{
					` !>`,
				},
				Timeout: root.Internal.Timeout,
			},
			{
				Inputs: []string{
					`cmo.getTargets()`,
				},
				Expecteds: []string{
					fmt.Sprintf(`Name=%s,Type=`, target.Name),
				},
				Timeout: root.Internal.Timeout,
			},
		}
		for _, task := range tasks {
			if err := RunTask(task, "Messaging-JMSModuleSubDeployment-Target", e); err != nil {
				return err
			}
		}
	}
	return nil
}
