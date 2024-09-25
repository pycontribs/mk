# Supported Tools

## Embedded commands

### changelog (github)

`changelog` command will produce a `CHANGELOG.md` file based on Github Releases.
You can define `CHANGELOG_FILE` environment variable to make it generate the
file in a different location.

This command is available only when `gh` command line utility is installed.

### containers check

You can use this command to verify if a specific container image has a maximum
size or maximum number of layers. This is useful when you want to prevent
accidental grow of an image your are producing.

```bash
$ mk containers check your-image-id-or-name --max-size=200 --max-layers=1
Image has too many layers: 3 > 1
Image size exceeded the max required size (MB): 301 > 200
FAIL: 1
```

You can also specify the container engine to be used, the default is to use
docker if found or podman if docker is not found.

## Recognized tools

### make

If a [makefile](https://www.gnu.org/software/make/manual/make.html) is found on
the repository root, the tool will expose all its targets that have a trailing
comment with a double hash - `## <description>`. If the comment is not found,
the command will not be exposed, as we assume that this is an internal target.

A good example of a project using this pattern is
[podman](https://github.com/containers/podman).

### npm

If a [package.json](https://docs.npmjs.com/cli/v7/configuring-npm/package-json)
file is found, the tool will expose all the scripts defined in the `scripts`.

Due to the
[lack of comments inside the package.json](https://stackoverflow.com/questions/14221579/how-do-i-add-comments-to-package-json-for-npm-install)
files, we are unable to provide descriptions for exposed commands. Still, if
others will find a good way to do it that gets some adoption, we will be more
than happy to add support for loading descriptions too.

### shell

All shell scripts found inside the repository root and`(scripts|tools|bin)/`
sub-folders will be exposed as commands.

### taskfile

[Taskfile](https://taskfile.dev/#/) is a task runner that uses YAML files. It is
similar to make, but it is written in Go and it is more flexible.

### tox

All tox environments will be exposed as commands and their descriptions will
also be shown. Internally, the tool will run `tox -lav` to get the list of
available environments and their descriptions.

### ansible

Any playbook found inside the `playbooks/` sub-folder will be exposed as a
command.

### git

Inside git repositories, the tool will expose the `up` command which can be used
to create an upstream pull request.

If the current git repository is using
[Gerrit](https://www.gerritcodereview.com), it will run `git review` and if the
repository is from GitHub, it will run `gh pr create` instead.

### pre-commit

If a [pre-commit](https://pre-commit.com/) configuration file is found, the tool
will expose the `lint` command for running linting.

### py (python packages)

If the current repository is a Python package, the tool will expose a set of
basic commands:

- `install`: Install the package in editable mode, `pip install -e .`
- `uninstall`: Uninstall the current package
- `build`: Run `python -m build`

### pytest

If a [pytest](https://docs.pytest.org/en/stable/) configuration file is found, a
`test` command will be exposed that runs `pytest`.
