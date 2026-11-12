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
# # American options with sensitivities
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
# This is a port of the `AdjointAmericanEquityOption` C++ example.  It prices
# an American put option with the finite-difference Black-Scholes engine and
# computes the sensitivities of the price to the risk-free rate, the strike,
# the volatility, the underlying, and the dividend yield in a single adjoint
# pass.  The results are cross-checked against bump-and-reprice finite
# differences.
#
# One caveat, also present in the C++ example: the FD engine builds its
# operator from the dividend yield as a plain value, so the adjoint dividend
# rho comes out as (numerically) zero even though bumping the yield does move
# the price.  The other four sensitivities match the bumped values closely.

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
# ### Market data and option inputs

# %%
riskFreeRate_in = ql.Real(0.06)
strike_in = ql.Real(40.0)
volatility_in = ql.Real(0.20)
underlying_in = ql.Real(36.0)
dividendYield_in = ql.Real(0.00)

tape.registerInput(riskFreeRate_in)
tape.registerInput(strike_in)
tape.registerInput(volatility_in)
tape.registerInput(underlying_in)
tape.registerInput(dividendYield_in)


# %% [markdown]
# ### Pricing
#
# The option and its engine are built inside the recording, so that they are
# constructed from the registered inputs.


# %%
def priceAmerican(riskFreeRate, strike, volatility, underlying, dividendYield):
    termStructure = ql.FlatForward(settlementDate, riskFreeRate, dayCounter)
    dividendTS = ql.FlatForward(settlementDate, dividendYield, dayCounter)
    volTS = ql.BlackConstantVol(settlementDate, calendar, volatility, dayCounter)
    process = ql.BlackScholesMertonProcess(
        ql.QuoteHandle(ql.SimpleQuote(underlying)),
        ql.YieldTermStructureHandle(dividendTS),
        ql.YieldTermStructureHandle(termStructure),
        ql.BlackVolTermStructureHandle(volTS),
    )
    option = ql.VanillaOption(
        ql.PlainVanillaPayoff(ql.Option.Put, strike),
        ql.AmericanExercise(settlementDate, maturity),
    )
    timeSteps = 801
    option.setPricingEngine(
        ql.FdBlackScholesVanillaEngine(process, timeSteps, timeSteps - 1)
    )
    return option.NPV()


# %%
tape.newRecording()
optionValue = priceAmerican(
    riskFreeRate_in, strike_in, volatility_in, underlying_in, dividendYield_in
)

tape.registerOutput(optionValue)
optionValue.derivative = 1.0
tape.computeAdjoints()

print(f"American option value: {optionValue:.10f}")

# %% [markdown]
# ### Greeks

# %%
greeks = [
    ("Rho", riskFreeRate_in.derivative),
    ("Strike sensitivity", strike_in.derivative),
    ("Vega", volatility_in.derivative),
    ("Delta", underlying_in.derivative),
    ("Dividend rho", dividendYield_in.derivative),
]

# %%
df = pd.DataFrame(greeks, columns=["Greek", "Value"])
df.style.hide(axis="index")

# %%
if not interactive:
    print(df.to_string(index=False))

# %% [markdown]
# ### Cross-check by bumping
#
# Each input is bumped in turn and the option repriced without the tape.
# Four of the five finite differences match the adjoints; the dividend rho
# does not, for the reason given at the top of this example.

# %%
eps = 1e-5
base = [
    value(riskFreeRate_in),
    value(strike_in),
    value(volatility_in),
    value(underlying_in),
    value(dividendYield_in),
]
checks = []
for i, (name, adjoint) in enumerate(greeks):
    bumped = list(base)
    bumped[i] += eps
    fd = (
        value(priceAmerican(*[ql.Real(v) for v in bumped])) - value(optionValue)
    ) / eps
    checks.append((name, adjoint, fd))

# %%
checkDf = pd.DataFrame(checks, columns=["Greek", "Adjoint", "Bump and reprice"])
checkDf.style.hide(axis="index")

# %%
if not interactive:
    print(checkDf.to_string(index=False))

# %%
tape.deactivate()
