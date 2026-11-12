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
# # Static replication of a barrier option, with sensitivities
#
# Copyright (&copy;) 2023 Xcelerit Computing Limited.
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
# This is a port of the `AdjointReplication` C++ example, which follows the
# static replication of a down-and-out barrier option with European options
# from M. Joshi, *The Concepts and Practice of Mathematical Finance*,
# chapter 17.  A portfolio is built that matches the barrier option's payoff
# on a set of points along the barrier: it starts from a put struck at the
# option's strike, a digital put and a put struck at the barrier, and then
# successively adds puts expiring at earlier dates whose notionals are chosen
# to make the portfolio worthless whenever the underlying touches the barrier
# at those dates.  Because the notionals are computed from portfolio values
# during the construction, the whole build is recorded on the tape, and the
# sensitivities of the final portfolio value to the zero rates, the strike,
# the volatility, the underlying, and the barrier level come out of a single
# adjoint pass.  The results are cross-checked against bump-and-reprice
# finite differences.
#
# One difference from the C++ code: there, a single variable holds the flat
# 4% rate used at every curve node, so its adjoint accumulates the sum of the
# per-node sensitivities.  Here each node gets its own input (all set to
# 4%), so the rhos are reported per node; their sum is the corresponding
# single-variable sensitivity.

# %%
import QuantLibAAD as ql
from xad.adj_1st import Tape
from xad import value
import pandas as pd

# %% [markdown]
# ### Global parameters

# %%
todaysDate = ql.Date(29, ql.May, 2006)
ql.Settings.instance().evaluationDate = todaysDate
dayCounter = ql.Actual365Fixed()
maturity = todaysDate + ql.Period(1, ql.Years)

# the zero curve dates: today plus these offsets in days
offsets = [13, 41, 75, 165, 256, 345, 524, 703]
dates = [todaysDate] + [todaysDate + n for n in offsets]

# setup and activate the tape
tape = Tape()
tape.activate()

# %%
interactive = "get_ipython" in globals()

# %% [markdown]
# ### Inputs
#
# The option to replicate is a down-and-out put with strike 101 and barrier
# 70 on an underlying at 100, with volatility 0.20 and a flat 4% zero curve.

# %%
rates_in = [ql.Real(0.04) for _ in dates]
strike_in = ql.Real(101.0)
volatility_in = ql.Real(0.20)
underlying_in = ql.Real(100.0)
barrier_in = ql.Real(70.0)
rebate = 0.0

tape.registerInputs(rates_in)
tape.registerInput(strike_in)
tape.registerInput(volatility_in)
tape.registerInput(underlying_in)
tape.registerInput(barrier_in)


# %% [markdown]
# ### The reference barrier option


# %%
def priceBarrierOption(rates, strike, volatility, underlying, barrier):
    termStructure = ql.ZeroCurve(dates, rates, dayCounter)
    volTS = ql.BlackConstantVol(
        0, ql.NullCalendar(), ql.QuoteHandle(ql.SimpleQuote(volatility)), dayCounter
    )
    process = ql.BlackScholesProcess(
        ql.QuoteHandle(ql.SimpleQuote(underlying)),
        ql.YieldTermStructureHandle(termStructure),
        ql.BlackVolTermStructureHandle(volTS),
    )
    option = ql.BarrierOption(
        ql.Barrier.DownOut,
        barrier,
        rebate,
        ql.PlainVanillaPayoff(ql.Option.Put, strike),
        ql.EuropeanExercise(maturity),
    )
    option.setPricingEngine(ql.AnalyticBarrierEngine(process))
    return option.NPV()


# %% [markdown]
# ### The replicating portfolio
#
# The kill loop runs over 26 fortnightly dates (B = 26 blocks of t = 2
# weeks).  Each iteration values the current portfolio and the new put with
# the evaluation date moved to the previous kill date and the underlying set
# to the barrier, then subtracts the put with the notional that makes the
# portfolio worthless at that point.


# %%
def pricePortfolio(rates, strike, volatility, underlying, barrier):
    termStructure = ql.ZeroCurve(dates, rates, dayCounter)
    volTS = ql.BlackConstantVol(
        0, ql.NullCalendar(), ql.QuoteHandle(ql.SimpleQuote(volatility)), dayCounter
    )
    underlyingQuote = ql.SimpleQuote(underlying)
    process = ql.BlackScholesProcess(
        ql.QuoteHandle(underlyingQuote),
        ql.YieldTermStructureHandle(termStructure),
        ql.BlackVolTermStructureHandle(volTS),
    )
    engine = ql.AnalyticEuropeanEngine(process)
    exercise = ql.EuropeanExercise(maturity)
    payoff = ql.PlainVanillaPayoff(ql.Option.Put, strike)

    portfolio = ql.CompositeInstrument()
    # final payoff first, as shown in Joshi: a put struck at K...
    put = ql.EuropeanOption(payoff, exercise)
    put.setPricingEngine(engine)
    portfolio.add(put)
    # ...minus a digital put struck at B of notional K-B...
    digitalPut = ql.EuropeanOption(
        ql.CashOrNothingPayoff(ql.Option.Put, barrier, 1.0), exercise
    )
    digitalPut.setPricingEngine(engine)
    portfolio.subtract(digitalPut, strike - barrier)
    # ...minus a put struck at B.
    lowerPut = ql.EuropeanOption(
        ql.PlainVanillaPayoff(ql.Option.Put, barrier), exercise
    )
    lowerPut.setPricingEngine(engine)
    portfolio.subtract(lowerPut)

    # now use puts struck at B to kill the value of the portfolio
    # on a number of points (B, t)
    B = 26  # number of dates
    t = 2  # spacing of the dates, in weeks
    for i in range(B * t, t - 1, -t):
        innerExercise = ql.EuropeanExercise(todaysDate + ql.Period(i, ql.Weeks))
        innerPut = ql.EuropeanOption(
            ql.PlainVanillaPayoff(ql.Option.Put, barrier), innerExercise
        )
        innerPut.setPricingEngine(engine)
        # evaluate the current portfolio and the latest put at (B, t)...
        killDate = todaysDate + ql.Period(i - t, ql.Weeks)
        ql.Settings.instance().evaluationDate = killDate
        underlyingQuote.setValue(barrier)
        portfolioValue = portfolio.NPV()
        putValue = innerPut.NPV()
        # ...and subtract the put with the notional that kills the value
        portfolio.subtract(innerPut, portfolioValue / putValue)

    ql.Settings.instance().evaluationDate = todaysDate
    underlyingQuote.setValue(underlying)
    return portfolio.NPV()


# %%
tape.newRecording()
barrierValue = priceBarrierOption(
    rates_in, strike_in, volatility_in, underlying_in, barrier_in
)
portfolioValue = pricePortfolio(
    rates_in, strike_in, volatility_in, underlying_in, barrier_in
)

tape.registerOutput(portfolioValue)
portfolioValue.derivative = 1.0
tape.computeAdjoints()

print(f"Original barrier option value: {value(barrierValue):.15f}")
print(f"Replicating portfolio value  : {value(portfolioValue):.15f}")

# %% [markdown]
# ### Sensitivities of the replicating portfolio

# %%
sensitivities = [("rho", f"rate {d}", r.derivative) for d, r in zip(dates, rates_in)]
sensitivities += [
    ("strike sensitivity", "strike", strike_in.derivative),
    ("vega", "volatility", volatility_in.derivative),
    ("delta", "underlying", underlying_in.derivative),
    ("barrier sensitivity", "barrier", barrier_in.derivative),
]

# %%
df = pd.DataFrame(sensitivities, columns=["Sensitivity", "Input", "Value"])
df.style.hide(axis="index")

# %%
if not interactive:
    print(df.to_string(index=False))

# %% [markdown]
# ### Cross-check by bumping
#
# Each input is bumped in turn and the portfolio rebuilt and repriced without
# the tape; the finite differences should match the adjoints above.

# %%
eps = 1e-5


def bumpedValue(which, index):
    rates = [value(r) for r in rates_in]
    strike = value(strike_in)
    volatility = value(volatility_in)
    underlying = value(underlying_in)
    barrier = value(barrier_in)
    if which == "rate":
        rates[index] += eps
    elif which == "strike":
        strike += eps
    elif which == "volatility":
        volatility += eps
    elif which == "underlying":
        underlying += eps
    else:
        barrier += eps
    return value(
        pricePortfolio(
            [ql.Real(r) for r in rates],
            ql.Real(strike),
            ql.Real(volatility),
            ql.Real(underlying),
            ql.Real(barrier),
        )
    )


# %%
checks = [
    ("rate", i, f"rate {d}", r.derivative) for i, (d, r) in enumerate(zip(dates, rates_in))
] + [
    ("strike", 0, "strike", strike_in.derivative),
    ("volatility", 0, "volatility", volatility_in.derivative),
    ("underlying", 0, "underlying", underlying_in.derivative),
    ("barrier", 0, "barrier", barrier_in.derivative),
]
checkRows = [
    (name, adjoint, (bumpedValue(which, index) - value(portfolioValue)) / eps)
    for which, index, name, adjoint in checks
]

# %%
checkDf = pd.DataFrame(checkRows, columns=["Input", "Adjoint", "Bump and reprice"])
checkDf.style.hide(axis="index")

# %%
if not interactive:
    print(checkDf.to_string(index=False))

# %%
tape.deactivate()
