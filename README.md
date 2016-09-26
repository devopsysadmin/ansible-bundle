# ansible-bundle

Small tool for automatic download roles and libs a-la-Gemfile

# Preamble

As many roles have changed their configurations among time, anyone would use a
specific version of a role (for instance, a commit, or a branch, or a tag).
Moreover, a complex playbook could need different versions from the same role. 
This app will download roles and modules (bundles, from now on) from their 
repositories before launching a playbook.

# Prerequisites

- Ansible. Any version.
- Git > 1.6 (possibly will work on earlier releases, but hasn't been tested)
- Python 2 > 2.6

# Installation

## The easy way: pip

`sudo pip install ansible-bundle`

## The not-that-easy way: from code

- Download [latest release](../../archive/master.zip)
- Run `sudo python setup.py`


# Syntax

`ansible-bundle FILEYAML [ansible-playbook-options] [ansible-bundle-options]`

ansible-bundle, along the ansible-playbook parameters, has also these:

- `--bundle-clean-roles` Will clean roles and library directories before download

- `--bundle-dry` Shows what will be run (as it won't download anything, 
also won't search for dependencies)

- `--bundle-deps-only` Don't run the playbook, just satisfies dependencies.


# Configuration

ansible-bundle expects to find a `[bundle]` section into ansible.cfg 
file with this configuration:

- `SCM_PREFIX` (mandatory): URL where the roles (or libraries) are located. For 
example, if role `apache` is in `github.com/foo/roles/apache`, the `SCM_PREFIX` 
should be set to `github.com/foo/roles`.

- `SCM_ROLES` | `SCM_MODULES` (optional): if roles are on a directory different 
than modules, these parameters will set both, preffixing `SCM_PREFIX` . 
Following the previous example, `SCM_PREFIX` should be github.com/foo, 
`SCM_ROLES` will be `roles` and `SCM_MODULES` will be `/modules`

## bundle.cfg example

		SCM_PREFIX='git@github.com:devopsysadmin'
		SCM_ROLES='/ansible-roles'
		SCM_MODULES='/ansible-modules'

# Unversioned bundles

This program will download from a GIT repository a branch (or tag). If no 
branch is set, will try to download master. But, in order to have an 
unversioned bundle living peacefully with a versioned bundle, those unversioned 
will be downloaded within their own directory. So, if you have (or need) 
unversioned bundles, add or modify this line to `ansible.cfg`, into `defaults` 
section:

- Before:

        [defaults]
        ...
        roles_path    = ./roles
        ...

- After:
  
        [defaults]
        ...
        roles_path    = ./roles/unversioned:./roles
        ...

# Example of use

Given the following playbook (site.yml):

		- include: site-common.yml
		  tags:
		    - common

		- hosts: all
		  roles:
		    - postgresql/1.0
		    - { role: apache, version: '2.4' }

Running `ansible-bundle site.yml` will search roles into the `site-common.yml` file and 
download them. Also, will download role postgresql 1.0 and apache master.

# Author

David Pedersen (david.3pwood AT gmail DOT com)

# License

GNU Public License v2 (GPLv2)
