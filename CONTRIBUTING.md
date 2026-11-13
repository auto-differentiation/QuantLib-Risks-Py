# How to contribute

We love pull requests from everyone. By participating in this project, you agree to abide
by our [code of conduct](CODE_OF_CONDUCT.md).

Note that this fork is importing all changes from the QuantLib-SWIG repository on each
release. Changes related to QuantLib's own Python bindings will be included in each new
release. 
Contributions to this repository should only be made if they are related to building
the Python bindings for QuantLibAAD (enabled with XAD).

1.  Fork, then clone the repository with its submodules:

```bash
git clone --recurse-submodules https://github.com/yourusername/QuantLibAAD-Py.git
```

2.  Follow the [Build Instructions](#build-instructions) below to build the software.
    Make sure all tests pass.

3.  Create a feature branch, typically based on master, for your change

```bash
git checkout -b feature/my-change main
```

4.  Make your changes, adding tests as you go, and commit. Again, make sure all 
    tests pass.

5.  Push your fork 

6.  [Submit a pull request][pr]. Not that you will have to sign the [Contributor License Agreement][cla] 
    before the PR can be merged.

At this point, you are depending on the core team to review your request. 
We may suggest changes, improvements, or alternatives. 
We strive to at least comment on a pull request within 3 business days. 
After feedback has been given, we expect a response within 2 weeks, 
after which we may close the pull request if it isn't showing activity.

Some things that will highly increase the chance that your pull request gets
accepted:

-   Discuss the change you wish to make via issue or email

-   Write good tests for all added features

-   Write good commit messages (short one-liner, followed by a blank line, 
    followed by a more detailed explanation)

## Build Instructions

The package is built in one step by [scikit-build-core](https://scikit-build-core.readthedocs.io)
(see `pyproject.toml`): CMake builds QuantLib as a static library together with
[QuantLibAAD](https://github.com/auto-differentiation/QuantLibAAD) from the `lib/` submodules,
against [XAD](https://github.com/auto-differentiation/xad) from the installed
[xad](https://pypi.org/project/xad/) package (`xad.get_cmake_dir()`), then the SWIG module from `SWIG/` and `Python/QuantLibAAD/`.

Requirements: Python 3.10+, and a C++17 compiler.
CMake, Ninja and SWIG are installed as build dependencies.
Boost headers are taken from the system if found (or `BOOST_ROOT`), otherwise Boost 1.90 is
downloaded.

```bash
git submodule update --init --recursive
python -m venv .venv
source .venv/bin/activate
pip install -v . pytest
# run the tests from outside the source tree, against the installed package
cd /tmp && python -m pytest --import-mode=importlib /path/to/QuantLibAAD-Py/Python/test
```

Notes:

-   The binary module links the xad package's shared libxad (found at runtime through the
    rpath `../xad/lib`, never bundled in the wheel) and shares its `Real` type, so
    `lib/pybind11` must be the exact version xad is built with, and the `xad` requirement is
    pinned to one major.minor series. Update them together.
-   `lib/QuantLib` is an unmodified QuantLib release; AAD support comes from QuantLibAAD.
-   Building QuantLib takes most of the time. To reuse it across builds (e.g. several Python
    versions), install it once and point the package build at it:

    ```bash
    cmake -DPREFIX=$PWD/build/quantlib-prefix -DPYTHON=$(which python) -P tools/build-quantlib.cmake
    pip install -v . -Ccmake.define.QLR_QUANTLIB_PREFIX=$PWD/build/quantlib-prefix
    ```

-   Wheels for all supported Python versions are built with
    [cibuildwheel](https://cibuildwheel.pypa.io) (`pipx run cibuildwheel`, configured in
    `pyproject.toml`), the source distribution with `pipx run build --sdist`.


[pr]: https://github.com/auto-differentiation/QuantLibAAD-Py/compare/

[cla]: https://gist.github.com/auto-differentiation-dev/5c6121c3f341e2de710fa034e9ff3263
