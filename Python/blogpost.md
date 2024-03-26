# Introducing QuantLib-Risks: Enhancing Risk Analysis with Automatic Differentiation

The Python ecosystem has recently been enriched with a notable addition, [QuantLib-Risks](https://pypi.org/project/QuantLib-Risks), a fork of the QuantLib Python bindings, now available on PyPI. This version integrates automatic differentiation capabilities through its dependency on [xad-autodiff](https://pypi.org/project/xad-autodiff), also a newcomer to PyPI. This integration significantly boosts the efficiency of performing high-performance risk assessments within QuantLib.

The key advantage brought by QuantLib-Risks is its ability to expediently ascertain how the pricing of derivatives is influenced by various input variables, notably market quotes.

In this post, we will delve into the application of QuantLib-Risks in the context of pricing swaps and scrutinising the sensitivities of market quotes crucial for curve bootstrapping.

## Setting the Stage for Swap Pricing

Our journey begins with the standard [swap pricing example](https://github.com/lballabio/QuantLib-SWIG/blob/v1.33/Python/examples/swap.py) found within QuantLib's Python bindings. This foundational example constructs a financial landscape through a series of market quotes encompassing deposits, FRAs, futures, and swap rates, serving as the building blocks for bootstrapping two distinct curves: `depoFuturesSwapCurve` and `depoFraSwapCurve`. The former curve is built from deposit, future, and swap rate quotes, while the latter emerges from deposits, FRAs, and swap rate quotes.

Upon this groundwork, we construct and price two types of swaps: a `spot` swap, extending over five years from the spot date, and a `forward` swap, also spanning five years but commencing one year into the future. The output from this example is summarised in the following table:

<div align="center">

|Swap | Curve | NPV |
|-----|-------|-----|
| `spot` | `depoFuturesSwapCurve` | 19,066.26 |
| `spot` | `depoFraSwapCurve` | 19,066.26 |
| `forward` | `depoFuturesSwapCurve` | 40,533.04 |
| `forward` | `depoFraSwapCurve` | 37,144.28 |

</div>

## Sensitivity Analysis

To discern how market quotes influence prices, we employ sensitivity analysis. This method not only identifies the impact of market parameters on prices but also aids in crafting hedges to balance overall portfolio risks. The full example demonstrating this analysis is available on [GitHub](https://github.com/auto-differentiation/QuantLib-Risks/blob/v1.33/Python/examples/swap-adjoint.py).

### Required Modules

The analysis requires the  [QuantLib-Risks Python package](https://pypi.org/project/QuantLib-Risks), a drop-in enhancement of the standard `QuantLib` package. This package, along with an adjoint tape for recording derivatives, is essential for our sensitivity analysis. Setup for these imports and the tape is outlined as follows:

```python
import QuantLib_Risks as ql
from xad_autodiff.adj_1st import Tape

# create and activate tape
tape = Tape()
tape.activate()
```

### Input Variables

In `QuantLib-Risks`, the numeric data types capable of being recorded on an adjoint automatic differentiation tape
is `ql.Real` (and alias to [xad-autodiff's](https://pypi.org/project/xad-autodiff) `adj_1st.Real` data type). 
This active type replaces standard `float` values for the independent variables in our sensitivity analysis. Initially, market quotes are stored in dictionaries, with `float` values later converted to `ql.SimpleQuote` instances. To maintain reference to original inputs, we rename the input dictionary from `futures` to `futures_in` and similarly for other quote types, ensuring all independent variables are registered with the tape. 

The setup for futures, as an example, is detailed here:

```python
futures_in = {
    ql.Date(19, 12, 2001): ql.Real(96.2875),
    ql.Date(20, 3, 2002):  ql.Real(96.7875),
    ql.Date(19, 6, 2002):  ql.Real(96.9875),
    ql.Date(18, 9, 2002):  ql.Real(96.6875),
    ql.Date(18, 12, 2002): ql.Real(96.4875),
    ql.Date(19, 3, 2003):  ql.Real(96.3875),
    ql.Date(18, 6, 2003):  ql.Real(96.2875),
    ql.Date(17, 9, 2003):  ql.Real(96.0875),
}
tape.registerInputs(futures_in.values())
```

### Calculations

Before commencing calculations, we activate the tape to record derivatives:

```python
tape.newRecording()
```

The remainder of the calculation process, including quotes, curve, and swap setup, remains unchanged.

### Determine Price and Sensitivities

To calculate mathematical derivatives, we follow these steps:

1. Compute the NPV as usual.
2. Register the NPV as an output with the tape (`tape.registerOutput()`).
3. Seed the output's adjoint (`v.derivative = 1.0`).
4. Roll back the tape to propagate output adjoints back to inputs (`tape.computeAdjoints()`).
5. Read adjoints of the inputs (`input_value.derivate` property) to obtain mathematical derivatives.

We focus on sensitivities as finite shifts in inputs, like a 1 basis point shift in interest rate quotes. These can be calculated by multiplying the derivatives by the desired shifts. The process is exemplified in the modified `show` function:

```python
def show(swap):
    
    npv = swap.NPV()         # calculate NPV value
    tape.registerOutput(npv) # register output
    tape.clearDerivatives()  # clear previous derivatives (to allow multiple calls)
    npv.derivative = 1.0     # seed output adjoint
    tape.computeAdjoints()   # roll back the tape to calculate input adjoints
    
    print("NPV         = {:.2f}".format(v))
    print("Fair spread = {:.4f} %".format(swap.fairSpread()*100))
    print("Fair rate   = {:.4f} %".format(swap.fairRate()*100))

    print("\nSensitivities to deposit quotes, 1bp shift:")
    for k, v in deposits_in.items():
        print(f"  {ql.Period(k[0], k[1])}: {v.derivative * 0.0001:.2f}")
    print("Sensitivities to FRA quotes, 1bp shift:")
    for k, v in FRAs_in.items():
        print(f"  {k[0]}M - {k[1]}M: {v.derivative * 0.0001:.2f}")
    print("Sensitivities to futures quotes, 1c shift:")
    for k, v in futures_in.items():
        print(f"  {k}: {v.derivative * 0.01:.2f}")
    print("Sensitivities to swap rate quotes, 1bp shift:")
    for k, v in swaps_in.items():
        print(f"  {ql.Period(k[0], k[1])}: {v.derivative * 0.0001:.2f}")
```

### Results

By employing the `show` function for both swap types across the two different curves, we can first confirm that the NPV, fair spread, and fair rate values match the original sample. 

Our analysis of sensitivities reveals:

- **5-Year Spot Swap on Deposit/Futures/Swap Curve**: Only the 5-year swap rate quote affects this swap's price, with other quotes having no impact. A 1 basis point shift in the 5Y swap rate results in a price change of 443.4. This is expected due to the direct use of this rate in curve construction.

```text
NPV         = 19066.26
Fair spread = -0.4174 %
Fair rate   = 4.4300 %

Sensitivities to deposit quotes, 1bp shift:
  3M: -0.00
Sensitivities to FRA quotes, 1bp shift:
  3M - 6M: 0.00
  6M - 9M: 0.00
  9M - 12M: 0.00
Sensitivities to futures quotes, 1c shift:
  December 19th, 2001: 0.00
  March 20th, 2002: 0.00
  June 19th, 2002: 0.00
  September 18th, 2002: 0.00
  December 18th, 2002: 0.00
  March 19th, 2003: 0.00
  June 18th, 2003: -0.00
  September 17th, 2003: 0.00
Sensitivities to swap rate quotes, 1bp shift:
  2Y: 0.00
  3Y: -0.00
  5Y: 443.40
  10Y: 0.00
  15Y: 0.00
```
  
- **5-Year Spot Swap on Deposit/FRA/Swap Curve**: This is pricing the same 5-year spot swap on a different curve, which  includes the same 5Y swap rate quote. Sensitivities for all quotes except the 5Y swap rate are zero, as anticipated, and the price is identical.

```text
NPV         = 19066.26
Fair spread = -0.4174 %
Fair rate   = 4.4300 %

Sensitivities to deposit quotes, 1bp shift:
  3M: -0.00
Sensitivities to FRA quotes, 1bp shift:
  3M - 6M: -0.00
  6M - 9M: -0.00
  9M - 12M: -0.00
Sensitivities to futures quotes, 1c shift:
  December 19th, 2001: 0.00
  March 20th, 2002: 0.00
  June 19th, 2002: 0.00
  September 18th, 2002: 0.00
  December 18th, 2002: 0.00
  March 19th, 2003: 0.00
  June 18th, 2003: 0.00
  September 17th, 2003: 0.00
Sensitivities to swap rate quotes, 1bp shift:
  2Y: -0.00
  3Y: 0.00
  5Y: 443.40
  10Y: 0.00
  15Y: 0.00
```

- **1-Year Forward-Starting Swap on Deposit/Futures/Swap Curve**: Recall that the that pricing date is 6 November 2001 and this swap starts in November 2002, maturing in November 2007. The sensitivities show dependencies on 3M deposit and future rates up to one year from the pricing date, which determine the rate at the time the swap starts. We see a further dependency on both the 5-year and 10-year swap rates, as the swap's maturity falls between these 2 rates. We see no dependency on FRA quotes, as they are not part of the curve.

```text
NPV         = 40533.04
Fair spread = -0.9241 %
Fair rate   = 4.9520 %

Sensitivities to deposit quotes, 1bp shift:
  3M: -11.42
Sensitivities to FRA quotes, 1bp shift:
  3M - 6M: 0.00
  6M - 9M: 0.00
  9M - 12M: 0.00
Sensitivities to futures quotes, 1c shift:
  December 19th, 2001: 24.49
  March 20th, 2002: 24.94
  June 19th, 2002: 24.53
  September 18th, 2002: 13.48
  December 18th, 2002: 0.00
  March 19th, 2003: -0.00
  June 18th, 2003: 0.00
  September 17th, 2003: 0.00
Sensitivities to swap rate quotes, 1bp shift:
  2Y: 0.00
  3Y: -0.00
  5Y: 347.43
  10Y: 174.31
  15Y: 0.00
```
  
- **1-Year Forward-Starting Swap on Deposit/FRA/Swap Curve**: Displays dependencies similar to the previous curve but relies on FRA quotes instead of futures, with sensitivities matching the previous curve for the 5-year and 10-year swap rates.

```text
NPV         = 37144.28
Fair spread = -0.8469 %
Fair rate   = 4.8724 %

Sensitivities to deposit quotes, 1bp shift:
  3M: -25.30
Sensitivities to FRA quotes, 1bp shift:
  3M - 6M: -24.23
  6M - 9M: -27.69
  9M - 12M: -21.64
Sensitivities to futures quotes, 1c shift:
  December 19th, 2001: 0.00
  March 20th, 2002: 0.00
  June 19th, 2002: 0.00
  September 18th, 2002: 0.00
  December 18th, 2002: 0.00
  March 19th, 2003: 0.00
  June 18th, 2003: 0.00
  September 17th, 2003: 0.00
Sensitivities to swap rate quotes, 1bp shift:
  2Y: -0.00
  3Y: -0.00
  5Y: 347.43
  10Y: 174.31
  15Y: 0.00
```

## Performance Evaluation

To gauge the performance impact of calculating sensitivities, we leverage the [multi-curve bootstrapping example](https://github.com/auto-differentiation/QuantLib-Risks/blob/v1.33/Python/examples/multicurve-bootstrapping.py). This setup, while similar to our earlier discussion, incorporates a wider array of quotes to construct the term structure for swap pricing. A notable scenario involves pricing a forward-starting 5-year swap, set to commence 15 months into the future, with a calculation of 69 sensitivities covering all market quotes used in curve construction and select swap parameters like nominal, fixed rate, and spread.

Performance metrics are drawn from averaging execution times over 20 runs for stability. Initial benchmarks using the standard QuantLib package clock in at 198ms for pricing alone. Switching to `QuantLib-Risks` for simultaneous pricing and sensitivity analysis results in an execution time of 370ms, demonstrating that *all sensitivities can be obtained within approximately 1.87x of the original pricing time*.

Comparatively, a traditional bump-and-reval approach for sensitivities would necessitate 70 pricer code executions (one for valuation and one for each variable bump), translating to 70x the pure pricing time. *Thus, `QuantLib-Risks` achieves a 37.4x speed advantage over bump and reval*.

Summary of performance benchmarks:

| Sensitivities | Valuation (QuantLib) | AAD (QuantLib-Risks) | Bumping (estimate) | AAD vs Valuation | Bumping vs AAD |
|---:|---:|---:|---:|---:|---:|
| 69 | 198ms | 370ms | 13,860ms | 1.87x | 37.4x |

Benchmark configuration details include:
- `QuantLib` and `QuantLib-Risks` version: 1.33
- `xad-autodiff` version: 1.5.0
- Operating on Ubuntu 22.04 with GCC 11.4.0
- Hardware specs include 128GB RAM and an Intel(R) Xeon(R) W-2295 CPU @ 3.00GHz.

## Do You Want to Try?

Interested in diving into these examples yourself? The code for both samples is readily accessible on [GitHub](https://github.com/auto-differentiation/QuantLib-Risks/blob/master/Python/examples/). For an interactive experience, you can test the examples in an [online notebook using binder](https://mybinder.org/v2/gh/auto-differentiation/QuantLib-Risks/binder?urlpath=lab/tree/Python/examples) — make sure to right-click on the desired example and open it with Jupyter.

To run the examples locally, you can install `QuantLib-Risks` using pip as:

```text
pip install QuantLib-Risks
```


For further insights and documentation, visit the [official documentation page](https://auto-differentiation.github.io/quantlib).