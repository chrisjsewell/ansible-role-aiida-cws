from ansible.errors import AnsibleFilterError


def aiida_conda_packages(python_version, core_version, code_plugins, add_packages):
    """Create a list of packages to install in the `aiida` conda environment.

    :param python_version: The python version to use.
    :param core_version: The aiida-core version to use.
    :param code_plugins: A dict of code plugin dictionaries, each should contain 'aiida_packages'.
    :param add_packages: A list of additional packages to install.
    """
    _var_name = "aiida_conda_code_plugins"
    output = [
        "python={}".format(python_version),
        "aiida-core={}".format(core_version),
    ]
    if not isinstance(code_plugins, dict):
        raise AnsibleFilterError(
            "%s requires a dict, got %s" % (_var_name, type(code_plugins))
        )
    for name, plugin in code_plugins.items():
        if not isinstance(plugin, dict):
            raise AnsibleFilterError(
                "%s requires a dict of dicts, got item %s: %s"
                % (_var_name, name, plugin)
            )
        if not ("aiida_packages" in plugin):
            raise AnsibleFilterError(
                "%s requires items containing 'aiida_packages', got item %s: %s"
                % (_var_name, name, plugin)
            )
        if not isinstance(plugin["aiida_packages"], list):
            raise AnsibleFilterError(
                "%s requires key aiida_packages to be a list, for %s got: %s"
                % (_var_name, name, plugin["aiida_packages"])
            )
        output.extend(plugin["aiida_packages"])
    return output + add_packages


class FilterModule:
    def filters(self):
        return {"aiida_conda_packages": aiida_conda_packages}
