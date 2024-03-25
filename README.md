
QuantLib-Risks: Risk-enabled QuantLib Python Bindings
=====================================================

[![Download source](https://img.shields.io/github/v/release/auto-differentiation/quantlib-risks?label=source&sort=semver)](https://github.com/auto-differentiation/quantlib-risks/releases/latest)
[![PyPI version](https://img.shields.io/pypi/v/quantlib-risks?label=PyPI)](https://pypi.org/project/quantlib-risks)

---

This fork of [QuantLib-SWIG](https://github.com/lballabio/QuantLib-SWIG) builds QuantLib Python bindings with automatic differentiation, enabling
fast risks calculation with QuantLib in Python.
It wraps [quantlib-xad](https://github.com/auto-differentiation/quantlib-xad)
in Python.

## Getting Started

You can install it as:

```
pip install quantlib-risks
```

## Getting Help

For documentation and other resources, see https://auto-differentiation.github.io/quantlib .

If you have found an issue, want to report a bug, or have a feature request, please raise a [GitHub issue](https://github.com/auto-differentiation/XAD/issues).

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for the process of contributing to this project.
Please also obey our [Code of Conduct](CODE_OF_CONDUCT.md) in all communication.

Note that large parts of this repository are left from the fork's origin (e.g. 
bindings for languages other than Python). They are unused in this fork.

## Versioning

This repository follows the QuantLib versions closely. With each new QuantLib release,
a new release of quantlib-risks is prepared with the same version number.

## License

This project is licensed under the GNU Affero General Public License - see the [LICENSE.md](LICENSE.md) file for details.

It contains code from [QuantLib](https://www.quantlib.org) 
and is based on [QuantLib-SWIG](https://github.com/lballabio/QuantLib-SWIG), 
which are shipped with a different (compatible) license.
Both licenses are included in [LICENSE.md](LICENSE.md)
