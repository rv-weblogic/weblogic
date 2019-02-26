// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"
	"strings"

	"phamhi/expect"
)

// Processes the deployment component by deploying the specified WLS applications
func (deploy *Deployment) Process(e *expect.GExpect, root *Root) error {
	if deploy.Ignore {
		return nil
	}
	if err := deploy.Deploy(e, root); err != nil {
		return err
	}
	return nil
}

// Deploys the WLS application
func (deploy *Deployment) Deploy(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Inputs: []string{
				fmt.Sprintf(`deploy(appName='%s', path='%s', targets='%s', stageMode='%s')`,
					deploy.Name, deploy.Path, strings.Join(deploy.Targets, ","), deploy.StageMode),
			},
			Expecteds: []string{
				`Deployment State : completed`,
			},
			Timeout: root.Internal.TimeoutLong,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Deployment-Deploy", e); err != nil {
			return err
		}
	}
	return nil
}
