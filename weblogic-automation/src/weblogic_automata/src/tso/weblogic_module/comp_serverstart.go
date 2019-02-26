// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"
	"strings"

	"phamhi/expect"
	"phamhi/ret"
)

// Processes the serverstart behaviour of the server
func (ss *ServerStart) Process(e *expect.GExpect, root *Root, server *Server) error {
	if ss.Ignore {
		return nil
	}
	args := strings.Join(ss.Arguments, " ")
	if err := ss.SetArguments(e, root, server, args); err != nil {
		ss.ReturnStatus = ret.Failed
		return err
	}
	ss.ReturnStatus = ret.Ok
	return nil
}

// Configures the server startup arguments
func (ss *ServerStart) SetArguments(e *expect.GExpect, root *Root, server *Server, args string) error {
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
				fmt.Sprintf(`cd('/Servers/%s/ServerStart/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/ServerStart/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setArguments('%s')`, args),
				`cmo.getArguments()`,
			},
			Expecteds: []string{
				fmt.Sprintf("%s", args),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-ServerStart-SetArguments", e); err != nil {
			ss.ReturnStatus = ret.Failed
			return err
		}
	}
	return nil
}
