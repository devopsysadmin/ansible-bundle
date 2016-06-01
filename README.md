# ansible-bundle

Small tool for automatic download roles and libs a-la-Gemfile

# Author
David Pedersen (david.3pwood AT gmail DOT com)

# License
GNU Public License v2 (GPLv2)

# Preamble

As many roles have changed their configurations among time, anyone would use a
specific version of a role (for instance, a commit, or a branch, or a tag).
Moreover, a complex playbook could need different versions from the same role. This app will download roles and modules (bundles, from now on) from their repositories before launching a playbook.

# Prerequisites

- Ansible >= 2.0

# Execution

The most basic usage is running `ansible-bundle` with no parameters. This will download bundles found on `site.yml` and its include files.

# Parameters

- `-c | --clean` Will clean roles and library directories before download

- `-f | --file` Use another file instead of `site.yml`

- `-v` Sets verbose mode

- `--args` Arguments bypassed to `ansible-playbook`. Must be put under marks.

- `--run` Run `ansible-playbook` after finishing

- `--dry` will perform a 

# Configuration

By now, ansible-bundle expects to find a `bundle.cfg` file within the current 
path, with this configuration:

- `SCM_PREFIX` (mandatory): URL where the roles (or libraries) are located. For example,
if role `apache` is in `github.com/foo/roles/apache`, the `SCM_PREFIX` should be set
to `github.com/foo/roles`.

- `SCM_ROLES` | `SCM_MODULES` (optional): if roles are on a directory different than modules,
these parameters will set both, preffixing `SCM_PREFIX` . Following the previous
example, `SCM_PREFIX` should be github.com/foo, `SCM_ROLES` will be `roles` and
`SCM_MODULES` will be `/modules`

## bundle.cfg example

>       SCM_PREFIX='git@github.com:devopsysadmin'
>       SCM_ROLES='/ansible-roles'
>       SCM_MODULES='/ansible-modules'

# Unversioned bundles

This program will download from a GIT repository a branch (or tag). If no branch is set, will try to download master. But, in order to have an unversioned bundle living peacefully with a versioned bundle, those unversioned must be downloaded within their own directory. So, if you have (or need) unversioned bundles, add or modify this line to `ansible.cfg`, into `defaults` section:

- Before:

        [defaults]
        ...
        roles_path    = ./roles
        ...

- After:
  
        [defaults]
        ...
        roles_path    = ./roles:./roles/unversioned
        ...
