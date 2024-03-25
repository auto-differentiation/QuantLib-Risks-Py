This package enables fast risks calculations on the QuantLib Python package. 
It provides the same interface as the [standard QuantLib package](https://pypi.org/project/QuantLib/), and in addition allows to calculate risks (sensitivities) using automatic differentiation via the [XAD automatic differentiation tool](https://auto-differentation.github.io).

Useful links:

-   [QuantLib Documentation](https://www.quantlib.org)
-   [XAD Documentation, incl Python bindings and QuantLib integration](https://auto-differentiation.github.io)

## Installation

```
pip install quantlib-risks
```

## Usage Illustration

```python
import quantlib_risks as ql
from xad_autodiff.adj_1st import Tape

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
