# ansible-bundle

Small tool for automatic download roles and libs a-la-Gemfile

# Preamble

As many roles have changed their configurations among time, anyone would use a
specific version of a role (for instance, a commit, or a branch, or a tag).
Moreover, a complex playbook could need different versions from the same role. 
This app will download roles (bundles, from now on) from their 
repositories before launching a playbook. _That means that a role should be in
its own repository_.

# Prerequisites

- Ansible. Any version.
- Git >= 1.8.5
- Python 2 >= 2.6

# Installation

## The easy way: pip

`sudo pip install ansible-bundle`

## The not-that-easy way: from code

- Download [latest release](../../archive/master.zip)
- Run `sudo python setup.py`


# Syntax

`ansible-bundle FILEYAML [ansible-playbook-options] [ansible-bundle-options]`

ansible-bundle, along the ansible-playbook parameters, has also these:

- `--bundle-clean-roles` Will clean roles and library directories before download (*)

- `--bundle-dry` Shows what will be run (as it won't download anything, 
also won't search for dependencies)

- `--bundle-deps-only` Don't run the playbook, just satisfy dependencies.

- `--bundle-disable-color` Useful for non-interactive consoles

- `--bundle-workers` concurrent connections when downloading/updating roles. Default: 1

- `--bundle-safe-update` Don't clean existing roles. (*)

(*) If both `bundle-clean-roles` and `bundle-safe-update` are set, `bundle-clean-roles` will take effect.


# Configuration

ansible-bundle expects to find a `[bundle]` section into ansible.cfg, which may 
contain some of the command lines parameters:

- workers

- verbosity

- safe

And the following extra options:

- `url`: URL where the roles are located. For example, if role `apache` is in 
`github.com/foo/roles/apache`, the `url` should be set to `github.com/foo/roles`.
Default is 'https://github.com'

## bundle.cfg example
		[bundle]
		url='git@github.com:devopsysadmin/ansible-roles'
		workers=5
		verbosity=1


# Example of use

Given the following playbook (site.yml):

		- include: site-common.yml
		  tags:
		    - common

		- hosts: all
		  roles:
		    - postgresql@1.0
		    - { role: apache, version: '2.4' }

Running `ansible-bundle site.yml` will search roles into the `site-common.yml` file and 
add to download queue, which already includes postgresql 1.0 and apache master.

Please note that each role is intended to be in its own repository, not in a folder.

# Changelog

## v 0.6

- Syntax role/version changes to role@version. This simplifies the configuration in
ansible.cfg and allows branches names such as feature/something in role version.
If a versioned role with the previous syntax is found, will complain with a
deprecation warning. The previous syntax will be obsoleted in v 0.7.


# Author

David Pedersen (david.3pwood AT gmail DOT com)

# License

GNU Public License v2 (GPLv2)
