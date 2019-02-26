// Copyright 2018 Hieu Pham. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package main

import (
	"fmt"

	"phamhi/expect"
	"phamhi/ret"
)

// Processes the security realm component and its parts: authentications,
// authorizations, rolemappings, auditings, and keystores
func (sr *SecurityRealm) Process(e *expect.GExpect, root *Root) error {
	if sr.Ignore {
		return nil
	}
	//	Authentications
	for _, authentication := range sr.Provider.Authentications {
		if authentication.Ignore {
			continue
		}
		if authentication.Mode == "edit" && authentication.ControlFlag != "" {
			if err := authentication.EditControlFlag(e, root, sr.Name); err != nil {
				authentication.ReturnStatus = ret.Failed
				return err
			}
		}
		if authentication.Mode == "add" || authentication.Mode == "" {
			if err := authentication.Create(e, root, sr.Name); err != nil {
				authentication.ReturnStatus = ret.Failed
				return err
			}
			if err := authentication.EditControlFlag(e, root, sr.Name); err != nil {
				authentication.ReturnStatus = ret.Failed
				return err
			}
			if err := authentication.EditSpecific(e, root, sr.Name); err != nil {
				authentication.ReturnStatus = ret.Failed
				return err
			}
		}
		authentication.ReturnStatus = ret.Ok
	}
	//	Authorizations
	for _, authorization := range sr.Provider.Authorizations {
		if authorization.Ignore {
			continue
		}
		if authorization.Mode == "add" || authorization.Mode == "" {
			if err := authorization.Create(e, root, sr.Name); err != nil {
				authorization.ReturnStatus = ret.Failed
				return err
			}
		}
		authorization.ReturnStatus = ret.Ok
	}
	//	RoleMappings
	for _, rolemapping := range sr.Provider.RoleMappings {
		if rolemapping.Ignore {
			continue
		}
		if rolemapping.Mode == "add" || rolemapping.Mode == "" {
			if err := rolemapping.Create(e, root, sr.Name); err != nil {
				rolemapping.ReturnStatus = ret.Failed
				return err
			}
		}
		rolemapping.ReturnStatus = ret.Ok
	}
	//	Auditings
	for _, auditing := range sr.Provider.Auditings {
		if auditing.Ignore {
			continue
		}
		if auditing.Mode == "add" || auditing.Mode == "" {
			if err := auditing.Create(e, root, sr.Name); err != nil {
				auditing.ReturnStatus = ret.Failed
				return err
			}
		}
		auditing.ReturnStatus = ret.Ok
	}
	//	Keystores
	for _, keystore := range sr.Provider.Keystores {
		if keystore.Ignore {
			continue
		}
		if keystore.Mode == "add" || keystore.Mode == "" {
			if err := keystore.Create(e, root, sr.Name); err != nil {
				keystore.ReturnStatus = ret.Failed
				return err
			}
		}
		keystore.ReturnStatus = ret.Ok
	}
	return nil
}

// Configures the config flag accordingly
func (a *ProviderAuthentication) EditControlFlag(e *expect.GExpect, root *Root, srName string) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/SecurityConfiguration/%s/Realms/%s/AuthenticationProviders/%s')`, root.Domain.Name, srName, a.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`AuthenticationProviders/%s !>`, a.Name),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setControlFlag('%s')`, a.ControlFlag),
				fmt.Sprintf(`cmo.getControlFlag()`),
			},
			Expecteds: []string{
				fmt.Sprintf(`'%s'`, a.ControlFlag),
			},
			Timeout: 5,
		},
	}

	for _, task := range tasks {
		if err := RunTask(task, "SecurityRealm-Authentications-EditControlFlag", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the provider authentication
func (a *ProviderAuthentication) Create(e *expect.GExpect, root *Root, srName string) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/SecurityConfiguration/%s/Realms/%s')`, root.Domain.Name, srName),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Realms/%s !>`, srName),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.createAuthenticationProvider('%s', '%s')`, a.Name, a.Type),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				`cmo.getAuthenticationProviders()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Security:Name=%s%s`, srName, a.Name),
				fmt.Sprintf(`%s already exists `, a.Name),
			},
			Timeout: 5,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "SecurityRealm-Authentications-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Configures the provider authentication
func (a *ProviderAuthentication) EditSpecific(e *expect.GExpect, root *Root, srName string) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/SecurityConfiguration/%s/Realms/%s/AuthenticationProviders/%s')`, root.Domain.Name, srName, a.Name),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`AuthenticationProviders/%s !>`, a.Name),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setHost('%s')`, a.Host),
				`cmo.getHost()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, a.Host),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setPort(%s)`, a.Port),
				`cmo.getPort()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> %s`, a.Port),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setPrincipal('%s')`, a.Principal),
				`cmo.getPrincipal()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, a.Principal),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setGroupBaseDN('%s')`, a.GroupBaseDN),
				`cmo.getGroupBaseDN()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, a.GroupBaseDN),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.setUserBaseDN('%s')`, a.UserBaseDN),
				`cmo.getUserBaseDN()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`!> '%s'`, a.UserBaseDN),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`set("Credential", '%s')`, a.Password),
			},
			Expecteds: []string{
				` !> $`,
			},
			Timeout: 5,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "SecurityRealm-Authentications-EditSpecific", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the provider authorization
func (a *ProviderAuthorization) Create(e *expect.GExpect, root *Root, srName string) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/SecurityConfiguration/%s/Realms/%s')`, root.Domain.Name, srName),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Realms/%s !>`, srName),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.createAuthorizer('%s', '%s')`, a.Name, a.Type),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				`cmo.getAuthorizers()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Security:Name=%s%s`, srName, a.Name),
				fmt.Sprintf(`%s already exists `, a.Name),
			},
			Timeout: 5,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "SecurityRealm-Authorization-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the provider rolemapping
func (a *ProviderRoleMapping) Create(e *expect.GExpect, root *Root, srName string) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/SecurityConfiguration/%s/Realms/%s')`, root.Domain.Name, srName),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Realms/%s !>`, srName),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.createRoleMapper('%s', '%s')`, a.Name, a.Type),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				`cmo.getRoleMappers()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Security:Name=%s%s`, srName, a.Name),
				fmt.Sprintf(`%s already exists `, a.Name),
			},
			Timeout: 5,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "SecurityRealm-RoleMapping-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the provider auditing
func (a *ProviderAuditing) Create(e *expect.GExpect, root *Root, srName string) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/SecurityConfiguration/%s/Realms/%s')`, root.Domain.Name, srName),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Realms/%s !>`, srName),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cmo.createAuditor('%s', '%s')`, a.Name, a.Type),
			},
			Expecteds: []string{
				`.+`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				`cmo.getAuditors()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Security:Name=%s%s`, srName, a.Name),
				fmt.Sprintf(`%s already exists `, a.Name),
			},
			Timeout: 5,
		},
	}
	for _, task := range tasks {
		if err := RunTask(task, "SecurityRealm-Auditing-Create", e); err != nil {
			return err
		}
	}
	return nil
}

// Creates the provider keystore
func (a *ProviderKeyStore) Create(e *expect.GExpect, root *Root, srName string) error {
	tasks := []*Task{
		{
			Requireds: []string{``},
			Inputs: []string{
				`cd('/')`,
				`pwd()`,
			},
			Expecteds: []string{
				`edit:/`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`cd('/SecurityConfiguration/%s/Realms/%s')`, root.Domain.Name, srName),
				`pwd()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Realms/%s !>`, srName),
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				fmt.Sprintf(`
for item in cmo.getKeyStores():
    if '%s%s' in repr(item):
        print 'XxX-already exists'
        break
else:
    cmo.createKeyStore('%s', '%s')
    print 'XxX-successfully created'
	
`, srName, a.Name, a.Name, a.Type),
			},
			Expecteds: []string{
				`XxX`,
			},
			Timeout: 5,
		},
		{
			Requireds: []string{``},
			Inputs: []string{
				`cmo.getKeyStores()`,
			},
			Expecteds: []string{
				fmt.Sprintf(`Security:Name=%s%s`, srName, a.Name),
				fmt.Sprintf(`%s already exists `, a.Name),
			},
			Timeout: 5,
		},
	}

	for _, task := range tasks {
		if err := RunTask(task, "SecurityRealm-KeyStore-Create", e); err != nil {
			return err
		}
	}
	return nil
}
