# pygnverifier

[![Release](https://img.shields.io/github/v/release/earth-metabolome-initiative/pygnverifier)](https://img.shields.io/github/v/release/earth-metabolome-initiative/pygnverifier)
[![Build status](https://img.shields.io/github/actions/workflow/status/earth-metabolome-initiative/pygnverifier/main.yml?branch=main)](https://github.com/earth-metabolome-initiative/pygnverifier/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/earth-metabolome-initiative/pygnverifier/branch/main/graph/badge.svg)](https://codecov.io/gh/earth-metabolome-initiative/pygnverifier)
[![Commit activity](https://img.shields.io/github/commit-activity/m/earth-metabolome-initiative/pygnverifier)](https://img.shields.io/github/commit-activity/m/earth-metabolome-initiative/pygnverifier)
[![License](https://img.shields.io/github/license/earth-metabolome-initiative/pygnverifier)](https://img.shields.io/github/license/earth-metabolome-initiative/pygnverifier)

A python wrapper for gnverifier

- **Github repository**: <https://github.com/earth-metabolome-initiative/pygnverifier/>
- **Documentation** <https://earth-metabolome-initiative.github.io/pygnverifier/>

## Examples on how to use the CLI:

1. Verify scientific names:

   ```
   python pygnverifier/cli.py verify -n "Pomatomus saltatrix" -n "Bubo bubo" --with-stats --verbose
   ```

   This command will verify the scientific names "Pomatomus saltatrix" and "Bubo bubo", include statistics, and enable verbose mode.

2. Verify scientific names with specific data sources:

   ```
   python pygnverifier/gnverifier_cli.py verify -n "Isoetes longissimum" -d 1 -d 12 --with-all-matches
   ```

   This command will verify the name "Isoetes longissimum" using data sources with IDs 1 and 12, and return all possible matches.

3. List available data sources:
   ```
   python pygnverifier/gnverifier_cli.py data-sources
   ```
   This command will list all available data sources from the GNVerifier API.

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:earth-metabolome-initiative/pygnverifier.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

## Releasing a new version

- Create an API Token on [PyPI](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/earth-metabolome-initiative/pygnverifier/settings/secrets/actions/new).
- Create a [new release](https://github.com/earth-metabolome-initiative/pygnverifier/releases/new) on Github.
- Create a new tag in the form `*.*.*`.
- For more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/cicd/#how-to-trigger-a-release).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
