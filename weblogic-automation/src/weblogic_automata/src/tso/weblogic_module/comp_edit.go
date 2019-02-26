// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"phamhi/expect"
)

// Public wrapper method for the start method
func (edit *Edit) Start(e *expect.GExpect, root *Root) error {
	if err := edit.start(e, root); err != nil {
		return err
	}
	return nil
}

// Public wrapper method for the save and activate methods
func (edit *Edit) Stop(e *expect.GExpect, root *Root) error {
	if edit.SaveChanges {
		if err := edit.save(e, root); err != nil {
			return err
		}
	}
	if edit.ActivateChanges {
		if err := edit.activate(e, root); err != nil {
			return err
		}
	}
	return nil
}

// Starts the editing mode
func (r *Edit) start(e *expect.GExpect, root *Root) error {
	task := &Task{
		Requireds: []string{``},
		Inputs: []string{
			`edit()`,
			`startEdit()`,
		},
		Expecteds: []string{
			`Starting an edit session`,
		},
		Timeout: root.Internal.Timeout,
	}

	if err := RunTask(task, "Edit-Start", e); err != nil {
		return err
	}
	return nil
}

// Saves all of the pending changes
func (r *Edit) save(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit !>`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				`save()`,
			},
			Expecteds: []string{
				`Saving all your changes`,
			},
			Timeout: root.Internal.TimeoutLong,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Edit-Save", e); err != nil {
			return err
		}
	}
	return nil
}

// Activates the changes
func (r *Edit) activate(e *expect.GExpect, root *Root) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit !>`,
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				`activate()`,
			},
			Expecteds: []string{
				`Activation completed`,
			},
			Timeout: root.Internal.TimeoutLong,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Edit-Activate", e); err != nil {
			return err
		}
	}
	return nil
}

// Stops the editing mode
//func (r *Edit) stop(e *expect.GExpect) error {
//	tasks := []*Task{
//		{
//			Inputs: []string{
//				`stopEdit('y')`,
//			},
//			Expecteds: []string{
//				`Edit session has been stopped successfully`,
//				`Cannot call stopEdit without an edit session in progress`,
//				`Cannot call Edit functions when you are not in the Edit tree`,
//			},
//			Timeout: 5,
//		},
//	}

//	for _, task := range tasks {
//		if err := RunTask(task, "Edit-Stop", e); err != nil {
//			return err
//		}
//	}
//	return nil
//}
