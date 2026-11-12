# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # European options with sensitivities
#
# Copyright (&copy;) 2004, 2005, 2006, 2007 StatPro Italia srl
# Copyright (&copy;) 2024 Xcelerit Computing Limited.
#
# This file is part of QuantLibAAD, a Python wrapper for QuantLib enabled
# for risk computation using automatic differentiation. It uses XAD,
# a fast and comprehensive C++ library for automatic differentiation.
#
# QuantLibAAD and XAD are free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QuantLibAAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# QuantLib is free software: you can redistribute it and/or modify it under the
# terms of the QuantLib license.  You should have received a copy of the
# license along with this program; if not, please email
# <quantlib-dev@lists.sf.net>. The license is also available online at
# <https://www.quantlib.org/license.shtml>.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the license for more details.

# %% [markdown]
# This is a port of the `AdjointEuropeanEquityOption` C++ example.  It prices
# a portfolio of European put options (several underlyings, each with a range
# of strikes) over a zero curve and a black variance curve, and computes the
# sensitivities of the total portfolio value to all market inputs (the zero
# rates, the volatilities, the strikes, the underlyings, and the dividend
# yield) in a single adjoint pass.  The results are cross-checked against
# bump-and-reprice finite differences.

# %%
import QuantLibAAD as ql
from xad.adj_1st import Tape
from xad import value
import pandas as pd

# %% [markdown]
# ### Global parameters

# %%
calendar = ql.TARGET()
todaysDate = ql.Date(15, ql.May, 1998)
settlementDate = ql.Date(17, ql.May, 1998)
ql.Settings.instance().evaluationDate = todaysDate
dayCounter = ql.Actual365Fixed()
maturity = ql.Date(17, ql.May, 1999)

# setup and activate the tape
tape = Tape()
tape.activate()

# %%
interactive = "get_ipython" in globals()

# %% [markdown]
# ### Market data
#
# The zero curve and the variance curve share the same node dates: the
# settlement date plus the offsets below.  The first rate is repeated at the
# first offset date, as in the C++ example.

# %%
offsets = [13, 41, 75, 165, 256, 345, 524, 703]
curveRates = [0.0357, 0.0349, 0.0341, 0.0355, 0.0359, 0.0368, 0.0386, 0.0401]
curveVols = [0.20, 0.18, 0.178, 0.183, 0.192, 0.203, 0.215, 0.208]

dates = [settlementDate] + [settlementDate + n for n in offsets]

rates_in = [ql.Real(curveRates[0])] + [ql.Real(r) for r in curveRates]
vols_in = [ql.Real(v) for v in curveVols]
strikes_in = [ql.Real(float(s)) for s in range(10, 80)]
underlyings_in = [ql.Real(float(s)) for s in range(15, 61, 5)]
dividendYield_in = ql.Real(0.01)

tape.registerInputs(rates_in)
tape.registerInputs(vols_in)
tape.registerInputs(strikes_in)
tape.registerInputs(underlyings_in)
tape.registerInput(dividendYield_in)


# %% [markdown]
# ### Pricing
#
# The whole portfolio is priced inside the recording, so that the curves and
# instruments are built from the registered inputs.


# %%
def pricePortfolio(rates, vols, strikes, underlyings, dividendYield):
    termStructure = ql.ZeroCurve(dates, rates, dayCounter)
    dividendTS = ql.FlatForward(settlementDate, dividendYield, dayCounter)
    # the variance curve drops the first (settlement) date
    volTS = ql.BlackVarianceCurve(settlementDate, dates[1:], vols, dayCounter)

    exercise = ql.EuropeanExercise(maturity)
    value = ql.Real(0.0)
    for underlying in underlyings:
        process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(ql.SimpleQuote(underlying)),
            ql.YieldTermStructureHandle(dividendTS),
            ql.YieldTermStructureHandle(termStructure),
            ql.BlackVolTermStructureHandle(volTS),
        )
        engine = ql.AnalyticEuropeanEngine(process)
        for strike in strikes:
            option = ql.VanillaOption(
                ql.PlainVanillaPayoff(ql.Option.Put, strike), exercise
            )
            option.setPricingEngine(engine)
            value = value + option.NPV()
    return value


# %%
tape.newRecording()
portfolioValue = pricePortfolio(
    rates_in, vols_in, strikes_in, underlyings_in, dividendYield_in
)

tape.registerOutput(portfolioValue)
portfolioValue.derivative = 1.0
tape.computeAdjoints()

print(f"Portfolio value: {portfolioValue:.5f}")

# %% [markdown]
# ### Sensitivities

# %%
results = []
for d, rate in zip(dates, rates_in):
    results.append(("rho", f"rate {d}", rate.derivative))
for d, vol in zip(dates[1:], vols_in):
    results.append(("vega", f"vol {d}", vol.derivative))
for strike in strikes_in:
    results.append(("strike sensitivity", f"strike {value(strike):.0f}", strike.derivative))
for underlying in underlyings_in:
    results.append(("delta", f"underlying {value(underlying):.0f}", underlying.derivative))
results.append(("dividend rho", "dividend yield", dividendYield_in.derivative))

# %%
df = pd.DataFrame(results, columns=["Sensitivity", "Input", "Value"])
df.style.hide(axis="index")

# %%
if not interactive:
    print(df.to_string(index=False))

# %% [markdown]
# ### Cross-check by bumping
#
# Each input is bumped in turn and the portfolio repriced without the tape;
# the finite differences should match the adjoints above.  Only the largest
# sensitivities are shown.

# %%
eps = 1e-5


def bumpedValue(which, index):
    rates = [value(r) for r in rates_in]
    vols = [value(v) for v in vols_in]
    strikes = [value(s) for s in strikes_in]
    underlyings = [value(u) for u in underlyings_in]
    dividendYield = value(dividendYield_in)
    if which == "rate":
        rates[index] += eps
    elif which == "vol":
        vols[index] += eps
    elif which == "strike":
        strikes[index] += eps
    elif which == "underlying":
        underlyings[index] += eps
    else:
        dividendYield += eps
    return pricePortfolio(
        [ql.Real(r) for r in rates],
        [ql.Real(v) for v in vols],
        [ql.Real(s) for s in strikes],
        [ql.Real(u) for u in underlyings],
        ql.Real(dividendYield),
    )


# %%
checks = []
named = (
    [("rate", i, f"rate {dates[i]}", r.derivative) for i, r in enumerate(rates_in)]
    + [("vol", i, f"vol {dates[i + 1]}", v.derivative) for i, v in enumerate(vols_in)]
    + [("strike", i, f"strike {value(s):.0f}", s.derivative) for i, s in enumerate(strikes_in)]
    + [("underlying", i, f"underlying {value(u):.0f}", u.derivative) for i, u in enumerate(underlyings_in)]
    + [("dividend", 0, "dividend yield", dividendYield_in.derivative)]
)
for which, index, name, adjoint in sorted(named, key=lambda t: -abs(t[3]))[:8]:
    fd = (bumpedValue(which, index) - value(portfolioValue)) / eps
    checks.append((name, adjoint, fd))

# %%
checkDf = pd.DataFrame(checks, columns=["Input", "Adjoint", "Bump and reprice"])
checkDf.style.hide(axis="index")

# %%
if not interactive:
    print(checkDf.to_string(index=False))

# %%
tape.deactivate()
