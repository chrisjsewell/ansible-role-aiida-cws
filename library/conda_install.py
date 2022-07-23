#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os.path
import typing as t
from shlex import split as shlex_split
from shutil import which as find_executable

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: conda_install
short_description: Install Conda packages
description: Install Conda packages
author: 
  - Chris Sewell
notes:  Requires conda to already be installed.
options:
  packages:
    description: The name of the packages to install.
    required: true
  executable:
    description: Full path to the conda executable.
    required: false
  channels:
    description: Extra channels to use when installing packages.
    required: false
  env:
    description: Name of the environment (if it does not exist then it will be created).
    required: false
  extra_args:
    description: Extra arguments passed to Conda.
    required: false
"""

EXAMPLES = """
- name: install packages via Conda
  conda_install: 
    packages:
    - git=2
    - numpy
"""

RETURN = """
output:
    description: JSON output from Conda
    returned: `changed == True`
    type: dict
stderr:
    description: stderr content written by Conda
    returned: `changed == True`
    type: str
"""


def _main():
    """Module entrypoint."""
    module = AnsibleModule(
        argument_spec={
            "packages": {"required": True, "type": "list"},
            "executable": {"default": None, "required": False},
            "env": {"default": None, "required": False},
            "channels": {"default": None, "required": False, "type": "list"},
            "extra_args": {"default": None, "required": False, "type": "str"},
        },
        supports_check_mode=True,
    )

    command = []
    try:
        command.append(find_conda(module.params["executable"]))
    except CondaExecutableNotFoundError as exc:
        module.fail_json(msg=str(exc))

    command.extend(["install", "--yes", "--json"])

    if module.params["env"]:
        command.extend(["--name", module.params["env"]])

    if module.check_mode:
        command.append("--dry-run")

    if module.params["channels"]:
        for channel in module.params["channels"]:
            command += ["--channel", channel]

    if module.params["extra_args"]:
        command += shlex_split(module.params["extra_args"])

    command += module.params["packages"]

    try:
        output, stderr = _run_conda_command(module, command)
    except CondaMissingEnvironmentError:
        # retry by creating the environment, instead of installing into it
        command[1] = "create"
        try:
            output, stderr = _run_conda_command(module, command)
        except CondaKnownError as exc:
            module.fail_json(msg=str(exc))
        else:
            module.exit_json(changed=True, output=output, stderr=stderr)
    except CondaKnownError as exc:
        module.fail_json(msg=str(exc))

    if (
        "message" in output
        and output["message"] == "All requested packages already installed."
    ):
        module.exit_json(changed=False)
    else:
        module.exit_json(changed=True, output=output, stderr=stderr)


def find_conda(executable: t.Optional[str]) -> str:
    """
    If `executable` is not None, checks whether it points to a valid file
    and returns it if this is the case. Otherwise tries to find the `conda`
    executable in the path. Calls `fail_json` if either of these fail.
    """
    if not executable:
        executable = "conda"

    if os.path.isfile(executable):
        return executable
    else:
        executable = find_executable(executable)
        if executable:
            return executable

    raise CondaExecutableNotFoundError(executable)


def _clean_conda_stdout(stdout: str) -> str:
    """Conda spews loading progress reports onto stdout(!?),
    which need ignoring. Bug observed in Conda version 4.3.25.

    :param stdout: the output from stdout
    """
    split_lines = stdout.strip().split("\n")
    while len(split_lines) > 0:
        line = split_lines.pop(0).strip("\x00")
        try:
            line_content = json.loads(line)
            if "progress" not in line_content and "maxval" not in line_content:
                # Looks like this was the output, not a progress update
                return line
        except ValueError:
            split_lines.insert(0, line)
            break

    return "".join(split_lines)


class CondaKnownError(Exception):
    """Raised when Conda returns a known error."""


class CondaMissingEnvironmentError(Exception):
    """Raised when the Conda environment is missing."""


class CondaCommandError(CondaKnownError):
    """Raised when a Conda command fails for any reason"""

    def __init__(self, command: t.List[str], stdout: str, stderr: str):
        msg = "'" + " ".join(command) + "' "
        msg += ", stdout: %s." % stdout if stdout.strip() != "" else ""
        msg += ", stderr: %s." % stderr if stderr.strip() != "" else ""

        super().__init__("Error running command: " + msg)


class CondaOutputError(CondaKnownError):
    """Raised when a Conda command fails, with a known error."""

    def __init__(self, msg: str, exception_name: str):
        self.exception_name = exception_name
        super().__init__(msg)


class CondaExecutableNotFoundError(CondaKnownError):
    """Raised when the Conda executable was not found."""

    def __init__(self, executable: str):
        super().__init__(f"Conda executable not found: {executable}")


def _run_conda_command(
    module: AnsibleModule, command: t.List[str]
) -> t.Tuple[t.Any, str]:
    """Runs the given Conda command.

    :param module: Ansible module
    :param command: the Conda command to run, which must return JSON
    :returns: (output JSON, stderr)
    """
    rc, stdout, stderr = module.run_command(command)
    stdout = _clean_conda_stdout(stdout)

    # https://github.com/mamba-org/mamba/issues/1802
    if stdout.startswith("Encountered problems while solving:"):
        raise CondaOutputError(stdout, "PackagesNotFoundError")

    try:
        output = json.loads(stdout)
    except ValueError:
        raise CondaCommandError(command, stdout, stderr)

    if rc != 0:
        if "error" in output:
            exception_name = output.get("exception_name")
            if exception_name == "EnvironmentLocationNotFound":
                raise CondaMissingEnvironmentError(output.get("error"))
            raise CondaOutputError(output["error"], exception_name)
        raise CondaCommandError(command, stdout, stderr)

    return output, stderr


if __name__ == "__main__":
    _main()
