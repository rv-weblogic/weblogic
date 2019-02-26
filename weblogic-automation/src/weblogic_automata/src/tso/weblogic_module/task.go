// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"bytes"
	"fmt"
	"log"
	//	"reflect"
	"regexp"
	//	"runtime"
	"time"

	"phamhi/expect"
	"phamhi/ret"
)

// Structure of a generic task
// Requireds expects certain strings before continuing
// Inputs will be entered into the stdin
// Expecteds expects certain strings in stdout before continuing
// Timeout in seconds before giving up
type Task struct {
	Requireds []string
	Inputs    []string
	Expecteds []string
	Timeout   int
}

//func FunctionName(i interface{}) string {
//	return runtime.FuncForPC(reflect.ValueOf(i).Pointer()).Name()
//}

// Uses re to compare the output to the expected value
func Compare(items []string, timeout time.Duration, alias string, e *expect.GExpect) error {
	var buf bytes.Buffer

	for _, item := range items {
		if buf.Len() != 0 {
			buf.WriteString("|")
		}
		buf.WriteString(item)
	}

	expectedRe, err := regexp.Compile(buf.String())
	if err != nil {
		return err
	}

	log.Printf("[%s](info) expected: %q", alias, buf.String())
	out, matched, err := e.Expect(expectedRe, timeout)

	if err != nil {
		log.Printf("[%s](error) out: %q", alias, out)
		log.Printf("[%s](error) matched: %q", alias, matched)
		return err
	}
	log.Printf("[%s](success) out: %q", alias, out)
	log.Printf("[%s](success) matched: %q", alias, matched)
	buf.Reset()
	return nil
}

// Goes through each item of the task and calls expect to process the value
func RunTask(t *Task, alias string, e *expect.GExpect) error {
	if t.Timeout <= 0 {
		t.Timeout = 1
	}

	log.Printf("--------------------------------------------------")
	timeout := time.Duration(t.Timeout) * time.Second

	if err := Compare(t.Requireds, timeout, alias, e); err != nil {
		return fmt.Errorf("[%s](error) required: %s", alias, err)
	}

	for _, line := range t.Inputs {
		//		flush := "sys.stdout.flush()"
		//		log.Printf("[%s](info) send: %q", alias, flush)
		//		if err := e.Send(flush + "\n"); err != nil {
		//			log.Printf("[%s](info) send: %q", alias, err)
		//			continue
		//		}

		log.Printf("[%s](info) send: %q", alias, line)
		if err := e.Send(line + "\n"); err != nil {
			log.Printf("[%s](info) send: %q", alias, err)
			continue
		}
	}

	if err := Compare(t.Expecteds, timeout, alias, e); err != nil {
		return fmt.Errorf("[%s](error) %s", alias, err)
	}
	return nil
}

// Ensures that important values are defined properly before continuing
func PreReq(root *Root) error {
	if root.WLST == nil {
		root.WLST = &WLST{ReturnStatus: ret.Failed}
		return fmt.Errorf("[WLST] missing wlst information")
	}

	if root.Credential == nil {
		root.Credential = &Credential{ReturnStatus: ret.Failed}
		return fmt.Errorf("[Credential] missing credential information")
	}

	if root.Domain == nil {
		root.Domain = &Domain{ReturnStatus: ret.Failed}
		return fmt.Errorf("[Domain] missing domain information")
	}

	if root.Domain.AdminServer == nil {
		root.Domain = &Domain{ReturnStatus: ret.Failed}
		return fmt.Errorf("[Domain-AdminServer] missing domain admin server information")
	}

	if root.Edit == nil {
		root.Edit = &Edit{ReturnStatus: ret.Failed}
		return fmt.Errorf("[Edit] missing edit information")
	}
	return nil
}

// Builds the domain from scratch (offline mode)
func Build(root *Root) error {
	// Check pre-reqs
	if err := PreReq(root); err != nil {
		return err
	}

	// WLST
	e, err := root.WLST.Run()
	if err != nil {
		root.WLST.ReturnStatus = ret.Failed
		return err
	}
	root.WLST.ReturnStatus = ret.Ok

	// Domain
	if err := root.Domain.Build(e, root); err != nil {
		root.Domain.ReturnStatus = ret.Failed
		return err
	}
	root.Domain.ReturnStatus = ret.Ok
	return nil
}

// Once built and online, configures the domain
func Config(root *Root) error {
	// Check pre-reqs
	if err := PreReq(root); err != nil {
		return err
	}

	// WLST
	e, err := root.WLST.Run()
	if err != nil {
		root.WLST.ReturnStatus = ret.Failed
		return err
	}
	root.WLST.ReturnStatus = ret.Ok

	// Credential
	if err := root.Credential.Connect(e, root); err != nil {
		root.Credential.ReturnStatus = ret.Failed
		return err
	}
	root.Credential.ReturnStatus = ret.Ok

	// Edit-Start
	if err := root.Edit.Start(e, root); err != nil {
		root.Edit.ReturnStatus = ret.Failed
		return err
	}
	root.Edit.ReturnStatus = ret.Ok

	// Domain
	if err := root.Domain.Config(e, root); err != nil {
		root.Domain.ReturnStatus = ret.Failed
		return err
	}
	root.Domain.ReturnStatus = ret.Ok

	// Datasources
	for _, ds := range root.DataSources {
		if err := ds.Process(e, root); err != nil {
			ds.ReturnStatus = ret.Failed
			return err
		}
		ds.ReturnStatus = ret.Ok
	}

	// SecurityRealms
	for _, sr := range root.SecurityRealms {
		if err := sr.Process(e, root); err != nil {
			sr.ReturnStatus = ret.Failed
			return err
		}
		sr.ReturnStatus = ret.Ok
	}

	// PersistentStores
	for _, ps := range root.PersistentStores {
		if err := ps.Process(e, root); err != nil {
			ps.ReturnStatus = ret.Failed
			return err
		}
		ps.ReturnStatus = ret.Ok
	}

	// Messaging
	if root.Messaging != nil {
		if err := root.Messaging.Process(e, root); err != nil {
			root.Messaging.ReturnStatus = ret.Failed
			return err
		}
		root.Messaging.ReturnStatus = ret.Ok
	}

	// Edit-Stop
	if err := root.Edit.Stop(e, root); err != nil {
		root.Edit.ReturnStatus = ret.Failed
		return err
	}
	root.Edit.ReturnStatus = ret.Ok
	return nil
}

// Once configured and online, deploy the applications
func Deploy(root *Root) error {
	// Check pre-reqs
	if err := PreReq(root); err != nil {
		return err
	}

	// WLST
	e, err := root.WLST.Run()
	if err != nil {
		root.WLST.ReturnStatus = ret.Failed
		return err
	}
	root.WLST.ReturnStatus = ret.Ok

	// Credential
	if err := root.Credential.Connect(e, root); err != nil {
		root.Credential.ReturnStatus = ret.Failed
		return err
	}
	root.Credential.ReturnStatus = ret.Ok

	// Deployments
	for _, deploy := range root.Deployments {
		if err := deploy.Process(e, root); err != nil {
			deploy.ReturnStatus = ret.Failed
			return err
		}
		deploy.ReturnStatus = ret.Ok
	}
	return nil
}
