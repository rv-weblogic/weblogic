// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"
	"log"
	"strings"

	"phamhi/expect"
)

// Runs the wlst script within an emulated PTY
func (wlst *WLST) Run() (*expect.GExpect, error) {
	cmd := wlst.ScriptPath + " " + strings.Join(wlst.ScriptArgs, " ")
	log.Printf("[WLST](info) spawning: %s", cmd)

	e, _, err := expect.SpawnEnv(cmd, -1, wlst.EnvVars)

	if err != nil {
		return nil, fmt.Errorf("[WLST-Run](error): %s", err)
	}
	return e, nil
}
