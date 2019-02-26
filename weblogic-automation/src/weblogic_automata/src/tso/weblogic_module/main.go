// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

// Main entrance of the weblogic module application

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"
	"time"

	"phamhi/ret"
)

var usage = func() {
	fmt.Fprintf(os.Stderr, "Usage: %s [OPTIONS] [validate|build|config|deploy] <domain_template.json>\n",
		os.Args[0])
	more := `  -debug
      enable debugging
  -noreport
      do not display result
`
	// flag.PrintDefaults()
	fmt.Fprintf(os.Stderr, "%s", more)
	os.Exit(1)
}

// Parses the JSON file into the structure defined within def.go
func ParseFile(path string) (*Root, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("[Main](info) %s", err)
	}
	defer f.Close()

	var root Root
	log.Printf("[Main](info) parsing %s", path)

	if err := json.NewDecoder(f).Decode(&root); err != nil {
		return nil, fmt.Errorf("[Main](info) parse template: %s", err)
	}
	return &root, nil
}

// Enables debugging
var debug bool

// Don't display the report at the end of the run
var noreport bool

// Main entrance
func main() {
	flag.BoolVar(&debug, "debug", false, "enable debugging")
	flag.BoolVar(&noreport, "noreport", false, "disable report")

	flag.Parse()
	if len(flag.Args()) != 2 {
		usage()
	}

	if !debug {
		log.SetOutput(ioutil.Discard)
	}

	exitCode := 0

	root, err := ParseFile(flag.Arg(1))
	if err != nil {
		log.Fatal(err)
	}

	if err := SetDefault(root); err != nil {
		log.Fatal(err)
	}

	root.ReturnStatus = ret.Ok
	todo := strings.ToLower(flag.Arg(0))

	switch todo {
	case "validate":
		fmt.Printf("Template %q is valid.\n", flag.Arg(1))
		os.Exit(exitCode)
	case "build":
		if err := Build(root); err != nil {
			root.ReturnStatus = ret.Failed
			exitCode = 1
			log.SetOutput(os.Stderr)
			log.Print(err)
		}
	case "config":
		if err := Config(root); err != nil {
			root.ReturnStatus = ret.Failed
			exitCode = 1
			log.SetOutput(os.Stderr)
			log.Print(err)
		}
	case "deploy":
		if err := Deploy(root); err != nil {
			root.ReturnStatus = ret.Failed
			exitCode = 1
			log.SetOutput(os.Stderr)
			log.Print(err)
		}
	default:
		usage()
		os.Exit(exitCode)
	}
	if !noreport {
		time.Sleep(time.Millisecond * 200)
		Report(root)
	}
	os.Exit(exitCode)
}
