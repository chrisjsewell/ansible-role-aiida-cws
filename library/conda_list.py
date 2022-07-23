#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os.path
import typing as t
from shutil import which as find_executable

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: conda_list
short_description: List Conda packages
description: List Conda packages
author: 
  - Chris Sewell
notes:  Requires conda to already be installed.
options:
  env:
    description: Name of the environment
    required: true
  regex:
    description: List only packages matching this regular expression.
    required: false
  executable:
    description: Full path to the conda executable.
    required: false
"""

EXAMPLES = """
- name: install packages via Conda
  conda_list: 
    env: base
    regex: ^python-
"""

RETURN = """
list:
    description: JSON output from Conda for each package (keys include 'name', 'version', 'channel')
    type: list of dict
"""


def _main():
    """Module entrypoint."""
    module = AnsibleModule(
        argument_spec={
            "env": {"default": None, "required": True},
            "executable": {"default": None, "required": False},
            "regex": {"default": None, "required": False},
        },
        supports_check_mode=True,
    )
    command = []
    try:
        command.append(find_conda(module.params["executable"]))
    except CondaExecutableNotFoundError as exc:
        module.fail_json(msg=str(exc))
    command.extend(["list", "--json", "--name", module.params["env"]])
    if module.params["regex"]:
        command.append(module.params["regex"])
    rc, stdout, stderr = module.run_command(command)
    if rc != 0:
        module.fail_json("Command failed", rc=rc, stdout=stdout, stderr=stderr)
    try:
        output = json.loads(stdout)
    except json.decoder.JSONDecodeError:
        module.fail_json("stdout not JSON", rc=rc, stdout=stdout, stderr=stderr)
    # if environment not found then a dict will be returned 'error' key etc
    if not isinstance(output, list):
        module.fail_json(
            f"Environment not found: {module.params['env']}",
            rc=rc,
            stdout=stdout,
            stderr=stderr,
        )
    return module.exit_json(changed=False, output=output, rc=rc)


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


class CondaKnownError(Exception):
    """Raised when Conda returns a known error."""


class CondaExecutableNotFoundError(CondaKnownError):
    """Raised when the Conda executable was not found."""

    def __init__(self, executable: str):
        super().__init__(f"Conda executable not found: {executable}")


if __name__ == "__main__":
    _main()
