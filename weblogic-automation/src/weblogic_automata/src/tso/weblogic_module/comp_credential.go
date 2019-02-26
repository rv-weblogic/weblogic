// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
)

// Connects to the online console via WLST
func (cred *Credential) Connect(e *expect.GExpect, root *Root) error {
	urlStr := fmt.Sprintf("%s://%s:%s", cred.Protocol, root.Domain.AdminServer.Host, root.Domain.AdminServer.Port)
	connectStr := fmt.Sprintf("connect('%s', '%s', '%s')", cred.Username, cred.Password, urlStr)

	task := &Task{
		Requireds: []string{
			`wls:/offline>`,
		},
		Inputs: []string{
			connectStr,
		},
		Expecteds: []string{
			`Successfully connected`,
		},
		Timeout: root.Internal.TimeoutLong,
	}
	if err := RunTask(task, "Credential-Connect", e); err != nil {
		return err
	}
	return nil
}
