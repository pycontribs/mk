# Multi-repo actions

Since June 2024, `mk` project adopted the multi-repository commands from [pre]
project. The list of repositories is loaded from `~/.config/mk/mk.yml` that has
a format like below:

```yaml title="~/.config/mk/mk.yml"
repos:
  gh_org/gh_repo1: {}
  gh_org/gh_repo2: {}
```

You can use a symlink to store this file in a different location.

This feature is enabled only when all the below requirements are met:

- [gh] command is installed
- The config file is present on on disk

<!-- markdownlint-disable MD046 -->

!!! note

    This feature is experimental and how it works might change between
    each new release, including command names and configuration file format.
    You are welcome to give your feedback about how we can make it more useful
    and flexible for most people.

## PRs

This command lists non-draft open pull requests on all repositories, listed by
their age, with PR numbers being clickable hyperlinks.

```bash
$ mk prs
ansible/tox-ansible                 28 minutes ago  Exclude *-py3.10-dev.  #336
ansible/vscode-ansible               2 hours ago    Update the segment s  #1375
ansible-community/molecule-plugins  16 hours ago    [pre-commit.ci] pre-c  #238
ansible/ansible-content-actions      2 days ago      Install tox-ansible    #14
ansible/vscode-ansible               3 days ago      Bump @types/vscode f #1351
```

## Drafts

This command lists draft releases on all your repositories, so you would know
which projects need to be released next.

```bash
$ mk drafts
🟢 ansible/ansible-compat has no draft release.
🟢 ansible/ansible-creator has an empty draft release.
🟠 ansible/ansible-dev-environment draft release v24.4.4 created 35 days ago:

  ## Bugfixes
  - Add some tests (#160) @cidrblock

🟠 ansible/ansible-dev-tools draft release v24.6.0 created 27 days ago:

  ## Enhancements
  - Bump tox-ansible from 24.6.0 to 24.6.14 in /.config (#267)
  - Encapsulate community-ansible-dev-tools container building (#255) @ssbarnea
  - Add lock extra to allow reproducible installation (#254) @ssbarnea
```

## Alerts

This command displays open security alerts on your repositories.

```bash
$ mk alerts
https://github.com/ansible/ansible-dev-tools/security/dependabot/18
https://github.com/ansible/ansible-lint/security/dependabot/36
https://github.com/ansible/vscode-ansible/security/dependabot/28
```

[pre]: https://github.com/pycontribs/gh-pre
[gh]: https://cli.github.com/
