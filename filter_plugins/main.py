from ansible.errors import AnsibleFilterError


def aiida_conda_packages(python_version, core_version, code_plugins, add_packages):
    """Create a list of packages to install in the `aiida` conda environment.
    
    :param python_version: The python version to use.
    :param core_version: The aiida-core version to use.
    :param code_plugins: A list of code plugin dictionaries,
        each should contain 'plugin_package' and 'plugin_version'.
    :param add_packages: A list of additional packages to install.
    """
    output = [
        "python={}".format(python_version),
        "aiida-core={}".format(core_version),
    ]
    if not isinstance(code_plugins, list):
        raise AnsibleFilterError(
            "aiida_code_plugins_list requires a list, got %s" % type(code_plugins)
        )
    for plugin in code_plugins:
        if not isinstance(plugin, dict):
            raise AnsibleFilterError(
                "aiida_code_plugins_list requires a list of dicts, got item %s" % plugin
            )
        if not ("plugin_package" in plugin and "plugin_version" in plugin):
            raise AnsibleFilterError(
                "aiida_code_plugins_list requires items containing 'plugin_package' and 'plugin_version', got item %s"
                % plugin
            )
        output.append("%s=%s" % (plugin["plugin_package"], plugin["plugin_version"]))
    return output + add_packages


class FilterModule:
    def filters(self):
        return {"aiida_conda_packages": aiida_conda_packages}
