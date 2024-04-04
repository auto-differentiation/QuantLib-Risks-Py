
QuantLib-Risks: Risk-enabled QuantLib for Python
================================================

[![Download source](https://img.shields.io/github/v/release/auto-differentiation/QuantLib-Risks-Py?label=source&sort=semver)](https://github.com/auto-differentiation/QuantLib-Risks-Py/releases/latest)
[![PyPI version](https://img.shields.io/pypi/v/QuantLib-Risks?label=PyPI)](https://pypi.org/project/QuantLib-Risks)

---

This repository builds QuantLib Python bindings with automatic differentiation, enabling
fast risks calculation with QuantLib in Python.
It wraps [C++ QuantLib-Risks](https://github.com/auto-differentiation/QuantLib-Risks-Cpp)
in Python.
It uses elements from [QuantLib-SWIG](https://github.com/lballabio/QuantLib-SWIG) and
is kept in sync with it.

## Getting Started

You can install it as:

```
pip install QuantLib-Risks
```

## Getting Help

For documentation and other resources, see https://auto-differentiation.github.io/quantlib-risks/python/ .

If you have found an issue, want to report a bug, or have a feature request, please raise a [GitHub issue](https://github.com/auto-differentiation/QuantLib-Risks-Py/issues).

## Related Projects

- XAD Comprehensive automatic differentiation in [Python](https://github.com/auto-differentiation/xad-py) and [C++](https://github.com/auto-differentiation/xad)
- QuantLib-Risks: Fast risk evaluations in [Python](https://github.com/auto-differentiation/QuantLib-Risks-Py) and [C++](https://github.com/auto-differentiation/QuantLib-Risks-Cpp)

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for the process of contributing to this project.
Please also obey our [Code of Conduct](CODE_OF_CONDUCT.md) in all communication.

## Versioning

This repository follows the QuantLib versions closely. With each new QuantLib release,
a new release of QuantLib-Risks is prepared with the same version number.

## License

This project is licensed under the GNU Affero General Public License - see the [LICENSE.md](LICENSE.md) file for details.

It contains code from [QuantLib](https://www.quantlib.org) 
and [QuantLib-SWIG](https://github.com/lballabio/QuantLib-SWIG), 
which are shipped with a different (compatible) license.
Both licenses are included in [LICENSE.md](LICENSE.md)
