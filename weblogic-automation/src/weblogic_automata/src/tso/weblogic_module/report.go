// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"
	"reflect"
	"strconv"
	"strings"
)

// Public wrapper of the display function
func Report(root *Root) {
	display("Root", reflect.ValueOf(root))
}

// Uses reflection to display the ReturnStatus variable of all components if exists
func display(path string, v reflect.Value) {
	switch v.Kind() {
	case reflect.Invalid:
		fmt.Printf("%s: <invalid>\n", path)
	case reflect.Slice, reflect.Array:
		for i := 0; i < v.Len(); i++ {
			display(fmt.Sprintf("%s[%d]", path, i), v.Index(i))
		}
	case reflect.Struct:
		for i := 0; i < v.NumField(); i++ {
			field := v.Type().Field(i).Name
			fieldPath := fmt.Sprintf("%s.%s", path, field)
			display(fieldPath, v.Field(i))
		}
		//	case reflect.Map:
		//		for _, key := range v.MapKeys() {
		//			display(fmt.Sprintf("%s[%s]", path,
		//				formatAtom(key)), v.MapIndex(key))
		//		}
	case reflect.Ptr:
		if v.IsNil() {
			//	fmt.Printf("%s: nil\n", path)
		} else {
			display(fmt.Sprintf("%s", path), v.Elem())
		}
		//	case reflect.Interface:
		//		if v.IsNil() {
		//			fmt.Printf("%s = nil\n", path)
		//		} else {
		//			fmt.Printf("%s.type = %s\n", path, v.Elem().Type())
		//			display(path+".value", v.Elem())
		//		}
	default: // basic types, channels, funcs
		if strings.HasSuffix(path, "ReturnStatus") {
			str := formatAtom(v)
			if str == "" {
				str = "<-->"
			} else {
				str = "<" + str + ">"
			}
			fmt.Printf("%6s %s\n", str, path)
		}

	}
}

// Helper function to discover the variable type and converts to string
func formatAtom(v reflect.Value) string {
	switch v.Kind() {
	case reflect.Invalid:
		return "invalid"
	case reflect.Int, reflect.Int8, reflect.Int16,
		reflect.Int32, reflect.Int64:
		return strconv.FormatInt(v.Int(), 10)
	case reflect.Uint, reflect.Uint8, reflect.Uint16,
		reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return strconv.FormatUint(v.Uint(), 10)
	case reflect.Bool:
		if v.Bool() {
			return "true"
		}
		return "false"
	case reflect.String:
		return v.String() //strconv.Quote(v.String())
	case reflect.Chan, reflect.Func, reflect.Ptr,
		reflect.Slice, reflect.Map:
		return v.Type().String() + " 0x" +
			strconv.FormatUint(uint64(v.Pointer()), 16)
	default: // reflect.Array, reflect.Struct, reflect.Interface
		return v.Type().String() + " value"
	}
}
