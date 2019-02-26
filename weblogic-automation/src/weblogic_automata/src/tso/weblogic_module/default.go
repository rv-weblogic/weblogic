// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

// Configures the default values of essential variables of the module
func SetDefault(root *Root) error {
	if root.Internal == nil {
		root.Internal = &Internal{Timeout: 5, TimeoutLong: 60}
	}
	return nil
}
