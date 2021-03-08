<br/>
<img align="right" src="docs/source/_static/logo.png" height="120"/>

# Steinbit

![build](https://github.com/rocktype/rocktype/actions/workflows/build.yaml/badge.svg)

## Contributing

Please [read our code of conduct](../../blob/master/v2021.01.md).


| File or folder           | Purpose |
| -----------------------  | ------- |
| [`README.md`](../../blob/master/README.md)               | Provides a high-level overview of the project |
| [`LICENSE`](../../blob/master/LICENSE)                   | License file (usually Apache v2.0) |
| [`requirements.txt`](../../blob/master/requirements.txt) | Dependencies for use of the python project |
| [`setup.py`](../../blob/master/setup.py)                 | Installation script for the python project |
| [`setup.cfg`](../../blob/master/setup.cfg)               | Configuration of tools (testing, linting etc...) |
| [`default.nix`](../../blob/master/default.nix) and [`nix/`](../../tree/master/nix) | Dependency management for the [nix](https://github.com/nixos) tool |
| [`steinbit/`](../../tree/master/steinbit/)(`<project>/`) | The python project folder |
| [`tests/`](../../tree/master/tests/)                     | Tests for the python project | 
| [`docs/`](../../tree/master/docs/)                       | Python documentation in [reStructureText](https://rest-sphinx-memo.readthedocs.io/en/latest/ReST.html) format |
| [`.github/workflows/`](../../tree/master/.github/workflows/) | GitHub Actions scripts for building, packaging and distributing the project |

## :hammer_and_pick: Tools and standards

* Python testing with coverage reporting via pytest and pytest-cov

  `$ pytest`

* Python code-styling via flake8. We follow the [numpy style guide](https://numpydoc.readthedocs.io/en/latest/format.html) for docstrings and use [sphinx-napoleon](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/) to render it.

  `$ flake8`

* Python static typing via mypy

  `$ mypy`

* Code documentation in [reST](https://rest-sphinx-memo.readthedocs.io/en/latest/ReST.html) using Sphinx

  `$ sphinx-build docs/source html`

* [Optional but recommended] GitHub markdown for the README.md and other markdown files

  `$ grip -b`

* [Optional but recommended] nix for package management. The following command will open a shell with all of the above commands in place:

  `$ nix-shell`
  `$ nix-build nix/rocktype.nix`

## :cloud: External Services

* Continuous Integration: [GitHub Actions](https://github.com/features/actions)
* Code coverage reporting: [Codecov](https://about.codecov.io/)
* Documentation: [Read the docs](https://readthedocs.org/)
* Packaging: [The Python Package Index (PyPI)](https://pypi.org/)
