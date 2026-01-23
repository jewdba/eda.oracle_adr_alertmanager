# Contributing

Thank you for your interest in contributing to this project!

Contributions of all kinds are welcome, including bug reports, documentation improvements, and code changes.

______________________________________________________________________

## License and contributions

This project is licensed under the **MIT License**.

By submitting a contribution, you agree that:

- Your contribution is your own work or you have the right to submit it
- Your contribution will be licensed under the **MIT License**
- Your contribution may be modified and redistributed as part of the project

No Contributor License Agreement (CLA) is required.

______________________________________________________________________

## Getting started

### Visual Studio Code (VS Code)

We provide a shared VS Code configuration to ensure a consistent development experience across contributors.

```
.vscode
├── extensions.json
└── settings.json
```

<u>Notes</u>
Make sure you have created and activated the virtual environment (.venv) before opening the project in VS Code. VS Code will prompt you to install the recommended extensions when you open the repository.

#### Settings

The following settings enable automatic formatting, strict type checking, and a consistent Python environment.

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

#### Extensions

These extensions are recommended for all contributors working in VS Code:

```
{
    "recommendations": [
        "charliermarsh.ruff",
    ],
}
```

### Setup your development environment

#### Clone the repository

```
# Folder structure required for ansible-test sanity  
mkdir ~/Ansible_devs/ansible_collections
cd ~/Ansible_devs/ansible_collections
mkdir jewdba
cd jewdba
git clone <REPO_URL>
cd <REPO_NAME>
```

##### Create and activate a virtual environment

```
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel


# Create virual environent
uv venv 
# Activate venv
source .venv/bin/activate
# Install all dependencies (including devel)
uv sync --all-extras
# Install project in editable mode
uv pip install -e . 


# deploy pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

### Pre-Commit Hooks configuration

Run hooks manually (optional but recommended):

```
pre-commit run --all-files
```

Pre-commit hooks configured:

- pycln Remov es unused imports from Python code
- mdformat Formats Markdown files consistently
- commitizen Validates commit messages follow Conventional Commit standards
- black Python code formatter
- ruff Lints and formats Python code
- mypy Static type checking for Python
- pytest Runs unit and integration tests
- ansible-test sanity Ansible collection static check

Please refer to [.pre-commit-config.yaml](.pre-commit-config.yaml) for details.

### Commit Guidelines

We follow Conventional Commit standards. Examples:

```
feat: add new feature
fix: resolve issue with parsing
chore: update dependencies
```

Validate commit messages using Commitizen:

```
cz check
```

Bump change(s) in dry-run mode:
```
cz bump --dry-run --yes
```

Pre-commit runs this automatically on the commit-msg stage (enforced).

Commitzen changelog <u>generated automatically by GitHub CI workflow [.github/workflows/build.yml](.github/workflows/build.yml)</u>

### Build Ansible collection documentation (antsibull-docs/Sphinx)

Initialize antsibull-docs/Sphinx:

```
antsibull-docs sphinx-init --use-current --dest-dir docs jewdba.eda
```

**Note**: Currently, generating documentation automatically may fail with EDA source plugins.
<u>Workarround:</u> Use manually created documentation structure:

```
docs/docsite/rst
├── event_sources
│   └── oracle_adr_alertmanager.html
└── index.html
```

Build documation with aformentioned workarround:

```
uv pip install -r docs/requirements.txt
uv run sphinx-build -b html docs docs/docsite
```

<u>Documenation generated automatically by GitHub CI workflow [.github/workflows/build.yml](.github/workflows/build.yml)</u>

### Ansible-test

**Ansible-test** ensures that code is reliable, follows best practices, and passes automated tests before being released. It is the primary tool for checking modules, plugins, and collections in Ansible projects.

#### Usage

Run **sanity checks** to validate code style, linting, and best practices:

```
uv run ansible-test sanity
uv run ansible-test tests
```

<u>Executed automatically by GitHub CI workflow [.github/workflows/python-ci.yml](.github/workflows/python-ci.yml)</u>

### Build Ansible collection 


Build the collection artifact locally using ansible-galaxy

```
uv run ansible-galaxy collection build
```

<u>Executed automatically by GitHub CI workflow [.github/workflows/build.yml](.github/workflows/build.yml)</u>


Deploy Ansible collection manually
```
ansible-galaxy collection install <Path to collection tarball>/jewdba-eda-1.0.0.tar.gz --force
```

## GitHub CI

### Testing GitHub Actions Locally (using `act`)

This project uses GitHub Actions for CI/CD. Contributors are encouraged to test
workflows locally before pushing changes using [`act`](https://github.com/nektos/act).

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

Test a particular workflow (option -W):

```
export DOCKER_HOST=unix:///Users/jew/.rd/docker.sock
act -W .github/workflows/build.yml \
    --container-daemon-socket - \
    -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest
``
