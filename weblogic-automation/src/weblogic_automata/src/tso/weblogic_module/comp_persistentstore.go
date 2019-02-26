// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
)

// Processes the persistent store component by creating the persistent stores
func (ps *PersistentStore) Process(e *expect.GExpect, root *Root) error {
	if ps.Ignore {
		return nil
	}
	if err := ps.Create(e, root); err != nil {
		return err
	}
	return nil
}

// Creates persistent store
func (ps *PersistentStore) Create(e *expect.GExpect, root *Root) error {
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
				fmt.Sprintf(`cmo.createFileStore('%s')`, ps.Name),
			},
			Expecteds: []string{
				` !> `,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getFileStores()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s,Type=FileStore`, ps.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cd('/FileStores/%s')`, ps.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`FileStores/%s !>`, ps.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.setDirectory('%s')`, ps.Directory),
			},
			Expecteds: []string{
				` !> `,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getDirectory()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, ps.Directory),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				fmt.Sprintf(`cmo.addTarget(getMBean('/%s/%s'))`, ps.Target.Type, ps.Target.Name),
			},
			Expecteds: []string{
				` !> `,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Inputs: []string{
				`cmo.getTargets()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Name=%s,Type=`, ps.Target.Name),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "PersistentStore-Create", e); err != nil {
			return err
		}
	}
	return nil
}
