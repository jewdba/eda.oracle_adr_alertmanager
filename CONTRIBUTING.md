# Contributing

Thank you for your interest in contributing to this project!

Contributions of all kinds are welcome, including bug reports, documentation improvements, and code changes.

______________________________________________________________________

# License and contributions

This project is licensed under the **MIT License**.

By submitting a contribution, you agree that:

- Your contribution is your own work or you have the right to submit it
- Your contribution will be licensed under the **MIT License**
- Your contribution may be modified and redistributed as part of the project

No Contributor License Agreement (CLA) is required.

______________________________________________________________________

# Getting started

## Clone the repo

```
git clone https://github.com/jewdba/eda.oracle_adr_alertmanager.git
```


## Create and activate a virtual environment

```
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

# Create virtual environent
uv venv 

# Activate virtual environment
source .venv/bin/activate

# Install all dependencies (including devel)
uv sync --all-extras

# Install project in editable mode
uv pip install -e . 

# deploy pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## Visual Studio Code (VS Code)

We provide a shared VS Code configuration to ensure a consistent development experience across contributors.

```
.vscode
├── extensions.json
└── settings.json
```

### Recommended Settings:

```
{
  "editor.formatOnSave": true,
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "pylint.enabled": true,
  "pylint.importStrategy": "fromEnvironment",
  "python.analysis.typeCheckingMode": "strict"
}

```

### Recommended Extensions:


```
{
    "recommendations": [
        "charliermarsh.ruff",
    ],
}
```

**Note**: Make sure the virtual environment is created and activated before opening the project in VS Code. VS Code will prompt to install recommended extensions


______________________________________________________________________

# Code Quality & Testing Guidance

## Pre-commit Hooks

Run manually (optional but recommended):
```
pre-commit run --all-files
```

| Hook                | Purpose                                          |
| ------------------- | ------------------------------------------------ |
| pycln               | Removes unused imports from Python code          |
| mdformat            | Formats Markdown files consistently              |
| commitizen          | Validates commit messages (Conventional Commits) |
| black               | Python code formatter                            |
| ruff                | Lints and formats Python code                    |
| mypy                | Static type checking                             |
| pytest              | Runs unit and integration tests                  |
| ansible-test sanity | Checks Ansible collection best practices         |


For details, see [.pre-commit-config.yaml](.pre-commit-config.yaml).


### Commit Guidelines

We follow **Conventional Commit standards**. Examples:

```
feat: add new feature
fix: resolve issue with parsing
chore: update dependencies
```

Validate commit messages with Commitizen:
```
uv run cz check
```

Bump version changes (dry-run mode):
```
uv run cz bump --dry-run --yes
```

Changelog is generated automatically using npm by the GitHub CI workflow: [.github/workflows/build.yml](.github/workflows/build.yml)

## Ansible-test

**Ansible-test** ensures code reliability, best practices, and passes automated tests.


Manual execution of `ansible-test` requires your project to follow the standard Ansible collection layout:
```
ansible_collections/<namespace>/<collection>/
```

Run checks manually:
```
uv run ansible-test sanity
uv run ansible-test tests
```

Executed automatically by GitHub CI workflow [.github/workflows/python-ci.yml](.github/workflows/python-ci.yml)

______________________________________________________________________
# GitHub CI

## Local testing with `act`

This project uses GitHub Actions for CI/CD. Contributors can test workflows locally using [`act`](https://github.com/nektos/act) without pushing commits.

`act` allows you to run GitHub Actions workflows locally using Docker, without
needing to push commits to GitHub.
333

### Using `act` with Rancher Desktop @ MacOS

```
# cd <Navigate to project root folder>
export DOCKER_HOST=unix:///Users/jew/.rd/docker.sock
act \
  --container-daemon-socket - \
  -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest \
  --rm                    
```

Test a specific workflow:
```
export DOCKER_HOST=unix:///Users/jew/.rd/docker.sock
act -W .github/workflows/python-ci.yml \
  --container-daemon-socket - \
  -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest \
  --rm


# Local act build test (Build preserved as filesystem bind-mounted)
export DOCKER_HOST=unix:///Users/jew/.rd/docker.sock
act -W .github/workflows/build.yml \
  -e <(echo '{"env":{"ACT":"true"}}') \
  --container-daemon-socket - \
  --bind \
  -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest \
  --rm


```

______________________________________________________________________
# Documentation

## Sphinx / Antsibull-docs

Initialize documentation:

```
antsibull-docs sphinx-init --use-current --dest-dir build_docsite jewdba.eda
```

**Note**: Generating documentation automatically may fail for EDA source plugins. Use a manual structure as a workaround:
```
build_docsite/rst
├── event_sources
│   └── oracle_adr_alertmanager.html
└── index.html
```

Build the documentation:
```
uv pip install -r docs/requirements.txt
uv run sphinx-build -b html build_docsite docs/docsite
```

Documenation is generated automatically by GitHub CI workflow [.github/workflows/build.yml](.github/workflows/build.yml)

______________________________________________________________________
# Build Ansible collection 

Build artifact locally:
```
uv run ansible-galaxy collection build
```

<u>Executed automatically by GitHub CI workflow [.github/workflows/build.yml](.github/workflows/build.yml)</u>

Deploy manually:
```
ansible-galaxy collection install <Path to collection tarball>/jewdba-eda-1.0.0.tar.gz --force
```
