[![CI](https://github.com/marvel-nccr/ansible-role-aiida-cws/workflows/CI/badge.svg)](https://github.com/marvel-nccr/ansible-role-aiida-cws/actions)
[![Release](https://img.shields.io/github/tag/marvel-nccr/ansible-role-aiida-cws.svg)](https://github.com/marvel-nccr/ansible-role-aiida-cws/releases)
<!-- [![Ansible Role](https://img.shields.io/ansible/role/25521.svg)](https://galaxy.ansible.com/marvel-nccr/aiida-cws) -->

# Ansible Role: marvel-nccr.aiida-cws

An Ansible role that installs and configures an environment for running the [AiiDA common-workflows](https://github.com/aiidateam/aiida-common-workflows) on Linux Ubuntu (with a bash shell).

The primary goal is to create an environment that a user can enter and, without any other steps, run commands like:

```shell
aiida-common-workflows launch relax quantum_espresso -S Si -X qe.pw -n 2
```

For all the available (open-source) simulation codes: `abinit`, `bigdft` (to come), `cp2k`, `fleur`, `nwchem`, `qe`, `siesta`, `wannier90`, `yambo`.

The key components are:

- **PostgreSQL** is installed system wide, with auto-start service.
- **RabbitMQ** is installed system wide, with auto-start service.
- **Conda** installed system wide (as [miniforge](https://github.com/conda-forge/miniforge)), with activation on terminals
- The **AiiDA** python environment installed into the `aiida` Conda environment, including the `aiida-common-workflows` package, dependent plugins, and `jupyterlab`, then a profile is created.
- Each simulation code, and their dependencies, are installed into their own Conda environment.
  - Then an AiiDA `Code` is created for each code executable
- The `aiida-pseudo` package is used to install the requisite pseudo-potentials.

The of the conda package and environment manager allows for fast installation of pre-compiled simulation codes, which are isolated from each other - ensuring correct use of dependency versions and environmental variables etc - but with sharing of common dependencies across environments (by use of hard-links), ensuring optimum memory usage.

## Installation

`ansible-galaxy install marvel-nccr.aiida-cws`

## Role Variables

See `defaults/main.yml`

## Example Playbook

```yaml
- hosts: servers
  roles:
  - role: marvel-nccr.aiida-cws
    vars:
      aiida_timezone_name: Europe/Zurich  # to set a certain timezone for AiiDA
      aiida_create_swapfile: true  # create a swapfile for RAM overflow, non-containers only
      aiida_allow_mpi_on_root: true  # containers only
```

If you want to install SLURM and use it as the scheduler, you can use e.g.:

```yaml
- hosts: servers
  roles:
  - role: marvel-nccr.slurm
  - role: marvel-nccr.aiida-cws
    vars:
      aiida_timezone_name: Europe/Zurich
      aiida_create_swapfile: true
      aiida_conda_code_computer: local_slurm_conda
```

## Usage

### Environment management

Once logged in to a terminal, the `base` environment of Conda is activated. To control the conda environments, you can use the `conda` command, or the `mamba` command is a drop-in replacement, for [faster installation of packages](https://wolfv.medium.com/the-future-of-mamba-fdf6d628b3df). FOr a brief introduction to Conda, see [the getting started tutorial](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html).

The alias `listenvs` (for `conda env --info`) can be used to list the available environments:

```shell
(base) root@instance:/# listenvs
# conda environments:
#
base                  *  /root/.conda
abinit                   /root/.conda/envs/abinit
aiida                    /root/.conda/envs/aiida
cp2k                     /root/.conda/envs/cp2k
fleur                    /root/.conda/envs/fleur
nwchem                   /root/.conda/envs/nwchem
qe                       /root/.conda/envs/qe
siesta                   /root/.conda/envs/siesta
wannier90                /root/.conda/envs/wannier90
yambo                    /root/.conda/envs/yambo
```

To enter an environment, use the alias `workon` (for `conda actiavate`):

```shell
(base) root@instance:/# workon aiida
(aiida) root@instance:/#
```

You can see what is installed in that environment, using `conda list`:

```shell
(aiida) root@instance:/# conda list
# packages in environment at /root/.conda/envs/aiida:
#
...
aiida-core                1.6.8              pyh6c4a22f_2    conda-forge
...
python                    3.8.13          h582c2e5_0_cpython    conda-forge
...
```

### Running AiiDA

This exposes the installed executables, such as `verdi` (with tab-completion) and `aiida-common-workflows`:

```shell
(aiida) root@instance:/# verdi status
 ✔ config dir:  /root/.aiida
 ✔ profile:     On profile generic
 ✔ repository:  /root/.aiida/repository/generic
 ✔ postgres:    Connected as aiida@localhost:5432
 ✔ rabbitmq:    Connected to RabbitMQ v3.6.10 as amqp://guest:guest@127.0.0.1:5672?heartbeat=600
 ✔ daemon:      Daemon is running as PID 18513 since 2022-07-23 18:40:31
```

You'll note that the `general` profile should already be set up, with connections to running PostgreSQL, RabbitMQ and AiiDA daemon systems services:

```shell
(aiida) root@instance:/# systemctl --type=service | grep -E '(rabbitmq|postgres|aiida)'
aiida-daemon@generic.service  loaded active running AiiDA daemon service for profile generic
postgresql@10-main.service    loaded active running PostgreSQL Cluster 10-main
rabbitmq-server.service       loaded active running RabbitMQ Messaging Server
```

AiiDA codes are set up to run simulation code executables:

```shell
(aiida) root@instance:/# verdi code list
# List of configured codes:
# (use 'verdi code show CODEID' to see the details)
* pk 1 - abinit.main@local_direct_conda
* pk 2 - cp2k.main@local_direct_conda
* pk 3 - fleur.main@local_direct_conda
* pk 4 - fleur.inpgen@local_direct_conda
* pk 5 - nwchem.main@local_direct_conda
* pk 6 - qe.cp@local_direct_conda
* pk 7 - qe.neb@local_direct_conda
* pk 8 - qe.ph@local_direct_conda
* pk 9 - qe.pp@local_direct_conda
* pk 10 - qe.pw@local_direct_conda
* pk 11 - siesta.main@local_direct_conda
* pk 12 - wannier90.main@local_direct_conda
* pk 13 - yambo.main@local_direct_conda
```

These are set up use `conda run -n env_name /path/to/executable` to run the executable within the correct environment.

### Launching Jupyter Lab

Inside the `aiida` environment, you can launch Jupyter Lab with the `jupyter lab` command:

```shell
(aiida) root@instance:/# jupyter lab
```

If using the Docker container, you should add the following options:

```shell
(aiida) root@instance:/# jupyter lab  --allow-root --ip=0.0.0.0
```

You can manage what jupyter servers are running with:

```shell
(aiida) root@instance:/# jupyter server list
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

### Code style

Code style is formatted and linted with [pre-commit](https://pre-commit.com/).

```bash
pip install pre-commit
pre-commit run -all
```

### Deployment

Deployment to Ansible Galaxy is automated *via* GitHub Actions.
Simply tag a release `vX.Y.Z` to initiate the CI and release workflow.
Note, the release will only complete if the CI tests pass.

## License

MIT

## Contact

Please direct inquiries regarding Quantum Mobile and associated ansible roles to the [AiiDA mailinglist](http://www.aiida.net/mailing-list/).

## TODO

- Add "User Guide" inside the build (in desktop folder)
- move to building docker with [tini](https://github.com/krallin/tini) as PID 1
  - What system service manager to use in place of systemd? (<https://github.com/krallin/tini/issues/175>)
- jupyter lab launcher
- rest api service
- check everything still works with non-root user install
- migrate tasks from `marvel-nccr.simulationbase` (understand `hostname.yml`, which is non-container only, and `clean.yml`)
- Get <https://github.com/quanshengwu/wannier_tools> on Conda, to replace `marvel-nccr.wannier_tools`

- run code tests (how to check success <https://github.com/aiidateam/aiida-common-workflows/issues/289>?):
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
