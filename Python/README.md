This package enables fast risks calculations on the QuantLib Python package. 
It provides the same interface as the [standard QuantLib package](https://pypi.org/project/QuantLib/), and in addition allows to calculate risks (sensitivities) using automatic differentiation via the [XAD automatic differentiation tool](https://auto-differentation.github.io).

Useful links:

-   [QuantLib Documentation](https://www.quantlib.org)
-   [XAD Documentation, incl Python bindings and QuantLib integration](https://auto-differentiation.github.io/quantlib-risks/python/)

## Installation

```
pip install QuantLib-Risks
```

## Usage Illustration

```python
import QuantLib_Risks as ql
from xad.adj_1st import Tape

with Tape() as t:
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
- QuantLib-Risks: Fast risk evaluations in [Python](https://github.com/auto-differentiation/QuantLib-Risks-Py) and [C++](https://github.com/auto-differentiation/QuantLib-Risks-Cpp)
