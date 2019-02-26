// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
)

// Process the logging component by configuring the logging behaviours of the
// specified server
func (logging *Logging) Process(e *expect.GExpect, root *Root, server *Server) error {
	if logging.Ignore {
		return nil
	}
	if logging.LogFileName != "" {
		if err := logging.SetLogFileName(e, root, server); err != nil {
			return err
		}
	}
	if logging.RotationType != "" {
		if err := logging.SetRotationType(e, root, server); err != nil {
			return err
		}
	}
	if logging.BeginRotationTime != "" {
		if err := logging.SetBeginRotationTime(e, root, server); err != nil {
			return err
		}
	}
	if logging.RotationInterval != "" {
		if err := logging.SetRotationInterval(e, root, server); err != nil {
			return err
		}
	}
	if logging.FileCount != "" {
		if err := logging.SetFileCount(e, root, server); err != nil {
			return err
		}
	}
	if logging.NumberOfFilesLimited != "" {
		if err := logging.SetNumberOfFilesLimited(e, root, server); err != nil {
			return err
		}
	}
	if logging.RotationFileSize != "" {
		if err := logging.SetRotationFileSize(e, root, server); err != nil {
			return err
		}
	}
	return nil
}

// Configures the size limit before rotation kicks in
func (logging *Logging) SetRotationFileSize(e *expect.GExpect, root *Root, server *Server) error {
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
				fmt.Sprintf(`cd('/Servers/%s/Log/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/Log/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setFileMinSize(%s)`, logging.RotationFileSize),
				`cmo.getFileMinSize()`,
			},
			Expecteds: []string{
				fmt.Sprintf(` !> %s`, logging.RotationFileSize),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Logging-SetRotationFileSize", e); err != nil {
			return err
		}
	}
	return nil
}

// Configures then number of log file limit
func (logging *Logging) SetNumberOfFilesLimited(e *expect.GExpect, root *Root, server *Server) error {
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
				fmt.Sprintf(`cd('/Servers/%s/Log/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/Log/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setNumberOfFilesLimited(%s)`, logging.NumberOfFilesLimited),
				`
if get('NumberOfFilesLimited'):
    print 'XxXtrueXxX'
else:
    print 'XxXfalseXxX'
`,
			},
			Expecteds: []string{
				fmt.Sprintf(`XxX%sXxX`, logging.NumberOfFilesLimited),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Logging-SetNumberOfFilesLimited", e); err != nil {
			return err
		}
	}
	return nil
}

// Configures the file count limit
func (logging *Logging) SetFileCount(e *expect.GExpect, root *Root, server *Server) error {
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
				fmt.Sprintf(`cd('/Servers/%s/Log/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/Log/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setFileCount(%s)`, logging.FileCount),
				`cmo.getFileCount()`,
			},
			Expecteds: []string{
				fmt.Sprintf(` !> %s`, logging.FileCount),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Logging-SetFileCount", e); err != nil {
			return err
		}
	}
	return nil
}

// Configures rotation interval (when the rotation kicks in)
func (logging *Logging) SetRotationInterval(e *expect.GExpect, root *Root, server *Server) error {
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
				fmt.Sprintf(`cd('/Servers/%s/Log/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/Log/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setFileTimeSpan(%s)`, logging.RotationInterval),
				`cmo.getFileTimeSpan()`,
			},
			Expecteds: []string{
				fmt.Sprintf(` !> %s`, logging.RotationInterval),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Logging-SetRotationInterval", e); err != nil {
			return err
		}
	}
	return nil
}

// Configures the log filename format
func (logging *Logging) SetLogFileName(e *expect.GExpect, root *Root, server *Server) error {
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
				fmt.Sprintf(`cd('/Servers/%s/Log/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/Log/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setFileName('%s')`, logging.LogFileName),
				`cmo.getFileName()`,
			},
			Expecteds: []string{
				fmt.Sprintf(` !> '%s'`, logging.LogFileName),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Logging-SetLogFileName", e); err != nil {
			return err
		}
	}
	return nil
}

// Configures when the rotation kicks in for that day
func (logging *Logging) SetBeginRotationTime(e *expect.GExpect, root *Root, server *Server) error {
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
				fmt.Sprintf(`cd('/Servers/%s/Log/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/Log/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setRotationTime('%s')`, logging.BeginRotationTime),
				`cmo.getRotationTime()`,
			},
			Expecteds: []string{
				fmt.Sprintf(` !> '%s'`, logging.BeginRotationTime),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Logging-SetBeginRotationTime", e); err != nil {
			return err
		}
	}
	return nil
}

// Configures the type of rotation to perform
func (logging *Logging) SetRotationType(e *expect.GExpect, root *Root, server *Server) error {
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
				fmt.Sprintf(`cd('/Servers/%s/Log/%[1]s')`, server.Name),
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
				fmt.Sprintf(`/Servers/%s/Log/%[1]s !>`, server.Name),
			},
			Timeout: root.Internal.Timeout,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setRotationType('%s')`, logging.RotationType),
				`cmo.getRotationType()`,
			},
			Expecteds: []string{
				fmt.Sprintf(` !> '%s'`, logging.RotationType),
			},
			Timeout: root.Internal.Timeout,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "Server-Logging-SetRotationType", e); err != nil {
			return err
		}
	}
	return nil
}
