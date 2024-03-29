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
# # Interest-rate swaps
#
# Copyright (&copy;) 2004, 2005, 2006, 2007 StatPro Italia srl<br>
# Copyright (&copy;) 2024 Xcelerit Computing Limited.
#
# This file is part of QuantLib-Risks, a Python wrapper for QuantLib enabled
# for risk computation using automatic differentiation. It uses XAD,
# a fast and comprehensive C++ library for automatic differentiation.
#
# QuantLib-Risks and XAD are free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QuantLib-Risks is distributed in the hope that it will be useful,
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

# %%
import QuantLib_Risks as ql
from xad_autodiff.adj_1st import Tape

# %% [markdown]
# ### Global data

# %%
calendar = ql.TARGET()
todaysDate = ql.Date(6, ql.November, 2001)
ql.Settings.instance().evaluationDate = todaysDate
settlementDate = ql.Date(8, ql.November, 2001)

# setup and activate the tape
tape = Tape()
tape.activate()

# %% [markdown]
# ### Market quotes

# %%
deposits_in = {
    (3, ql.Months): ql.Real(0.0363),
}
tape.registerInputs(deposits_in.values())


# %%
FRAs_in = {(3, 6): ql.Real(0.037125), (6, 9): ql.Real(0.037125), (9, 12): ql.Real(0.037125)}
tape.registerInputs(FRAs_in.values())

# %%
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

# %%
swaps_in = {
    (2, ql.Years):  ql.Real(0.037125),
    (3, ql.Years):  ql.Real(0.0398),
    (5, ql.Years):  ql.Real(0.0443),
    (10, ql.Years): ql.Real(0.05165),
    (15, ql.Years): ql.Real(0.055175),
}
tape.registerInputs(swaps_in.values())

tape.newRecording()
# %% [markdown]
# We'll convert them to `Quote` objects...

# %%
deposits = dict()
for n, unit in deposits_in.keys():
    deposits[(n, unit)] = ql.SimpleQuote(deposits_in[(n, unit)])
FRAs = dict()
for n, m in FRAs_in.keys():
    FRAs[(n, m)] = ql.SimpleQuote(FRAs_in[(n, m)])
futures = dict()
for d in futures_in.keys():
    futures[d] = ql.SimpleQuote(futures_in[d])
swaps = dict()
for n, unit in swaps_in.keys():
    swaps[(n, unit)] = ql.SimpleQuote(swaps_in[(n, unit)])

# %% [markdown]
# ...and build rate helpers.

# %%
dayCounter = ql.Actual360()
settlementDays = 2
depositHelpers = [
    ql.DepositRateHelper(
        ql.QuoteHandle(deposits[(n, unit)]),
        ql.Period(n, unit),
        settlementDays,
        calendar,
        ql.ModifiedFollowing,
        False,
        dayCounter,
    )
    for n, unit in deposits.keys()
]

# %%
dayCounter = ql.Actual360()
settlementDays = 2
fraHelpers = [
    ql.FraRateHelper(
        ql.QuoteHandle(FRAs[(n, m)]), n, m, settlementDays, calendar, ql.ModifiedFollowing, False, dayCounter
    )
    for n, m in FRAs.keys()
]

# %%
dayCounter = ql.Actual360()
months = 3
futuresHelpers = [
    ql.FuturesRateHelper(
        ql.QuoteHandle(futures[d]),
        d,
        months,
        calendar,
        ql.ModifiedFollowing,
        True,
        dayCounter,
        ql.QuoteHandle(ql.SimpleQuote(0.0)),
    )
    for d in futures.keys()
]

# %% [markdown]
# The discount curve for the swaps will come from elsewhere. A real application would use some kind of risk-free curve; here we're using a flat one for convenience.

# %%
discountTermStructure = ql.YieldTermStructureHandle(
    ql.FlatForward(settlementDate, 0.04, ql.Actual360()))

# %%
settlementDays = 2
fixedLegFrequency = ql.Annual
fixedLegTenor = ql.Period(1, ql.Years)
fixedLegAdjustment = ql.Unadjusted
fixedLegDayCounter = ql.Thirty360(ql.Thirty360.BondBasis)
floatingLegFrequency = ql.Quarterly
floatingLegTenor = ql.Period(3, ql.Months)
floatingLegAdjustment = ql.ModifiedFollowing
swapHelpers = [
    ql.SwapRateHelper(
        ql.QuoteHandle(swaps[(n, unit)]),
        ql.Period(n, unit),
        calendar,
        fixedLegFrequency,
        fixedLegAdjustment,
        fixedLegDayCounter,
        ql.Euribor3M(),
        ql.QuoteHandle(),
        ql.Period("0D"),
        discountTermStructure,
    )
    for n, unit in swaps.keys()
]

# %% [markdown]
# ### Term structure construction

# %%
forecastTermStructure = ql.RelinkableYieldTermStructureHandle()

# %%
helpers = depositHelpers + futuresHelpers + swapHelpers[1:]
depoFuturesSwapCurve = ql.PiecewiseFlatForward(settlementDate, helpers, ql.Actual360())

# %%
helpers = depositHelpers + fraHelpers + swapHelpers
depoFraSwapCurve = ql.PiecewiseFlatForward(settlementDate, helpers, ql.Actual360())

# %% [markdown]
# ### Swap pricing

# %%
swapEngine = ql.DiscountingSwapEngine(discountTermStructure)

# %%
nominal = 1000000
length = 5
maturity = calendar.advance(settlementDate, length, ql.Years)
payFixed = True

# %%
fixedLegFrequency = ql.Annual
fixedLegAdjustment = ql.Unadjusted
fixedLegDayCounter = ql.Thirty360(ql.Thirty360.BondBasis)
fixedRate = 0.04

# %%
floatingLegFrequency = ql.Quarterly
spread = 0.0
fixingDays = 2
index = ql.Euribor3M(forecastTermStructure)
floatingLegAdjustment = ql.ModifiedFollowing
floatingLegDayCounter = index.dayCounter()

# %%
fixedSchedule = ql.Schedule(
    settlementDate,
    maturity,
    fixedLegTenor,
    calendar,
    fixedLegAdjustment,
    fixedLegAdjustment,
    ql.DateGeneration.Forward,
    False,
)
floatingSchedule = ql.Schedule(
    settlementDate,
    maturity,
    floatingLegTenor,
    calendar,
    floatingLegAdjustment,
    floatingLegAdjustment,
    ql.DateGeneration.Forward,
    False,
)

# %% [markdown]
# We'll build a 5-years swap starting spot...

# %%
spot = ql.VanillaSwap(
    ql.Swap.Payer,
    nominal,
    fixedSchedule,
    fixedRate,
    fixedLegDayCounter,
    floatingSchedule,
    index,
    spread,
    floatingLegDayCounter,
)
spot.setPricingEngine(swapEngine)

# %% [markdown]
# ...and one starting 1 year forward.

# %%
forwardStart = calendar.advance(settlementDate, 1, ql.Years)
forwardEnd = calendar.advance(forwardStart, length, ql.Years)
fixedSchedule = ql.Schedule(
    forwardStart,
    forwardEnd,
    fixedLegTenor,
    calendar,
    fixedLegAdjustment,
    fixedLegAdjustment,
    ql.DateGeneration.Forward,
    False,
)
floatingSchedule = ql.Schedule(
    forwardStart,
    forwardEnd,
    floatingLegTenor,
    calendar,
    floatingLegAdjustment,
    floatingLegAdjustment,
    ql.DateGeneration.Forward,
    False,
)

# %%
forward = ql.VanillaSwap(
    ql.Swap.Payer,
    nominal,
    fixedSchedule,
    fixedRate,
    fixedLegDayCounter,
    floatingSchedule,
    index,
    spread,
    floatingLegDayCounter,
)
forward.setPricingEngine(swapEngine)


# %%
def show(swap):
    
    npv = swap.NPV()
    tape.registerOutput(npv) # register output
    tape.clearDerivatives()  # clear previous derivatives to allow multiple calls
    npv.derivative = 1.0     # seed output adjoint
    tape.computeAdjoints()   # roll back the tape to calculate input adjoints
    
    print("NPV         = {:.2f}".format(npv))
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


# %% [markdown]
# These are the results for the 1-year forward swap, except for the fair rate not matching the spot rate.

# %%
print("---------------- deposit/futures/swap curve, 5-years spot swap")
forecastTermStructure.linkTo(depoFuturesSwapCurve)
show(spot)

# %%
print("\n---------------- deposit/FRA/swap curve, 5-years spot swap")
forecastTermStructure.linkTo(depoFraSwapCurve)
show(spot)

# %%
print("\n---------------- deposit/futures/swap curve, 1-year forward swap")
forecastTermStructure.linkTo(depoFuturesSwapCurve)
show(forward)

# %%
print("\n---------------- deposit/FRA/swap curve, 1-year forward swap")
forecastTermStructure.linkTo(depoFraSwapCurve)
show(forward)

# %%

tape.deactivate()
