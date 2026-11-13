> Part of the [XAD ecosystem](https://github.com/auto-differentiation) — the fastest automatic differentiation library for C++.
> If this is useful to you, please star the [core XAD repository](https://github.com/auto-differentiation/xad).

QuantLibAAD: Risk-enabled QuantLib for Python
=============================================

[![Download source](https://img.shields.io/github/v/release/auto-differentiation/QuantLibAAD-Py?label=source&sort=semver)](https://github.com/auto-differentiation/QuantLibAAD-Py/releases/latest)
[![PyPI version](https://img.shields.io/pypi/v/QuantLibAAD?label=PyPI)](https://pypi.org/project/QuantLibAAD)

---

This repository builds QuantLib Python bindings with automatic differentiation, enabling
fast risks calculation with QuantLib in Python.
It wraps [C++ QuantLibAAD](https://github.com/auto-differentiation/QuantLibAAD)
in Python.
It uses elements from [QuantLib-SWIG](https://github.com/lballabio/QuantLib-SWIG) and
is kept in sync with it.

## Getting Started

You can install it as:

```
pip install QuantLibAAD
```

```python
import QuantLibAAD as ql
```

It links the XAD library that the [xad](https://pypi.org/project/xad) package ships, so
QuantLib and `xad` share one active tape per thread: a `xad.adj_1st.Tape` records QuantLib's
calculations as well as your own.

### Formerly QuantLib-Risks

This package was called QuantLib-Risks up to version 1.33.3. From 1.44, `QuantLib-Risks`
is a deprecated alias that installs `QuantLibAAD` and keeps `import QuantLib_Risks` working
with a `DeprecationWarning`. Please switch to `pip install QuantLibAAD` and
`import QuantLibAAD`. Anyone pinned to `QuantLib-Risks==1.33.3` must also pin `xad<2`.

## Notebooks

Run these notebooks on Google Colab, with nothing to install:

| Notebook | What it shows |
|---|---|
| [Quickstart](notebooks/01_quickstart.ipynb): a European option's Greeks in one adjoint sweep, checked against QuantLib's analytic Greeks and bumping | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/auto-differentiation/QuantLibAAD-Py/blob/main/notebooks/01_quickstart.ipynb) |
| [Curve risk](notebooks/02_curve_risk.ipynb): a swap book's sensitivities to every quote of a bootstrapped curve in one sweep | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/auto-differentiation/QuantLibAAD-Py/blob/main/notebooks/02_curve_risk.ipynb) |

## Getting Help

For documentation and other resources, see https://auto-differentiation.github.io/quantlib-aad/python/ .

If you have found an issue, want to report a bug, or have a feature request, please raise a [GitHub issue](https://github.com/auto-differentiation/QuantLibAAD-Py/issues).

## Related Projects

- XAD Comprehensive automatic differentiation in [Python](https://github.com/auto-differentiation/xad-py) and [C++](https://github.com/auto-differentiation/xad)
- QuantLibAAD: Fast risk evaluations in [Python](https://github.com/auto-differentiation/QuantLibAAD-Py) and [C++](https://github.com/auto-differentiation/QuantLibAAD)

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for the process of contributing to this project.
Please also obey our [Code of Conduct](CODE_OF_CONDUCT.md) in all communication.

## Versioning

This repository follows the QuantLib versions closely. With each new QuantLib release,
a new release of QuantLibAAD is prepared with the same version number.

## License

This project is licensed under the GNU Affero General Public License - see the [LICENSE.md](LICENSE.md) file for details.

It contains code from [QuantLib](https://www.quantlib.org) 
and [QuantLib-SWIG](https://github.com/lballabio/QuantLib-SWIG), 
which are shipped with a different (compatible) license.
Both licenses are included in [LICENSE.md](LICENSE.md)
