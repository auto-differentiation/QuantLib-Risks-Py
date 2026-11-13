This package enables fast risks calculations on the QuantLib Python package. 
It provides the same interface as the [standard QuantLib package](https://pypi.org/project/QuantLib/), and in addition allows to calculate risks (sensitivities) using automatic differentiation via the [XAD automatic differentiation tool](https://auto-differentation.github.io).

Useful links:

-   [QuantLib Documentation](https://www.quantlib.org)
-   [XAD Documentation, incl Python bindings and QuantLib integration](https://auto-differentiation.github.io/quantlib-risks/python/)

## Installation

```
pip install QuantLibAAD
```

This package was called QuantLib-Risks up to version 1.33.3. `QuantLib-Risks` 1.44.0 is the last
release under that name: a deprecated alias that installs `QuantLibAAD` 1.44 and keeps
`import QuantLib_Risks` working with a `DeprecationWarning`; newer versions are QuantLibAAD only.
Anyone pinned to `QuantLib-Risks==1.33.3` must also pin `xad<2`.

Binary wheels are provided for CPython 3.10 to 3.14 on Linux (x86_64, aarch64), macOS (x86_64, arm64)
and Windows (x86_64). The package requires the matching [xad](https://pypi.org/project/xad/) release,
which pip installs automatically.

### Building from source

On other platforms pip builds the package from the source distribution, which compiles QuantLib
and takes a while. This needs a C++17 compiler; CMake, Ninja and SWIG are
fetched as build dependencies, and Boost headers are downloaded unless found on the system
(or via `BOOST_ROOT`). To build from a clone of the
[repository](https://github.com/auto-differentiation/QuantLibAAD-Py):

```
git clone --recurse-submodules https://github.com/auto-differentiation/QuantLibAAD-Py.git
pip install -v ./QuantLibAAD-Py
```

## Usage Illustration

```python
import QuantLibAAD as ql
from xad.adj_1st import Tape

with Tape() as tape:
    rate = ql.Real(0.2)
    tape.registerInput(rate)
    
    # quantlib pricing code
    ...
    npv = option.NPV()
    

    tape.registerOutput(npv)
    npv.derivative = 1.0
    tape.computeAdjoints()

    print(f"price = {npv}")
    print(f"delta = {rate.derivative}")
```

## Related Projects

- XAD Comprehensive automatic differentiation in [Python](https://github.com/auto-differentiation/xad-py) and [C++](https://github.com/auto-differentiation/xad)
- QuantLibAAD: Fast risk evaluations in [Python](https://github.com/auto-differentiation/QuantLibAAD-Py) and [C++](https://github.com/auto-differentiation/QuantLibAAD)
