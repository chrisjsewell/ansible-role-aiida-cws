[![CI](https://github.com/marvel-nccr/ansible-role-aiida-cws/workflows/CI/badge.svg)](https://github.com/marvel-nccr/ansible-role-aiida-cws/actions)
[![Ansible Role](https://img.shields.io/ansible/role/25521.svg)](https://galaxy.ansible.com/marvel-nccr/aiida-cws)
[![Release](https://img.shields.io/github/tag/marvel-nccr/ansible-role-aiida-cws.svg)](https://github.com/marvel-nccr/ansible-role-aiida-cws/releases)

# Ansible Role: marvel-nccr.aiida-cws

An Ansible role that installs and configures an environment for running the [AiiDA common-workflows](https://github.com/aiidateam/aiida-common-workflows) on Linux Ubuntu (with a bash shell).

The primary goal is to create an environment that a user can enter and, without any other steps, run commands like:

```shell
aiida-common-workflows launch relax siesta --structure=Si -X siesta -n 2
```

For all the available (open-source) simulation codes: `abinit`, `cp2k`, `fleur`, `nwchem`, `qe`, `siesta`, `wannier90`, `yambo`.

The key components are:

- PostgreSQL installed system wide, with auto-start service.
- RabbitMQ installed system wide, with auto-start service.
- Conda installed system wide, with activation on terminals
- The AiiDA python environment installed into the `aiida` Conda environment, including the `aiida-common-workflows` package, dependent plugins, and `jupyterlab`, then a profile is created.
- Each simulation code, and their dependencies, are installed into their own Conda environment.
  - Then an AiiDA `Code` is created for each code executable
- The `aiida-pseudo` package is used to install the requisite pseudo potentials.

## Installation

`ansible-galaxy install marvel-nccr.aiida-cws`

## Role Variables

See `defaults/main.yml`

## Example Playbook

```yaml
- hosts: servers
  roles:
  - role: marvel-nccr.aiida-cws
```

## Development and testing

This role uses [Molecule](https://molecule.readthedocs.io/en/latest/#) and [Docker](https://www.docker.com/) for tests.

After installing [Docker](https://www.docker.com/):

Clone the repository into a package named `marvel-nccr.aiida-cws` (the folder must be named the same as the Ansible Galaxy name)

```bash
git clone https://github.com/marvel-nccr/ansible-role-aiida-cws marvel-nccr.aiida-cws
cd marvel-nccr.aiida-cws
```

Then run:

```bash
pip install -r requirements.txt  # Installs molecule
molecule test  # runs tests
```

or use tox (see `tox.ini`):

```bash
pip install tox
tox
```

## Code style

Code style is formatted and linted with [pre-commit](https://pre-commit.com/).

```bash
pip install pre-commit
pre-commit run -all
```

## Deployment

Deployment to Ansible Galaxy is automated *via* GitHub Actions.
Simply tag a release `vX.Y.Z` to initiate the CI and release workflow.
Note, the release will only complete if the CI tests pass.

## License

MIT

## Contact

Please direct inquiries regarding Quantum Mobile and associated ansible roles to the [AiiDA mailinglist](http://www.aiida.net/mailing-list/).

## TODO

- move to building docker with [tini](https://github.com/krallin/tini) as PID 1
  - What system service manager to use in place of systemd? (<https://github.com/krallin/tini/issues/175>)
- jupyter lab launcher
- rest api service
- check everything still works with non-root user install
- report on `du -sh /root` (8Gb) and `du -sh /root/.conda/envs/*`

- run pip check at end, on aiida environment (but would currently fail)
- run code tests (how to check success?):
  - `aiida-common-workflows launch relax abinit -S Si -X abinit.main -n 2`  ✅
    - although issues with `abipy` and `The netcdf library does not support parallel IO` and `nkpt*nsppol (29) is not a multiple of nproc_spkpt (2)`
  - `aiida-common-workflows launch relax cp2k -S Si -X cp2k.main -n 1` ✅
    - But `-n 2` fails ❌
    - quite slow to run as well
  - `aiida-common-workflows launch relax fleur -S Si -X fleur.main -n 2 2` ✅
  - `aiida-common-workflows launch relax quantum_espresso -S Si -X qe.pw -n 2` ✅
  - `aiida-common-workflows launch relax siesta -S Si -X siesta.main -n 2` ❌
    - `Block Chemical_species_label does not exist`.
    - what is difference between 4.1.5 and MaX-1.2.0? (<https://gitlab.com/siesta-project/siesta/-/wikis/Guide-to-Siesta-versions>)
  - `aiida-common-workflows launch relax nwchem -S Si -X nwchem.main -n 2` ❌
    - The stdout output file was incomplete.
  - awaiting conda packages:
    - `aiida-common-workflows launch relax bigdft ...` (`bigdft` <https://github.com/conda-forge/staged-recipes/pull/19683>) ❓
    - `yambo` can also be installed but not in common workflows to test. (`aiida-yambo`) ❓

- `aiida-gaussian` and `aiida-common-workflow` need to update their dependency pinning of pymatgen to allow 2022, to be compatible with the latest `abipy=0.9`, also `abipy` should be a direct dependency of `aiida-abinit`.

- for common workflow group:
  - maintainership of feedstocks
  - confirm ranges of code versions compatibilities
  - check on use of `OMP_NUM_THREADS=1` (and other env vars)
  - get all to insure they are using latest pymatgen (2022), see <https://pymatgen.org/compatibility.html>
  - update to aiida-core v2

<https://wolfv.medium.com/the-future-of-mamba-fdf6d628b3df>
